/* js/18_cai_dat.js — UX1A-L2b: trang Cài đặt = MỘT câu hỏi, ba thẻ, lưu ngay khi bấm.

   "Học sinh cho biết mình muốn CLB nào nhiều hơn bằng cách nào?"
     Chỉ xếp thứ tự   -> wharton=false, fa_daa=false
     Chia 100 điểm    -> wharton=true,  fa_daa=false   (mặc định)
     Huy chương       -> wharton=true,  fa_daa=true

   Cùng một thành phần (ux1aTaoThe) dùng ở: trang Cài đặt (#ux1aCaiDat), mục ⋯ "Cài đặt…" của màn chọn
   workspace, và bước 3 của trình tạo workspace. Các tính năng SAU khi xếp không còn là cài đặt: chúng là
   hành động ở thẻ "Chi tiết và xuất tệp" (#ux1aSauXep), chỉ hiện khi đang ở chế độ Huy chương.
   Chỉ giao diện: ghi qua update_workspace_config / dat_loai_clb sẵn có. Script thường (không ES module). */
"use strict";

const UX1A_CACH = [
  { ma: "chi_xep", wharton: false, fa: false, id: "ChiXep", tt: "ux1a_the_chi_xep_tt", mt: "ux1a_the_chi_xep_mt" },
  { ma: "chia_100", deXuat: true, wharton: true, fa: false, id: "Chia100", tt: "ux1a_the_chia_100_tt", mt: "ux1a_the_chia_100_mt" },
  { ma: "huy_chuong", wharton: true, fa: true, id: "HuyChuong", tt: "ux1a_the_huy_chuong_tt", mt: "ux1a_the_huy_chuong_mt" },
];
const UX1A_CO_SAU_XEP = ["fa_diem_danh", "fa_khieu_nai", "fa_vong_2", "fa_phan_hoi", "fa_vong_doi_cho"];

function ux1aCachTuLuat(luat) {
  if (luat && luat.fa_daa === true) return "huy_chuong";
  return luat && luat.wharton === false ? "chi_xep" : "chia_100";
}

function ux1aEl(tag, thuocTinh, ...con) {
  const e = document.createElement(tag);
  Object.keys(thuocTinh || {}).forEach((k) => {
    const v = thuocTinh[k];
    if (v === null || v === undefined || v === false) return;
    if (k === "text") e.textContent = v;
    else if (typeof v === "function") e.addEventListener(k.replace(/^on/, ""), v);
    else e.setAttribute(k, v === true ? "" : v);
  });
  con.forEach((c) => { if (c) e.append(c); });
  return e;
}

/* ---- Ba thẻ (dùng chung) -------------------------------------------------------------- */

/* khiChon(ma) được gọi khi bấm một thẻ chưa chọn. Trả về {hop, datCach, khoa, loi, sanSang}.
   MT1: `bo` (mặc định ba thẻ cách xét), `khoaCauHoi`, `moiTheTab` cho phép cùng thành phần vẽ câu hỏi thứ hai (mục tiêu). */
function ux1aTaoThe(tienTo, khiChon, bo, khoaCauHoi, moiTheTab) {
  bo = bo || UX1A_CACH;
  khoaCauHoi = khoaCauHoi || "ux1a_cd_cau_hoi";
  const cauHoi = ux1aEl("h2", { id: tienTo + "CauHoi", class: "ux1a-cau-hoi", "data-i18n": khoaCauHoi,
    text: t(khoaCauHoi) });
  const luoi = ux1aEl("div", { class: "ux1a-the-luoi", id: tienTo + "Luoi", role: "radiogroup",
    "aria-labelledby": tienTo + "CauHoi" });
  const nut = {};
  bo.forEach((c) => {
    const b = ux1aEl("button", { type: "button", role: "radio", class: "ux1a-the", id: tienTo + c.id,
      "data-cach": c.ma, "aria-checked": "false" },
      ux1aEl("span", { class: "ux1a-the-tt", "data-i18n": c.tt, text: t(c.tt) }),
      ux1aEl("span", { class: "ux1a-the-mt", "data-i18n": c.mt, text: t(c.mt) }),
      ...(c.deXuat ? [ux1aEl("span", { class: "ux4-de-xuat", "data-i18n": "ux4_de_xuat", text: t("ux4_de_xuat") })] : []));   /* UX4-L4: nhãn "Đề xuất" duy nhất */
    b.addEventListener("click", () => { if (b.getAttribute("aria-checked") !== "true" && !b.disabled) khiChon(c.ma); });
    nut[c.ma] = b;
    luoi.append(b);
  });
  const loi = ux1aEl("p", { class: "ux1a-loi", role: "alert", id: tienTo + "LoiThe", hidden: true });
  const sanSang = ux1aEl("div", { class: "ux1a-san-sang", id: tienTo + "SanSang", hidden: true });
  /* SF-B7 (ST-A-001): cảnh báo `che_do_thieu_du_lieu` của update_workspace_config, ngay dưới các thẻ chế độ. */
  const canhBao = ux1aEl("div", { class: "canh-bao-vang ux1a-canh-bao", id: tienTo + "CanhBaoDuLieu", role: "status", hidden: true });
  const hop = ux1aEl("div", { class: "ux1a-cai-dat" }, cauHoi, luoi, loi, canhBao, sanSang);
  return {
    hop, sanSang,
    /* `ds` = data.warnings của lần lưu cấu hình vừa xong ([{code, params}]); rỗng / không có = ẩn. */
    datCanhBao(ds) {
      const co = (ds || []).filter((w) => w && w.code === "che_do_thieu_du_lieu");
      canhBao.textContent = co.length ? trErrs(co).join(" ") : "";
      canhBao.hidden = !co.length;
    },
    datCach(ma) {
      const coThe = bo.some((c) => c.ma === ma);
      bo.forEach((c, i) => {
        const chon = c.ma === ma;
        nut[c.ma].setAttribute("aria-checked", chon ? "true" : "false");
        nut[c.ma].classList.toggle("is-chon", chon);
        /* Mặc định chỉ thẻ đang chọn nhận Tab; `moiTheTab` (MT1): Tab tới MỌI thẻ, Enter chọn. Không thẻ nào chọn: vẫn Tab vào được. */
        nut[c.ma].tabIndex = moiTheTab || chon || (!coThe && i === 0) ? 0 : -1;
      });
    },
    khoa(ma, dongKhoa) { nut[ma].disabled = !!dongKhoa; },
    loi(chu) { loi.textContent = chu || ""; loi.hidden = !chu; },
  };
}

/* ---- Sửa tại chỗ: Huy chương cần dữ liệu CLB sẵn sàng ------------------------------------ */

function ux1aVeSanSang(hop, d, taiLai, quayLai, tuyChon) {
  /* MT2: `tuyChon.giuBang` = vẽ bảng đặt loại cả khi đã sẵn sàng (công tắc "Chia CLB theo loại" cần sửa loại bất cứ lúc nào);
     `tuyChon.khoaConThieu` = câu đầu khi còn thiếu (không nhắc Huy chương); `tuyChon.khoaGt` {loại: khoá chữ} đổi chữ mục đích
     của từng loại (MT2: Giới hạn không có huy chương). Không truyền: đúng như cũ. */
  tuyChon = tuyChon || {};
  hop.textContent = "";
  hop.hidden = false;
  if (d.san_sang) {
    hop.append(ux1aEl("p", { class: "ux1a-san-sang-xong", id: "ux1aSanSangXong", text: t("ux1a_ss_san_sang") }));
    if (!tuyChon.giuBang) return;
  } else {
    hop.append(ux1aEl("p", { class: "ux1a-ss-dau", text: t(tuyChon.khoaConThieu || "ux1a_ss_con_thieu") }));
  }
  /* Dữ liệu huy chương đã nạp không phải huy chương (vd. điểm quyết tâm của sổ cũ) hoặc đặt ở CLB Tự do: nói MỘT dòng,
     không tự đổi dữ liệu; cách sửa là nạp lại sổ có cột Huy chương. UX1B-L5c: kèm hai nút làm việc đó (tải sổ mẫu,
     quay lại Chia 100 điểm) và ẩn các nút loại CLB cho tới khi dữ liệu học sinh hợp lệ (đặt loại xong vẫn không chạy được). */
  if (d.huy_chuong_sai > 0) {
    const ca = d.huy_chuong_ca_so === true;      /* ngưỡng "cả sổ" do backend giữ (cùng nguồn với cảnh báo sức khoẻ) */
    hop.append(ux1aEl("p", { class: "ux1a-ss-hc-sai", id: "ux1aSsHuyChuongSai",
      text: ca ? t("ux1b_ss_nap_lai_ca_so", { n: d.huy_chuong_sai, tong: d.n_hoc_sinh })
               : t("ux1a_ss_huy_chuong_sai", { n: d.huy_chuong_sai, vd: d.huy_chuong_sai_vd }) }));
    const hang = ux1aEl("div", { class: "ux1b-ss-nut" });
    if (typeof taiSoNhapMau === "function") {
      hang.append(ux1aEl("button", { type: "button", class: "btn btn-secondary", id: "ux1bSsTaiSoMau",
        text: t("ux1a_btn_so_mau_huy_chuong"), onclick: () => taiSoNhapMau("huy_chuong") }));
    }
    if (quayLai) {
      hang.append(ux1aEl("button", { type: "button", class: "btn btn-primary", id: "ux1bSsQuayLai",
        text: t("ux1b_ss_quay_lai"), onclick: quayLai }));
    }
    hop.append(hang);
    if (ca) return;      /* ít em sai (dưới một nửa): vẫn cho đặt loại CLB tại chỗ bên dưới */
  }
  /* MT1 (gom): BẢNG đặt loại — mỗi CLB một dòng, ba nút loại có trạng thái chọn, điểm sàn của Tuyển chọn ngay tại dòng,
     nhóm theo buổi kèm dấu "đã có / cần CLB Tự do", bộ đếm. Vẫn lưu qua `dat_loai_clb`; không thêm đường lưu mới.
     Sau mỗi lần lưu vẽ lại cả khối từ dữ liệu đã lưu, rồi trả tiêu điểm về đúng ô vừa bấm (`hoiPhuc`). */
  const luu = (cid, loai, diemSan, hoiPhuc) => callApi("dat_loai_clb", cid, loai, diemSan).then((r) => {
    if (!r.ok) { showErrorToast(r.errors); return; }
    const xong = taiLai();
    /* MT1: loại / điểm sàn vừa đổi thì bảng CLB (cột "Loại", "Điểm sàn") và thanh "Việc tiếp theo" phải đổi theo ngay,
       không đợi tải lại trang. Chỉ gọi lại hàm vẽ sẵn có; không thêm đường lưu mới. */
    if (typeof loadAdminClubs === "function") loadAdminClubs();
    if (typeof capNhatViecTiepTheo === "function") capNhatViecTiepTheo();
    return Promise.resolve(xong).then(() => {
      const o = hoiPhuc && hop.querySelector(hoiPhuc);
      if (o) o.focus();
    });
  });
  const nhieuBuoi = new Set(d.clubs.map((c) => c.buoi)).size > 1;
  const daDat = d.clubs.filter((c) => c.loai !== null && c.loai !== undefined).length;
  hop.append(ux1aEl("p", { class: "ux1a-ss-dem", id: "ux1aSsDem", role: "status",
    text: t("ux1a_ss_dem", { x: daDat, y: d.clubs.length }) }));
  /* Mục đích từng loại: chữ "i" nhỏ, đưa chuột vào (hoặc focus bằng bàn phím / chạm) thì hiện; chữ luôn nằm trong DOM
     (aria-label + tooltip) nên trình đọc màn hình đọc được. */
  hop.append(ux1aEl("p", { class: "hint-text ux1a-ss-giai-thich", id: "ux1aSsGiaiThich" },
    ux1aEl("span", { class: "ux1a-ss-gt-nhan", text: t("ux1a_ss_cac_loai") }),
    ...["TU_DO", "GIOI_HAN", "TUYEN_CHON"].map((ma) => {
      const idTip = "ux1aSsTip_" + ma;
      const chu = t((tuyChon.khoaGt && tuyChon.khoaGt[ma]) || "ux1a_ss_gt_" + ma);
      return ux1aEl("span", { class: "ux1a-ss-gt" },
        ux1aEl("span", { class: "ux1a-ss-gt-ten", text: t("fa_loai_" + ma) }),
        ux1aEl("button", { type: "button", class: "ux1a-i", "data-loai": ma, text: "i",
          "aria-label": chu, "aria-describedby": idTip }),
        ux1aEl("span", { class: "ux1a-i-tip", id: idTip, role: "tooltip", text: chu }));
    })));

  const bang = ux1aEl("table", { class: "data-table ux1a-ss-bang" });
  bang.append(ux1aEl("thead", null, ux1aEl("tr", null,
    ux1aEl("th", { scope: "col", text: t("gt_th_clb") }),
    ux1aEl("th", { scope: "col", text: t("th_fa_loai") }),
    ux1aEl("th", { scope: "col", text: t("th_fa_diem_san") }))));
  const than = ux1aEl("tbody");
  let buoiTruoc = null;
  d.clubs.forEach((c) => {
    if (c.buoi !== buoiTruoc) {
      buoiTruoc = c.buoi;
      const co = !d.buoi_thieu_tu_do.includes(c.buoi);
      than.append(ux1aEl("tr", { class: "ux1a-ss-buoi", "data-buoi": c.buoi, "data-co-tu-do": co ? "true" : "false" },
        ux1aEl("td", { colspan: "3" },
          nhieuBuoi ? ux1aEl("strong", { class: "ux1a-ss-buoi-ten", text: nhanBuoi(c.buoi) + " " }) : null,
          ux1aEl("span", { class: "ux1a-ss-buoi-tt" + (co ? " is-xong" : " is-thieu"),
            text: t(co ? "ux1a_ss_buoi_co_tu_do" : "ux1a_ss_buoi_can_tu_do") }))));
    }
    const vien = ux1aEl("span", { class: "ux1a-vien-nhom", role: "group", "aria-label": c.name });
    ["TU_DO", "GIOI_HAN", "TUYEN_CHON"].forEach((ma) => {
      const b = ux1aEl("button", { type: "button", class: "ux1a-vien", "data-loai": ma, "data-clb": c.club_id,
        "aria-pressed": c.loai === ma ? "true" : "false", text: t("fa_loai_" + ma) });
      b.addEventListener("click", () => {
        if (c.loai === ma) return;
        luu(c.club_id, ma, null, 'tr[data-clb="' + c.club_id + '"] button[data-loai="' + ma + '"]');
      });
      vien.append(b);
    });
    let sanO = "—";
    if (c.loai === "TUYEN_CHON") {
      const o = ux1aEl("input", { type: "number", class: "text-input ux1a-so", min: "0", max: "10", step: "1",
        value: c.diem_san === null || c.diem_san === undefined ? "" : String(c.diem_san),
        "aria-label": t("ux1a_ss_diem_san", { clb: c.name }) });
      const gui = () => {
        if (o.value === "") { o.focus(); return; }
        luu(c.club_id, "TUYEN_CHON", Number(o.value), 'tr[data-clb="' + c.club_id + '"] input[type=number]');
      };
      o.addEventListener("keydown", (ev) => { if (ev.key === "Enter") gui(); });
      sanO = ux1aEl("span", { class: "ux1a-ss-san" + (c.diem_san === null || c.diem_san === undefined ? " is-thieu" : "") },
        o, ux1aEl("button", { type: "button", class: "btn btn-secondary btn-nho", "data-luu-san": c.club_id,
          text: t("ws_btn_luu"), onclick: gui }));
    }
    than.append(ux1aEl("tr", { class: "ux1a-ss-dong", "data-clb": c.club_id, "data-buoi": c.buoi },
      ux1aEl("td", { class: "ux1a-ss-ten", text: c.name }),
      ux1aEl("td", null, vien),
      ux1aEl("td", null, sanO)));
  });
  bang.append(than);
  hop.append(bang);
}

/* MT2: công tắc "Chia CLB theo loại" ở thẻ Quản lý › Câu lạc bộ. Lưu qua update_workspace_config (chỉ khoá chia_loai);
   bảng đặt loại dùng lại ux1aVeSanSang + dat_loai_clb. Tắt: ẩn bảng, loại đã đặt vẫn nằm trong CSDL. */
let mt2DangLuu = false;

function mt2VeChiaLoai() {
  const khung = el("mt2ChiaLoai"), cb = el("mt2CongTac"), bang = el("mt2Bang");
  if (!khung || !cb) return Promise.resolve();
  return callApi("get_chia_loai").then((r) => {
    if (!r.ok) { khung.hidden = true; return; }
    khung.hidden = false;
    const d = r.data;
    cb.checked = d.hieu_luc === true;
    cb.disabled = d.fa_daa === true || mt2DangLuu;
    el("mt2GhiChu").textContent = t(d.fa_daa ? "mt2_do_huy_chuong" : "mt2_ghi_chu");
    /* Huy chương: bảng đặt loại đã nằm ở Cài đặt (#ux1aSanSang) — không vẽ hai bảng trùng id. */
    if (!d.hieu_luc || d.fa_daa) { bang.hidden = true; bang.textContent = ""; return; }
    return callApi("get_san_sang_loai").then((s) => {
      if (!s.ok) { bang.hidden = true; return; }
      ux1aVeSanSang(bang, s.data, mt2VeChiaLoai, null, { giuBang: true, khoaConThieu: "mt2_con_thieu", khoaGt: { GIOI_HAN: "mt2_gt_GIOI_HAN" } });
    });
  });
}

function mt2KhoiTaoChiaLoai() {
  const cb = el("mt2CongTac");
  if (!cb || cb.dataset.daNoi) return;
  cb.dataset.daNoi = "1";
  cb.addEventListener("change", () => {
    if (mt2DangLuu) return;
    mt2DangLuu = true;
    cb.disabled = true;      /* chặn bấm đúp */
    callApi("update_workspace_config", { rules: { chia_loai: cb.checked } }).then((r) => {
      if (!r.ok) showErrorToast(r.errors);
      mt2DangLuu = false;
      /* Vẽ lại từ cấu hình ĐÃ LƯU (lỗi thì công tắc trở về trạng thái thật), rồi cập nhật bảng CLB và thanh việc tiếp theo. */
      mt2VeChiaLoai();
      if (typeof loadAdminClubs === "function") loadAdminClubs();
      if (typeof capNhatViecTiepTheo === "function") capNhatViecTiepTheo();
      if (typeof loadHealthReport === "function") loadHealthReport();
    });
  });
}

function ux1aKiemSanSang(the, quayLai) {
  const lam = () => callApi("get_san_sang_huy_chuong").then((r) => {
    if (!r.ok) { the.sanSang.hidden = true; return; }
    ux1aVeSanSang(the.sanSang, r.data, lam, quayLai);
  });
  return lam();
}

/* ---- Trang Cài đặt (đang mở một workspace) ------------------------------------------------- */

function ux1aTenCach(ma) { return t(UX1A_CACH.find((c) => c.ma === ma).tt); }

function ux1aMoNangCao() {
  switchTab("admin");
  /* UX4-L2: tiêu chí xếp nằm trong tab "Cách xếp" (không còn mục gập "Nâng cao"). */
  if (typeof datTabConQl === "function") datTabConQl("cach_xep", { luu: true });
  const d = el("ux1aNangCao");
  if (d) d.open = true;                       /* UX4-L4: "Tuỳ chỉnh thêm" là mục gập; mở ra để thấy tiêu chí */
  const p = el("gt2TieuChiPanel");
  if (p) p.scrollIntoView({ block: "start" });
}

function ux1aApDungSong(cfg) {
  if (typeof wsApDungCauHinh === "function") wsApDungCauHinh(cfg);
  if (typeof TAB_LOADERS !== "undefined" && TAB_LOADERS.others) TAB_LOADERS.others();
  if (typeof capNhatViecTiepTheo === "function") capNhatViecTiepTheo();
  if (typeof ux1aVeSauXep === "function") ux1aVeSauXep();
  /* ST-B-002: công tắc "Chia CLB theo loại" (Quản lý › CLB) phụ thuộc chế độ vừa đổi; vẽ lại từ cấu hình đã lưu. */
  if (typeof mt2VeChiaLoai === "function") mt2VeChiaLoai();
}

/* Vẽ trang Cài đặt vào `host` cho workspace `slug`. */
function ux1aVeCaiDatSong(host, slug, tienTo) {
  let luat = {};
  const dangMo = () => wsTrangThai && wsTrangThai.enabled && wsTrangThai.slug === slug;
  const the = ux1aTaoThe(tienTo, (ma) => doi(ma));
  /* MT1: một thẻ mục tiêu có thể đổi cách xét (vd. "Cơ hội như nhau" tắt điểm chia, rời thẻ thì bật lại): câu hỏi đầu
     phải vẽ lại từ cấu hình ĐÃ LƯU sau mỗi lần chọn / hoàn tác / "Về mục tiêu mẫu". */
  const veLaiCauDau = () => callApi("get_workspace_config", slug).then((res) => {
    if (!res.ok) return;
    const cfg = res.data.config || {};
    luat = cfg.rules || {};
    the.datCach(ux1aCachTuLuat(luat));
    the.sanSang.hidden = true;
    if (ux1aCachTuLuat(luat) === "huy_chuong" && dangMo()) ux1aKiemSanSang(the, () => doi("chia_100"));
    if (dangMo()) ux1aApDungSong(cfg);
  });
  const mt = typeof mt1TaoCauHoi === "function" && dangMo() ? mt1TaoCauHoi(tienTo, veLaiCauDau) : null;
  host.textContent = "";
  host.append(the.hop);
  if (mt) host.append(mt.hop);

  const ve = () => {
    the.datCach(ux1aCachTuLuat(luat));
    the.sanSang.hidden = true;
    if (ux1aCachTuLuat(luat) === "huy_chuong" && dangMo()) ux1aKiemSanSang(the, () => doi("chia_100"));
    if (mt) mt.lamMoi();
  };
  const dat = (rules) => callApi("update_workspace_config", { rules }, slug);
  const luatCu = () => {
    const r = { wharton: luat.wharton !== false, fa_daa: luat.fa_daa === true };
    UX1A_CO_SAU_XEP.forEach((k) => { if (luat[k] === true) r[k] = true; });
    if (Number.isInteger(luat.fa_khieu_nai_so_ngay)) r.fa_khieu_nai_so_ngay = luat.fa_khieu_nai_so_ngay;
    return r;
  };
  const khiXong = (cfg) => { luat = cfg.rules || {}; ve(); if (dangMo()) ux1aApDungSong(cfg); };

  function doi(ma) {
    const c = UX1A_CACH.find((x) => x.ma === ma);
    const truoc = luatCu();
    const rules = { wharton: c.wharton, fa_daa: c.fa };
    if (!c.fa) UX1A_CO_SAU_XEP.forEach((k) => { if (luat[k] === true) rules[k] = false; });
    the.loi("");
    the.datCanhBao(null);       /* đổi chế độ thì làm mới: cảnh báo cũ không còn đúng */
    return dat(rules).then((r) => {
      if (!r.ok) { the.loi(trErrs(r.errors).join(" ")); return; }
      khiXong(r.data.config);
      the.datCanhBao(r.data.warnings);      /* SF-B7: sau khiXong (nó vẽ lại thẻ) để cảnh báo của lần đổi này còn lại */
      callApi("get_last_run_info").then((lr) => {
        const daChay = lr.ok && lr.data;
        const chu = t("ux1a_cd_da_chuyen", { cach: ux1aTenCach(ma) }) +
          (daChay ? "\n" + t("ux1a_cd_giu_ket_qua") : "");
        const toast = showToast(chu, "success", { sticky: true, hanhDong: { nhan: t("ux1a_cd_hoan_tac"), khiBam: () => {
          toast.goBo();
          /* Hoàn tác = cùng một lời gọi với giá trị cũ; cờ sau khi xếp đã tắt thì bật lại cùng lúc. */
          const ve0 = Object.assign({ fa_daa: false }, truoc);
          UX1A_CO_SAU_XEP.forEach((k) => { if (!(k in ve0)) ve0[k] = false; });
          dat(ve0).then((r2) => {
            if (!r2.ok) { the.loi(trErrs(r2.errors).join(" ")); return; }
            khiXong(r2.data.config);
            the.datCanhBao(r2.data.warnings);
          });
        } } });
        setTimeout(() => toast.goBo(), 10000);
      });
    });
  }

  return callApi("get_workspace_config", slug).then((res) => {
    if (!res.ok) { showErrorToast(res.errors); return; }
    luat = (res.data.config || {}).rules || {};
    ve();
  });
}

/* Trang Cài đặt trong nhóm "Cài đặt" (view Quản lý). Chỉ có nghĩa khi có workspace. */
function ux1aTaiCaiDat() {
  const panel = el("ux1aCaiDat");
  if (!panel) return;
  if (!wsTrangThai || !wsTrangThai.enabled) { panel.hidden = true; return; }
  panel.hidden = false;
  el("ux1aCaiDatTen").textContent = t("ux1a_cd_tieu_de", { ten: wsTrangThai.name || wsTrangThai.slug || "" });
  return ux1aVeCaiDatSong(el("ux1aCaiDatThan"), wsTrangThai.slug, "ux1a");
}

/* Mục ⋯ "Cài đặt…" ở màn chọn workspace: cùng thành phần, trong một hộp thoại. */
function ux1aMoCaiDatWs(w) {
  const dong = () => {
    lop.remove();
    wsHienOverlay(true);
    const tom = document.querySelector('#wsBang tr[data-slug="' + w.slug + '"] .menu-khac > summary');
    const dich = tom || el("wsTieuDe");
    if (dich) dich.focus();
  };
  const than = ux1aEl("div", { id: "ux1aWsThan" });
  const xong = ux1aEl("button", { type: "button", class: "btn btn-primary", id: "ux1aWsXong", text: t("ux1a_cd_xong"),
    onclick: dong });
  const lop = ux1aEl("div", { class: "ws-overlay", role: "dialog", "aria-modal": "true", "aria-labelledby": "ux1aWsTieuDe" },
    ux1aEl("div", { class: "ws-hop" },
      ux1aEl("h2", { id: "ux1aWsTieuDe", class: "ws-tieu-de", text: t("ux1a_cd_tieu_de", { ten: w.name }) }),
      than,
      ux1aEl("div", { class: "ws-chan" }, xong)));
  lop.addEventListener("keydown", (ev) => { if (ev.key === "Escape") dong(); });
  wsHienOverlay(false);
  document.body.append(lop);
  xong.focus();
  return ux1aVeCaiDatSong(than, w.slug, "ux1aWs");
}

/* ---- Tính năng sau khi xếp: hành động ở thẻ "Chi tiết và xuất tệp" ---------------------------- */

const UX1A_SAU_XEP = [
  { co: "fa_vong_2", nut: "ux1a_sx_vong_2", he_qua: "ux1b_sx_he_vong_2", bang: ["vong2Panel"] },
  { co: "fa_khieu_nai", nut: "ux1a_sx_khieu_nai", he_qua: "ux1b_sx_he_khieu_nai", bang: ["khieuNaiPanel"], ngay: true },
  { co: "fa_diem_danh", nut: "ux1a_sx_diem_danh", he_qua: "ux1b_sx_he_diem_danh", bang: ["diemDanhPanel"] },
  { co: "fa_vong_doi_cho", nut: "ux1a_sx_doi_cho", he_qua: "ux1b_sx_he_doi_cho", bang: ["moiPanel", "vong2Panel"] },
  { co: "fa_phan_hoi", nut: "ux1a_sx_phan_hoi", he_qua: "ux1b_sx_he_phan_hoi", bang: ["phanHoiTongPanel", "phanHoiPanel"] },
];

function ux1aVeSauXep() {
  const hop = el("ux1aSauXep");
  if (!hop) return Promise.resolve();
  return Promise.all([callApi("get_workspace_config"), callApi("get_em_chua_co_cho"), callApi("get_club_fill_stats")]).then(([cfg, cho, lap]) => {
    const luat = cfg.ok ? ((cfg.data.config || {}).rules || {}) : {};
    /* Chỉ ở chế độ Huy chương (backend: fa_tinh_nang_can_fa). Chế độ khác: không hiện gì. */
    hop.hidden = !(cfg.ok && luat.fa_daa === true);
    if (hop.hidden) return;
    const so = cho.ok ? cho.data.so_em : 0;
    /* Chỗ trống còn lại (không tính CLB Tự do: không giới hạn chỗ), cùng cách tính với thẻ "Chỗ trống". */
    const trong = lap.ok ? lap.data.reduce((a, c) => a + (c.tu_do ? 0 : Math.max(0, (c.capacity || 0) - (c.matched || 0))), 0) : 0;
    const luoi = el("ux1aSauXepLuoi");
    /* Không vẽ lại khi chưa có gì đổi: giữ nguyên ô đang gõ dở và vị trí con trỏ (nhiều nơi cùng gọi hàm này). */
    const dau = JSON.stringify([UX1A_SAU_XEP.map((m) => luat[m.co] === true), luat.fa_khieu_nai_so_ngay, so, trong, window.I18N.getLang()]);
    if (luoi.dataset.dau === dau && luoi.children.length) return;
    luoi.dataset.dau = dau;
    /* Vẽ lại (sau một hành động khác) không được xoá số ngày người dùng đang gõ dở. */
    const ngayDangGo = el("ux1aSxNgay") ? el("ux1aSxNgay").value : null;
    luoi.textContent = "";
    UX1A_SAU_XEP.forEach((m) => {
      const bat = luat[m.co] === true;
      /* "Vào lúc có nghĩa": mở vòng 2 khi còn người chưa có chỗ, mời danh sách chờ khi còn chỗ trống. Đang bật thì vẫn
         hiện để tắt được. */
      if (!bat && m.co === "fa_vong_2" && so <= 0) return;
      if (!bat && m.co === "fa_vong_doi_cho" && trong <= 0) return;
      const dong = ux1aEl("div", { class: "ux1a-sx-dong", "data-co": m.co });
      const hang = ux1aEl("div", { class: "ux1b-sx-hang" });
      let nhan = m.co === "fa_vong_2" ? t(m.nut, { n: so }) : t(m.nut);
      /* UX1B-L5c: đang bật thì nút nói trọn câu (kèm số ngày), không còn "…: Nhận khiếu nại trong" cụt. */
      if (m.ngay && bat) nhan = t("ux1b_sx_khieu_nai_ngay", { n: Number.isInteger(luat.fa_khieu_nai_so_ngay) ? luat.fa_khieu_nai_so_ngay : 3 });
      let oNgay = null;
      if (m.ngay && !bat) {
        oNgay = ux1aEl("input", { type: "number", class: "text-input ux1a-so", min: "1", max: "14", step: "1",
          value: bat || ngayDangGo === null ? String(Number.isInteger(luat.fa_khieu_nai_so_ngay) ? luat.fa_khieu_nai_so_ngay : 3)
            : ngayDangGo,
          id: "ux1aSxNgay", "aria-label": t("ws_tn_so_ngay") });
      }
      const b = ux1aEl("button", { type: "button", class: "btn " + (bat ? "btn-ghost" : "btn-secondary"),
        id: "ux1aSx_" + m.co, "aria-pressed": bat ? "true" : "false", text: bat ? t("ux1a_sx_tat", { nhan }) : nhan });
      b.addEventListener("click", () => {
        const rules = { [m.co]: !bat };
        if (m.ngay && !bat) {
          const n = Number(oNgay.value);
          if (!Number.isInteger(n) || n < 1 || n > 14) { showToast(t("ux1a_sx_ngay_sai"), "error"); return; }
          rules.fa_khieu_nai_so_ngay = n;
        }
        callApi("update_workspace_config", { rules }).then((r) => {
          if (!r.ok) { showErrorToast(r.errors); return; }
          ux1aApDungSong(r.data.config);
          /* Mở bảng sẵn có của tính năng vừa bật (nạp xong thẻ rồi mới cuộn tới). */
          if (!bat) {
            let lan = 0;
            const tim = () => {
              const p = m.bang.map(el).find((x) => x && !x.hidden);
              if (p) { p.scrollIntoView({ behavior: "smooth", block: "start" }); return; }
              if (++lan < 20) setTimeout(tim, 150);
            };
            tim();
          }
        });
      });
      hang.append(b);
      if (oNgay) hang.append(oNgay, ux1aEl("span", { class: "ux1b-sx-ngay", text: t("ux1a_sx_ngay") }));
      dong.append(hang, ux1aEl("p", { class: "hint-text ux1b-sx-he-qua", text: t(m.he_qua) }));   /* UX1B-L5c: hệ quả */
      luoi.append(dong);
    });
  });
}

function initCaiDat() {
  window.addEventListener("langchange", () => { ux1aTaiCaiDat(); ux1aVeSauXep(); });
  ux1aVeSauXep();
}
