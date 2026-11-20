/* js/19_muc_tieu.js — MT1-L4: câu hỏi thứ hai ở Cài đặt, "Khi một CLB đông người, trường ưu tiên điều gì?",
   ba thẻ (cùng thành phần `ux1aTaoThe` của câu hỏi đầu), và dòng kết quả ở thẻ "Chi tiết và xuất tệp".

     Theo năng lực    nang_luc   Cơ hội như nhau  co_hoi    Dành chỗ cho một nhóm  danh_cho

   Bấm thẻ = lưu ngay (backend `chon_muc_tieu`, một giao dịch) + thông báo có "Hoàn tác" (10 giây). Một nhóm duy nhất
   thì tự chọn (1 lần bấm); nhiều nhóm thì hiện các nút nhóm ngay dưới thẻ (2 lần bấm). Dòng tác động dưới thẻ
   lấy từ `uoc_tinh_muc_tieu` (chỉ đọc). Chỉ giao diện: không có đường lưu mới. Script thường (không ES module). */
"use strict";

const MT1_THE = [
  { ma: "nang_luc", id: "NangLuc", tt: "mt1_the_nang_luc_tt", mt: "mt1_the_nang_luc_mt" },
  { ma: "co_hoi", id: "CoHoi", tt: "mt1_the_co_hoi_tt", mt: "mt1_the_co_hoi_mt" },
  { ma: "danh_cho", id: "DanhCho", tt: "mt1_the_danh_cho_tt", mt: "mt1_the_danh_cho_mt" },
];

/* Nhãn nhóm đọc được: "khoi_10" -> "khối 10". Chỉ để HIỂN THỊ (mã nhóm gốc vẫn gửi cho backend). */
const MT1_TU_NHOM = { khoi: "khối", chinh: "chính", sach: "sách", ngheo: "nghèo", ho: "hộ", can: "cận",
  kho: "khó", khan: "khăn", hoan: "hoàn", canh: "cảnh", dan: "dân", toc: "tộc", thieu: "thiểu", so: "số",
  nu: "nữ", lop: "lớp" };
function mt1NhanNhom(ma) {
  return String(ma || "").split(/[_\s]+/).filter(Boolean).map((w) => MT1_TU_NHOM[w.toLowerCase()] || w).join(" ");
}

/* Thông báo "Đã chuyển sang…" mới nhất: lần chọn kế tiếp đóng nó, để Hoàn tác luôn là của lần MỚI NHẤT. */
let mt1ToastCu = null;

function mt1TenThe(ma) { return t(MT1_THE.find((x) => x.ma === ma).tt); }
function mt1So(x) { return x && x.duoi_5 ? t("mt1_duoi_5") : String(x ? x.n : 0); }
function mt1Ngoai() { return document.body.dataset.vai === "giao_vien"; }
function mt1Dong(cls, chu, id) { return ux1aEl("p", { class: cls, id, text: chu }); }

/* ---- Câu hỏi trong trang Cài đặt ------------------------------------------------------------- */

function mt1TaoCauHoi(tienTo) {
  const tt = tienTo + "Mt";
  let d = null;            /* get_muc_tieu */
  let choNhom = false;     /* đã bấm "Dành chỗ", chờ bấm nhóm (nhiều nhóm) */
  let ghiChu = [];         /* ghi chú của lần chọn vừa rồi (vd. điểm chia không được dùng) */
  let lan = 0;
  const the = ux1aTaoThe(tt, (ma) => chon(ma, null), MT1_THE, "mt1_cau_hoi", true);
  const lyDo = ux1aEl("p", { class: "mt1-dong", id: tt + "LyDo", hidden: true });
  const nhom = ux1aEl("div", { class: "mt1-nhom", id: tt + "Nhom", role: "group", hidden: true,
    "aria-label": t("mt1_chon_nhom") });
  const hieuQua = ux1aEl("p", { class: "mt1-dong", id: tt + "HieuQua", hidden: true });
  const thayDoi = ux1aEl("button", { type: "button", class: "btn btn-ghost btn-nho mt1-nut", id: tienTo + "ThayDoi",
    "data-i18n": "ux1a_cd_thay_doi", text: t("ux1a_cd_thay_doi"), onclick: ux1aMoNangCao });
  const dong = ux1aEl("div", { class: "mt1-hang" }, hieuQua, thayDoi);
  const canhBao = ux1aEl("div", { id: tt + "CanhBao" });
  const chiTiet = ux1aEl("details", { class: "mt1-chi-tiet", id: tt + "ChiTiet", hidden: true });
  const rieng = ux1aEl("p", { class: "mt1-dong mt1-rieng", id: tt + "Rieng", hidden: true });
  const hop = ux1aEl("div", { class: "ux1a-cai-dat mt1-hop", id: tt + "Block" },
    the.hop, lyDo, nhom, dong, canhBao, chiTiet, rieng);

  function chon(ma, nhomChon) {
    const lyThe = d && d.cac_the.find((x) => x.id === ma);
    if (lyThe && lyThe.khoa) return;
    if (ma === "danh_cho" && !nhomChon) {
      const co = d ? d.nhom : [];
      if (co.length > 1) { choNhom = true; ve(); return; }       /* nhiều nhóm: bấm thẻ chỉ mở các nút nhóm */
      nhomChon = co.length ? co[0].nhan : null;                  /* một nhóm: tự chọn */
    }
    choNhom = false;
    the.loi("");
    callApi("chon_muc_tieu", ma, nhomChon).then((r) => {
      if (!r.ok) { the.loi(trErrs(r.errors).join(" ")); return; }
      ghiChu = (r.data.canh_bao || []).slice();
      const hoanTac = r.data.hoan_tac;
      if (mt1ToastCu) { mt1ToastCu.goBo(); mt1ToastCu = null; }
      const them = ghiChu.length ? "\n" + trErrs(ghiChu).join(" ") : "";
      callApi("get_last_run_info").then((lr) => {
        const daChay = lr.ok && lr.data;
        const chu = t("ux1a_cd_da_chuyen", { cach: mt1TenThe(ma) }) + them + (daChay ? "\n" + t("ux1a_cd_giu_ket_qua") : "");
        const toast = showToast(chu, "success", { sticky: true, hanhDong: { nhan: t("ux1a_cd_hoan_tac"), khiBam: () => {
          toast.goBo();
          if (mt1ToastCu === toast) mt1ToastCu = null;
          callApi("hoan_tac_muc_tieu", hoanTac).then((r2) => {
            if (!r2.ok) { the.loi(trErrs(r2.errors).join(" ")); return; }
            ghiChu = [];
            lamMoi(true);
          });
        } } });
        mt1ToastCu = toast;
        setTimeout(() => { toast.goBo(); if (mt1ToastCu === toast) mt1ToastCu = null; }, 10000);
      });
      lamMoi(true);
    });
  }

  function veNhom() {
    nhom.textContent = "";
    const hienTai = d && d.hien_tai === "danh_cho" && d.lan_cuoi ? d.lan_cuoi.nhom : null;
    const coNhieu = d && d.nhom.length > 1;
    nhom.hidden = !(coNhieu && (choNhom || hienTai));
    if (nhom.hidden) return;
    nhom.append(ux1aEl("span", { class: "mt1-nhom-nhan", text: t("mt1_chon_nhom") }));
    d.nhom.forEach((g) => {
      nhom.append(ux1aEl("button", { type: "button", class: "ux1a-vien mt1-nut", "data-nhom": g.nhan,
        "aria-pressed": g.nhan === hienTai ? "true" : "false", text: mt1NhanNhom(g.nhan),
        onclick: () => chon("danh_cho", g.nhan) }));
    });
  }

  function veChiTiet(du) {
    chiTiet.textContent = "";
    chiTiet.hidden = !(du && du.giu_cho && du.giu_cho.length);
    if (chiTiet.hidden) return;
    let giu = 0, suc = 0;
    du.giu_cho.forEach((c) => { giu += c.giu; suc += c.suc_chua || 0; });
    chiTiet.append(ux1aEl("summary", { text: t("mt1_giu_cho_tom", { giu, suc, nhom: mt1NhanNhom(du.nhom) }) }),
      ux1aEl("ul", { class: "mt1-ds" }, ...du.giu_cho.map((c) => ux1aEl("li", {
        text: t("mt1_giu_cho_dong", { ten: c.ten, giu: c.giu, suc: c.suc_chua || 0 }) }))));
  }

  function veTacDong() {
    const so = ++lan;
    hieuQua.hidden = true;
    canhBao.textContent = "";
    chiTiet.hidden = true;
    const hienTai = d && d.hien_tai;
    if (!MT1_THE.some((x) => x.ma === hienTai)) return;
    const nhomHT = hienTai === "danh_cho" && d.lan_cuoi ? d.lan_cuoi.nhom : null;
    callApi("uoc_tinh_muc_tieu", hienTai, nhomHT).then((r) => {
      if (so !== lan) return;                                    /* có lần vẽ mới hơn */
      const dongCanhBao = [];
      let chu = "";
      if (!r.ok) {
        dongCanhBao.push(...trErrs(r.errors));
      } else {
        const du = r.data;
        const lang = window.I18N.getLang();
        if (du.co_so_sanh) {
          const t0 = du.tot_hon, x0 = du.xuong_sau;
          chu = (t0.n === 0 && x0.n === 0 && !t0.duoi_5 && !x0.duoi_5)
            ? t("mt1_khong_doi")
            : t("mt1_uoc_tinh", { tot: mt1So(t0), xuong: mt1So(x0) });
        } else {
          const lines = lang === "en" ? du.mo_ta_en : du.mo_ta;
          const t1 = lines.filter((m) => m.nhom === "tang_1");
          const mo = t1.length ? t1 : lines.filter((m) => m.nhom === "tang_2");   /* bốc thăm thuần: chỉ có tầng 2 */
          const ngan = (s) => s.split(/\s[(–-]/)[0].trim();
          chu = mo.length ? t("ux1a_cd_cach_xet") + " " + mo.map((m) => ngan(m.chu)).join(" → ") : "";
        }
        trErrs(du.canh_bao || []).forEach((x) => dongCanhBao.push(x));
        veChiTiet(du);
      }
      const ghi = trErrs(ghiChu).filter((g) => !dongCanhBao.includes(g));
      hieuQua.textContent = [chu].concat(ghi).filter(Boolean).join(" ");
      hieuQua.hidden = !hieuQua.textContent;
      [...new Set(dongCanhBao)].forEach((g) => canhBao.append(ux1aEl("p", { class: "canh-bao-vang mt1-canh-bao", text: g })));
    });
  }

  function ve() {
    if (!d) return;
    const hienTai = d.hien_tai;
    const co = MT1_THE.some((x) => x.ma === hienTai);
    the.datCach(choNhom ? "danh_cho" : co ? hienTai : "");
    let ly = "";
    d.cac_the.forEach((c) => {
      the.khoa(c.id, c.khoa);
      if (c.khoa && !ly) ly = trErrs([c.ly_do]).join(" ");
    });
    lyDo.textContent = ly;
    lyDo.hidden = !ly;
    veNhom();
    rieng.textContent = "";
    rieng.hidden = co || choNhom;
    if (!rieng.hidden) {
      rieng.append(t("mt1_rieng") + " ");
      if (d.lan_cuoi) {
        rieng.append(ux1aEl("button", { type: "button", class: "btn btn-ghost btn-nho mt1-nut", text: t("mt1_ve_mau"),
          onclick: () => chon(d.lan_cuoi.id, d.lan_cuoi.nhom) }));
      }
    }
    if (choNhom) { hieuQua.hidden = true; canhBao.textContent = ""; chiTiet.hidden = true; return; }
    veTacDong();
  }

  function lamMoi(giuGhiChu) {
    if (!giuGhiChu) ghiChu = [];
    return callApi("get_muc_tieu").then((r) => {
      if (!r.ok) { hop.hidden = true; return; }
      hop.hidden = false;
      d = r.data;
      ve();
    });
  }

  window.addEventListener("langchange", () => { if (d) ve(); });
  return { hop, lamMoi };
}

/* ---- Dòng kết quả ở thẻ "Chi tiết và xuất tệp" ----------------------------------------------- */

function mt1VeKetQua() {
  const hop = el("mt1KetQua");
  if (!hop) return Promise.resolve();
  if (mt1Ngoai() || !(typeof wsTrangThai !== "undefined" && wsTrangThai && wsTrangThai.enabled)) {
    hop.hidden = true;
    return Promise.resolve();
  }
  return callApi("bao_cao_muc_tieu").then((r) => {
    hop.textContent = "";
    if (!r.ok || !r.data || !r.data.ap_dung) { hop.hidden = true; return; }
    const d = r.data;
    const ten = d.muc_tieu === "danh_cho" ? t("mt1_kq_the_danh_cho", { nhom: mt1NhanNhom(d.nhom) }) : mt1TenThe(d.muc_tieu);
    let chu = t("mt1_kq_dong", { ten });
    if (d.dat) chu += " — " + t("mt1_kq_dat", { k: d.dat.so_dat, m: d.dat.so_clb });
    if (d.co_so_sanh) {
      chu += (d.dat ? " · " : " — ") + t("mt1_kq_giup", { n: mt1So(d.duoc_giup) }) + " · " + t("mt1_kq_nhuong", { n: mt1So(d.nhuong_cho) });
    }
    const ct = ux1aEl("details", { class: "mt1-chi-tiet", id: "mt1KetQuaChiTiet" }, ux1aEl("summary", { text: t("mt1_kq_xem_them") }));
    const ds = ux1aEl("ul", { class: "mt1-ds" });
    const nv1 = t("mt1_kq_nv1", { pct: d.an_toan.nguyen_vong_1_pct });
    ds.append(ux1aEl("li", { text: d.an_toan_truoc ? nv1 + " " + t("mt1_kq_truoc", { pct: d.an_toan_truoc.nguyen_vong_1_pct }) : nv1 }));
    ds.append(ux1aEl("li", { text: t("mt1_kq_chua_co_cho", { n: mt1So(d.an_toan.chua_co_cho) }) }));
    if (d.nhom_duoc_giup) ds.append(ux1aEl("li", { text: t("mt1_kq_nhom_giup", { n: mt1So(d.nhom_duoc_giup) }) }));
    ct.append(ds);
    hop.append(ux1aEl("p", { class: "mt1-dong mt1-kq-dong", text: chu + "." }), ct);
    hop.hidden = false;
  });
}

function initMucTieu() {
  window.addEventListener("langchange", () => { mt1VeKetQua(); });
}
