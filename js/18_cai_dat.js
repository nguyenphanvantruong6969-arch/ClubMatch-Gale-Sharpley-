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
  { ma: "chia_100", wharton: true, fa: false, id: "Chia100", tt: "ux1a_the_chia_100_tt", mt: "ux1a_the_chia_100_mt" },
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
      ux1aEl("span", { class: "ux1a-the-mt", "data-i18n": c.mt, text: t(c.mt) }));
    b.addEventListener("click", () => { if (b.getAttribute("aria-checked") !== "true" && !b.disabled) khiChon(c.ma); });
    nut[c.ma] = b;
    luoi.append(b);
  });
  const loi = ux1aEl("p", { class: "ux1a-loi", role: "alert", id: tienTo + "LoiThe", hidden: true });
  const sanSang = ux1aEl("div", { class: "ux1a-san-sang", id: tienTo + "SanSang", hidden: true });
  const hop = ux1aEl("div", { class: "ux1a-cai-dat" }, cauHoi, luoi, loi, sanSang);
  return {
    hop, sanSang,
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

function ux1aVeSanSang(hop, d, taiLai, quayLai) {
  hop.textContent = "";
  hop.hidden = false;
  if (d.san_sang) {
    hop.append(ux1aEl("p", { class: "ux1a-san-sang-xong", id: "ux1aSanSangXong", text: t("ux1a_ss_san_sang") }));
    return;
  }
  hop.append(ux1aEl("p", { class: "ux1a-ss-dau", text: t("ux1a_ss_con_thieu") }));
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
  const luu = (cid, loai, diemSan) => callApi("dat_loai_clb", cid, loai, diemSan).then((r) => {
    if (!r.ok) { showErrorToast(r.errors); return; }
    taiLai();
  });
  const nhieuBuoi = new Set(d.clubs.map((c) => c.buoi)).size > 1;
  const tenClb = {};
  d.clubs.forEach((c) => { tenClb[c.club_id] = c.name || c.club_id; });

  d.clubs.filter((c) => c.loai === null).forEach((c) => {
    const vien = ux1aEl("span", { class: "ux1a-vien-nhom", role: "group", "aria-label": c.name });
    [["TU_DO", "fa_loai_TU_DO"], ["GIOI_HAN", "fa_loai_GIOI_HAN"], ["TUYEN_CHON", "fa_loai_TUYEN_CHON"]].forEach(([ma, khoa]) => {
      const b = ux1aEl("button", { type: "button", class: "ux1a-vien", "data-loai": ma, "data-clb": c.club_id,
        "aria-pressed": "false", text: t(khoa) });
      b.addEventListener("click", () => luu(c.club_id, ma, null));
      vien.append(b);
    });
    hop.append(ux1aEl("div", { class: "ux1a-ss-dong", "data-clb": c.club_id },
      ux1aEl("span", { class: "ux1a-ss-ten", text: c.name + (nhieuBuoi ? " · " + nhanBuoi(c.buoi) : "") }),
      vien));
  });

  d.thieu_diem_san.forEach((cid) => {
    const o = ux1aEl("input", { type: "number", class: "text-input ux1a-so", min: "0", max: "10", step: "1",
      "aria-label": t("ux1a_ss_diem_san", { clb: tenClb[cid] }) });
    const b = ux1aEl("button", { type: "button", class: "btn btn-secondary btn-nho", text: t("ws_btn_luu") });
    b.addEventListener("click", () => {
      if (o.value === "") return;
      luu(cid, "TUYEN_CHON", Number(o.value));
    });
    hop.append(ux1aEl("div", { class: "ux1a-ss-dong", "data-diem-san": cid },
      ux1aEl("span", { class: "ux1a-ss-ten", text: t("ux1a_ss_diem_san", { clb: tenClb[cid] }) }), o, b));
  });

  d.buoi_thieu_tu_do.forEach((buoi) => {
    const ds = d.clubs.filter((c) => c.buoi === buoi);
    const sel = ux1aEl("select", { class: "text-input ux1a-chon-tu-do", "data-buoi": buoi,
      "aria-label": t("ux1a_ss_chon_tu_do", { buoi: nhanBuoi(buoi) }) },
      ux1aEl("option", { value: "", text: "—" }),
      ...ds.map((c) => ux1aEl("option", { value: c.club_id, text: c.name })));
    sel.addEventListener("change", () => { if (sel.value) luu(sel.value, "TU_DO", null); });
    hop.append(ux1aEl("div", { class: "ux1a-ss-dong", "data-buoi": buoi },
      ux1aEl("span", { class: "ux1a-ss-ten", text: t("ux1a_ss_thieu_tu_do", { buoi: nhanBuoi(buoi) }) }), sel));
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
  const d = el("ux1aNangCao");
  if (d) {
    d.open = true;
    el("gt2TieuChiPanel").scrollIntoView({ block: "start" });
  }
}

function ux1aApDungSong(cfg) {
  if (typeof wsApDungCauHinh === "function") wsApDungCauHinh(cfg);
  if (typeof TAB_LOADERS !== "undefined" && TAB_LOADERS.others) TAB_LOADERS.others();
  if (typeof capNhatViecTiepTheo === "function") capNhatViecTiepTheo();
  if (typeof ux1aVeSauXep === "function") ux1aVeSauXep();
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
    return dat(rules).then((r) => {
      if (!r.ok) { the.loi(trErrs(r.errors).join(" ")); return; }
      khiXong(r.data.config);
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
