/* js/20_xem_xet_chi_tieu.js — CT1: "Xem xét chỉ tiêu" (chỉ đọc, chỉ quản trị).

   Mở từ MỘT nút phụ "Gợi ý chỉ tiêu" ở góc phải thanh công cụ của thẻ Kết quả (#btnCt1Mo, cạnh nút vàng; chỉ quản trị). Backend: `get_xem_xet_chi_tieu` (đề xuất +
   kết quả sau từng bước, tính trong bộ nhớ, cùng bộ số bốc thăm đã khoá), `export_de_xuat_chi_tieu_csv`,
   `export_xem_xet_chi_tieu_csv`. KHÔNG có nút "Áp dụng": màn này không ghi chỉ tiêu nào.

   Luật thiết kế (Hick + Von Restorff): mỗi khung ≤ 7 điều khiển nhìn thấy; đúng MỘT nút vàng mỗi khung (khung "Khuyến nghị":
   xuất bảng đề xuất; khung "Tự thử": xếp lại); màu xanh / vàng chỉ mang nghĩa tăng / giảm và LUÔN kèm chữ (+4, −3, "Mất chỗ").
   Hình vẽ bằng thẻ div (không thư viện). Script thường (không ES module). */
"use strict";

const CT1_BUOC_HIEN = 6;      /* số bước hiện sẵn khi có ≤ 6 bước; nhiều hơn thì hiện 5 bước + "Xem thêm bước" (đủ 7 điều khiển) */
const CT1_O_TOI_DA = 64;       /* số ô vuông "chưa có CLB" vẽ tối đa (8 × 8); phần còn lại ghi "+N" bằng chữ, ngoài lưới */
const CT1_DONG_TOI_DA = 30;   /* số dòng tối đa của danh sách "tự thử" trên màn hình (CSV có đủ) */

let ct1Luot = false;          /* trường có > 1 buổi: mọi số đếm là LƯỢT (học sinh × buổi), nên dùng chuỗi `<khoá>_luot` */

/* Như t(), nhưng khi đếm theo lượt thì lấy biến thể `_luot` (nếu có) để nhãn không nói "học sinh" cho một con số lượt. */
function ct1T(khoa, p) {
  return t(ct1Luot && ct1Co(khoa + "_luot") ? khoa + "_luot" : khoa, p);
}
function ct1Co(khoa) {
  return t(khoa) !== khoa;
}

let ct1Du = null;             /* data của lần gọi gần nhất ở chế độ đề xuất */
let ct1Lan = 0;               /* lần gọi mới nhất: bỏ phản hồi về muộn */
let ct1HienHet = false;       /* đã bấm "Xem thêm bước" */
let ct1ThuBuoc = null;        /* bước tự chọn gần nhất đã xếp lại (để xuất CSV đúng bước đó) */
let ct1ThuDu = null;
let ct1TimerNhay = 0;

function ct1Dau(n) { return n > 0 ? "+" + n : n < 0 ? "−" + Math.abs(n) : "0"; }
function ct1Mo() { return !el("ct1Khung").hidden; }
function ct1Ten(d, id) { const c = d.clb.find((x) => x.club_id === id); return c ? c.ten : id; }

function ct1Trang(chu, loai) {
  const o = el("ct1TrangThai");
  o.textContent = chu || "";
  o.className = "ct1-trang-thai" + (loai ? " is-" + loai : "");
  o.hidden = !chu;
}

/* ---- Mở / đóng ------------------------------------------------------------------------------- */

function ct1MoKhung() {
  if (document.body.dataset.vai === "giao_vien") return;
  el("view-results").classList.add("ct1-dang-mo");
  el("ct1Khung").hidden = false;
  const d = el("ux1bThemMenu");
  if (d) d.open = false;
  ct1Tai();
  el("ct1TieuDe").scrollIntoView({ block: "start" });
}

function ct1DongKhung() {
  el("view-results").classList.remove("ct1-dang-mo");
  el("ct1Khung").hidden = true;
  ct1Lan += 1;
}

function ct1Tai() {
  const lan = ++ct1Lan;
  el("ct1Noi").hidden = true;
  ct1Trang(t("ct1_dang_tai"), "tai");
  callApi("get_xem_xet_chi_tieu").then((r) => {
    if (lan !== ct1Lan) return;
    if (!r.ok) {
      el("ct1Noi").hidden = true;
      const chua = (r.errors || []).some((e) => e.code === "gt2_chua_co_lan_chinh_thuc");
      ct1Trang(chua ? t("ct1_chua_co_kq") : t("ct1_loi", { errors: trErrs(r.errors).join("; ") }), chua ? "nhe" : "loi");
      return;
    }
    ct1Du = r.data;
    ct1HienHet = false;
    ct1Trang("", "");
    el("ct1Noi").hidden = false;
    ct1Ve();
  });
}

function ct1Ve() {
  if (!ct1Du) return;
  ct1Luot = (ct1Du.so_buoi || 1) > 1;
  ct1VeKhuyenNghi(ct1Du);
  ct1VeBuoc(ct1Du);
  ct1VeChonThu(ct1Du);
  ct1VeThieu(ct1Du);
  ct1VeBang(ct1Du);
  if (ct1ThuDu) ct1VeKqThu(ct1ThuDu, false);
}

/* ---- Khung 1: Khuyến nghị ------------------------------------------------------------------- */

function ct1Tile(nhan, giaTri, chuDel) {
  return ux1aEl("div", { class: "ct1-o" },
    ux1aEl("span", { class: "ct1-o-nhan", text: nhan }),
    ux1aEl("div", { class: "ct1-o-so" }, ...giaTri),
    chuDel);
}

function ct1VeKhuyenNghi(d) {
  const k = d.khuyen_nghi;
  el("ct1KnCau").textContent = k.so_cho_chuyen > 0
    ? t("ct1_kn_co", { k: k.so_cho_chuyen, a: k.so_clb_cho, b: k.so_clb_nhan })
    : t("ct1_kn_khong");
  el("ct1KnGhiChu").textContent = (d.truoc
    ? ct1T("ct1_kn_tong", { n: d.tong_cho, m: d.truoc.tong }) : ct1T("ct1_kn_tong", { n: d.tong_cho, m: d.so_hoc_sinh }))
    + (ct1Luot ? " " + t("ct1_luot_ghi_chu", { b: d.so_buoi }) : "");
  const luoi = el("ct1Tile");
  luoi.textContent = "";
  if (!d.truoc) return;                                   /* không có kết quả từng bước: bốn ô số cũng không có */
  const x = (s, cls) => ux1aEl("span", { class: cls, text: s });
  const mui = () => ux1aEl("span", { class: "ct1-mui-ten", "aria-hidden": "true", text: "→" });
  const tuNv = d.truoc.nv1, denNv = d.sau.nv1, tuKo = d.truoc.chua_co, denKo = d.sau.chua_co;
  const dNv = denNv - tuNv, dKo = denKo - tuKo;
  luoi.append(
    ct1Tile(t("ct1_o_nv1"), [x(tuNv, "ct1-so-cu"), mui(), x(denNv, "ct1-so-moi"),
      x(ct1T("ct1_o_nv1_don_vi", { n: d.truoc.tong }), "ct1-don-vi")],
    ux1aEl("span", { class: "ct1-o-dong " + (dNv > 0 ? "la-tang" : dNv < 0 ? "la-giam" : ""),
      text: dNv > 0 ? ct1T("ct1_o_them", { k: dNv }) : dNv < 0 ? ct1T("ct1_o_bot", { k: -dNv }) : ct1Dau(0) })),
    ct1Tile(t("ct1_o_chua_co"), [x(tuKo, "ct1-so-cu"), mui(), x(denKo, "ct1-so-moi"),
      x(ct1T("ct1_don_vi"), "ct1-don-vi")],
    ux1aEl("span", { class: "ct1-o-dong " + (dKo < 0 ? "la-tang" : dKo > 0 ? "la-giam" : ""),
      text: dKo < 0 ? ct1T("ct1_o_bot", { k: -dKo }) : dKo > 0 ? ct1T("ct1_o_them", { k: dKo }) : ct1Dau(0) })),
    ct1Tile(t("ct1_o_tot"), [x(d.so_tot_hon, "ct1-so-moi"), x(ct1T("ct1_don_vi"), "ct1-don-vi")],
      ux1aEl("span", { class: "ct1-o-dong", text: t("ct1_o_tot_phu") })),
    ct1Tile(t("ct1_o_kem"), [x(d.so_kem_hon, "ct1-so-moi"), x(ct1T("ct1_don_vi"), "ct1-don-vi")],
      ux1aEl("span", { class: "ct1-o-dong", text: d.so_kem_hon === 0 ? ct1T("ct1_o_kem_khong") : t("ct1_o_kem_co") })));
}

/* ---- Khung 2: kết quả sau từng bước --------------------------------------------------------- */

function ct1BangDoi(ds, coBuoi, gioiHan) {
  const bang = ux1aEl("table", { class: "data-table ct1-bang-doi" });
  const dau = ["ct1_c_ma", "ct1_c_ten", "ct1_c_lop"].concat(coBuoi ? ["ct1_c_buoi"] : [], ["ct1_c_truoc", "ct1_c_sau", "ct1_c_huong"]);
  bang.append(ux1aEl("thead", {}, ux1aEl("tr", {}, ...dau.map((k) => ux1aEl("th", { scope: "col", text: t(k) })))));
  const than = ux1aEl("tbody");
  const chuClb = (ten) => ten || t("ct1_chua_co_clb");
  ds.slice(0, gioiHan || ds.length).forEach((e) => {
    const huong = e.huong === "len" ? t("ct1_huong_len", { n: e.nv_sau })
      : e.huong === "xuong" ? t("ct1_huong_xuong", { n: e.nv_sau })
      : e.huong === "vao" ? t("ct1_huong_vao", { n: e.nv_sau }) : t("ct1_huong_ra");
    const o = ["student_id", "ten", "lop"].map((k) => ux1aEl("td", { text: e[k] }));
    if (coBuoi) o.push(ux1aEl("td", { text: nhanBuoi(e.buoi) }));
    o.push(ux1aEl("td", { text: chuClb(e.tu_ten) }), ux1aEl("td", { text: chuClb(e.den_ten) }),
      ux1aEl("td", { class: "ct1-huong " + (e.huong === "len" || e.huong === "vao" ? "la-tang" : "la-giam"), text: huong }));
    than.append(ux1aEl("tr", {}, ...o));
  });
  bang.append(than);
  return bang;
}

function ct1VeThanh(d) {
  const N = d.truoc.tong || 1;
  const hop = ux1aEl("div", { class: "ct1-hinh" });
  const dsDelta = d.buoc.map((b) => b.nv1_them);
  const tong = d.sau.nv1;
  const thanh = ux1aEl("div", { class: "ct1-thanh", role: "img",
    "aria-label": t("ct1_b_thanh_aria", {
      a: d.truoc.nv1, b: tong, n: d.truoc.tong,
      ds: d.buoc.map((b, i) => t("ct1_b_buoc_n", { i: i + 1, d: ct1Dau(dsDelta[i]) })).join(", ") }) });
  thanh.append(ux1aEl("div", { class: "ct1-doan la-goc", style: "width:" + (100 * d.truoc.nv1 / N).toFixed(2) + "%",
    text: t("ct1_b_hien_tai", { a: d.truoc.nv1 }) }));
  d.buoc.forEach((b, i) => {
    const dl = dsDelta[i];
    thanh.append(ux1aEl("div", { class: "ct1-doan " + (dl > 0 ? "la-tang" : dl < 0 ? "la-giam" : "la-giu"),
      style: "width:" + (100 * Math.abs(dl) / N).toFixed(2) + "%", title: t("ct1_b_buoc_n", { i: i + 1, d: ct1Dau(dl) }) }));
  });
  hop.append(
    ux1aEl("span", { class: "ct1-hinh-tde", text: t("ct1_b_nv1_tde", { a: d.truoc.nv1, b: tong }) }),
    thanh,
    ux1aEl("div", { class: "ct1-thanh-chu" },
      ux1aEl("span", { text: "0" }),
      ux1aEl("span", { text: t("ct1_b_thanh_ct", { ds: dsDelta.map(ct1Dau).join(", ") }) }),
      ux1aEl("span", { text: String(d.truoc.tong) })));
  return hop;
}

function ct1VeO(d) {
  const hop = ux1aEl("div", { class: "ct1-hinh" });
  const o = d.o_chua_co;
  const xep = o.filter((x) => x !== null);
  const luoi = ux1aEl("div", { class: "ct1-o-vuong", role: "img",
    "aria-label": ct1T("ct1_b_o_aria", { a: o.length, x: xep.length, b: d.sau.chua_co }) });
  const sapXep = o.slice().sort((p, q) => (p === null) - (q === null) || p - q);
  sapXep.slice(0, CT1_O_TOI_DA).forEach((b) => {
    luoi.append(ux1aEl("div", { class: "ct1-vuong " + (b === null ? "la-chua" : "la-xep"), text: b === null ? "" : "B" + b }));
  });
  hop.append(
    ux1aEl("span", { class: "ct1-hinh-tde", text: t("ct1_b_chua_co_tde", { a: d.truoc.chua_co, b: d.sau.chua_co }) }),
    luoi,
    ...(sapXep.length > CT1_O_TOI_DA    /* nhiều hơn mức vẽ: chữ "+N" NGOÀI lưới (không vẽ hàng nghìn ô) */
      ? [ux1aEl("span", { class: "ct1-thanh-chu ct1-o-con-lai", text: ct1T("ct1_b_o_con_lai", { n: sapXep.length - CT1_O_TOI_DA }) })] : []),
    ux1aEl("span", { class: "ct1-thanh-chu", text: ct1T("ct1_b_o_chu_thich") }));
  return hop;
}

function ct1LyDo(b) {
  const l = b.ly_do;
  const p1 = l.tu_trong > 0 ? t("ct1_b_ly_trong", { a: b.tu_ten, n: l.tu_trong }) : t("ct1_b_ly_het", { a: b.tu_ten, n: l.tu_nv1 });
  const p2 = l.den_chua_dap > 0 ? t("ct1_b_ly_nhan", { m: l.den_chua_dap, b: b.den_ten }) : t("ct1_b_ly_nhan_khong", { b: b.den_ten });
  return t("ct1_b_vi_sao", { ly_do: p1 + " " + p2 });
}

function ct1VeMotBuoc(b, coBuoi) {
  const chip = (cls, ten, truoc, sau) => ux1aEl("span", { class: "ct1-chip " + cls, text: ten + " " + truoc + " → " + sau });
  const trai = ux1aEl("div", { class: "ct1-buoc-trai" },
    ux1aEl("div", { class: "ct1-chips" },
      chip("la-giam", b.tu_ten, b.cap_tu_truoc, b.cap_tu_sau),
      ux1aEl("span", { "aria-hidden": "true", text: "→" }),
      chip("la-tang", b.den_ten, b.cap_den_truoc, b.cap_den_sau)),
    ux1aEl("p", { class: "ct1-vi-sao", text: ct1LyDo(b) }));
  const li = ux1aEl("li", { class: "ct1-buoc", id: "ct1Buoc" + b.stt },
    ux1aEl("span", { class: "ct1-so-buoc", text: String(b.stt) }));
  const phai = ux1aEl("div", { class: "ct1-buoc-phai" });
  if (b.co_ket_qua) {
    const so = (nhan, v, dl, tang) => ux1aEl("div", { class: "ct1-cot" },
      ux1aEl("span", { class: "ct1-cot-nhan", text: nhan }),
      ux1aEl("span", { class: "ct1-cot-so" }, String(v), " ",
        ux1aEl("span", { class: "ct1-cot-dl " + (dl === 0 ? "" : (dl > 0) === tang ? "la-tang" : "la-giam"), text: ct1Dau(dl) })));
    phai.append(
      so(t("ct1_b_cot_nv1"), b.nv1_sau, b.nv1_them, true),
      so(t("ct1_b_cot_chua_co"), b.chua_co_sau, b.chua_co_doi, false),
      ux1aEl("div", { class: "ct1-cot" }, ux1aEl("span", { class: "ct1-cot-nhan", text: t("ct1_b_cot_buoc") }),
        ux1aEl("span", { class: "ct1-cot-chu", text: t("ct1_b_len_xuong", { u: b.so_len, d: b.so_xuong }) })));
    if (b.so_xuong > 0) {
      trai.append(ux1aEl("p", { class: "ct1-luu-y", id: "ct1LuuY" + b.stt,
        text: b.so_mat_cho > 0 ? t("ct1_b_luu_y_mat", { d: b.so_xuong, x: b.so_mat_cho }) : t("ct1_b_luu_y", { d: b.so_xuong }) }));
    }
  }
  const doiMuc = b.co_ket_qua && b.so_doi > 0
    ? ux1aEl("details", { class: "ct1-doi", id: "ct1Doi" + b.stt },
      ux1aEl("summary", { class: "btn btn-secondary btn-nho ux6-mui-ten", id: "ct1DoiTom" + b.stt,
        text: t("ct1_b_xem", { k: b.so_doi }) }),
      ux1aEl("div", { class: "scroll-x" }, ct1BangDoi(b.doi, coBuoi))) : null;
  li.append(ux1aEl("div", { class: "ct1-buoc-cot" }, ux1aEl("div", { class: "ct1-buoc-than" }, trai, phai), doiMuc));
  return li;
}

function ct1VeBuoc(d) {
  const coKetQua = !!d.truoc;
  const coBuoi = d.clb.some((c) => c.buoi !== BUOI_MAC_DINH);
  el("ct1BuocMoTa").textContent = d.buoc.length ? t("ct1_b_mo_ta", { n: d.buoc.length }) : t("ct1_b_khong_buoc");
  const hinh = el("ct1BuocHinh");
  hinh.textContent = "";
  if (coKetQua && d.buoc.length) hinh.append(ct1VeThanh(d), ct1VeO(d));
  hinh.hidden = !(coKetQua && d.buoc.length);
  const ds = el("ct1DsBuoc");
  ds.textContent = "";
  const nhieu = d.buoc.length > CT1_BUOC_HIEN;
  const hien = ct1HienHet || !nhieu ? d.buoc : d.buoc.slice(0, CT1_BUOC_HIEN - 1);
  hien.forEach((b) => ds.append(ct1VeMotBuoc(b, coBuoi)));
  const them = el("btnCt1ThemBuoc");
  them.hidden = ct1HienHet || !nhieu;
  them.textContent = t("ct1_b_them", { n: d.buoc.length - hien.length });
  const ket = el("ct1KetBuoc");
  ket.hidden = !(coKetQua && d.buoc.length);
  ket.textContent = coKetQua
    ? ct1T("ct1_b_ket", { n: d.buoc.length, t: d.so_tot_hon, k: d.so_kem_hon }) + (d.so_moi_mat_cho > 0 ? " " + ct1T("ct1_b_mat_moi", { x: d.so_moi_mat_cho }) : "")
    : "";
  const kemNhieu = el("ct1KemNhieuHon");     /* chữ cảnh báo (không phải nút): chỉ khi số kém hơn LỚN HƠN số tốt hơn */
  kemNhieu.hidden = !(coKetQua && d.buoc.length && d.so_kem_hon > d.so_tot_hon);
  kemNhieu.textContent = kemNhieu.hidden ? "" : ct1T("ct1_b_kem_nhieu_hon", { k: d.so_kem_hon, t: d.so_tot_hon });
  el("btnCt1XuatDoiChieu").hidden = !(coKetQua && d.buoc.length);
  if (!coKetQua) {                          /* không xếp lại được: nói rõ lý do bằng chữ thường, phần còn lại vẫn xem được */
    el("ct1BuocMoTa").textContent = t("ct1_b_khong_ket_qua", { errors: trErrs(d.loi_giai || []).join("; ") });
  }
  (d.canh_bao || []).forEach((c) => { el("ct1BuocMoTa").textContent += " " + trErrs([c]).join(" "); });
}

/* ---- Khung "Tự thử một thay đổi" ------------------------------------------------------------ */

function ct1VeChonThu(d) {
  ["ct1ThuTu", "ct1ThuDen"].forEach((id) => {
    const o = el(id);
    const cu = o.value;
    o.textContent = "";
    o.append(ux1aEl("option", { value: "", text: t("ct1_thu_chon") }));
    d.clb.filter((c) => !c.loai_tru).forEach((c) => o.append(ux1aEl("option", { value: c.club_id, text: c.ten })));
    if (cu && d.clb.some((c) => c.club_id === cu)) o.value = cu;
  });
}

function ct1ThuXep() {
  const tu = el("ct1ThuTu").value, den = el("ct1ThuDen").value, k = parseInt(el("ct1ThuK").value, 10);
  const loi = el("ct1ThuLoi");
  loi.hidden = true;
  if (!tu || !den || tu === den) {
    loi.textContent = t("ct1_thu_chon_du");
    loi.hidden = false;
    return;
  }
  const buoc = [{ tu, den, k }];
  const nut = el("btnCt1ThuXep");
  nut.disabled = true;
  callApi("get_xem_xet_chi_tieu", buoc).then((r) => {
    nut.disabled = false;
    if (!r.ok) {
      loi.textContent = trErrs(r.errors).join("; ");
      loi.hidden = false;
      return;
    }
    ct1ThuBuoc = buoc;
    ct1ThuDu = r.data;
    ct1VeKqThu(r.data, true);
  });
}

function ct1VeKqThu(d, nhay) {
  const kq = el("ct1ThuKq");
  if (!d.truoc) {
    kq.hidden = true;
    return;
  }
  const doi = [].concat(...d.buoc.map((b) => b.doi || []));
  el("ct1ThuTieuDe").textContent = t("ct1_thu_kq", { a: d.truoc.nv1, b: d.sau.nv1, c: d.truoc.chua_co, d: d.sau.chua_co,
    u: d.buoc.reduce((s, b) => s + b.so_len, 0), v: d.buoc.reduce((s, b) => s + b.so_xuong, 0) });
  const hop = el("ct1ThuBangHop");
  hop.textContent = "";
  if (doi.length) {
    hop.append(ct1BangDoi(doi, d.clb.some((c) => c.buoi !== BUOI_MAC_DINH), CT1_DONG_TOI_DA));
    if (doi.length > CT1_DONG_TOI_DA) hop.append(ux1aEl("p", { class: "hint-text", text: t("ct1_thu_bot", { n: CT1_DONG_TOI_DA }) }));
  }
  kq.hidden = false;
  if (nhay) {
    kq.classList.remove("ct1-vua-xong");
    void kq.offsetWidth;                  /* khởi động lại hiệu ứng; CSS tắt nó khi giảm chuyển động */
    kq.classList.add("ct1-vua-xong");
    clearTimeout(ct1TimerNhay);
    ct1TimerNhay = setTimeout(() => kq.classList.remove("ct1-vua-xong"), 1800);
    kq.focus({ preventScroll: false });
  }
}

/* ---- Khung 3: thiếu chỗ / thừa chỗ ---------------------------------------------------------- */

function ct1ChuGiai() {
  const ul = el("ct1ThieuChuGiai");
  ul.textContent = "";
  [["la-cho", "ct1_t_cho"], ["la-tang", "ct1_t_thieu"], ["la-giam", "ct1_t_thua"], ["la-giu", "ct1_t_giu"]].forEach(([cls, k]) => {
    ul.append(ux1aEl("li", {}, ux1aEl("span", { class: "ct1-mau " + cls, "aria-hidden": "true" }), t(k)));
  });
}

function ct1VeThieu(d) {
  ct1ChuGiai();
  const ds = el("ct1ThieuDs");
  ds.textContent = "";
  const lon = Math.max(1, ...d.clb.map((c) => Math.max(c.cap, c.nv1)));
  d.clb.filter((c) => !c.loai_tru).slice().sort((p, q) => (q.nv1 / (q.cap || 1)) - (p.nv1 / (p.cap || 1)) || (p.club_id < q.club_id ? -1 : 1))
    .forEach((c) => {
      const cls = c.doi > 0 ? "la-tang" : c.doi < 0 ? "la-giam" : "la-giu";
      const the = c.doi > 0 ? t("ct1_t_the_tang", { d: ct1Dau(c.doi) }) : c.doi < 0 ? t("ct1_t_the_giam", { d: ct1Dau(c.doi) }) : t("ct1_t_the_giu");
      ds.append(ux1aEl("div", { class: "ct1-hang-thanh" },
        ux1aEl("span", { class: "ct1-ten", text: c.ten }),
        ux1aEl("div", { class: "ct1-hai-thanh", role: "img", "aria-label": t("ct1_t_dong", { a: c.nv1, b: c.cap }) + ", " + the },
          ux1aEl("div", { class: "ct1-thanh-mong la-cho", style: "width:" + (100 * c.cap / lon).toFixed(1) + "%" }),
          ux1aEl("div", { class: "ct1-thanh-mong " + cls, style: "width:" + (100 * c.nv1 / lon).toFixed(1) + "%" })),
        ux1aEl("span", { class: "ct1-ghi", text: t("ct1_t_dong", { a: c.nv1, b: c.cap }) + " · " + the })));
    });
  const nho = d.clb.filter((c) => !c.loai_tru && c.doi === 0 && c.cap <= 8 && c.nv1 < c.cap);
  const gc = el("ct1ThieuGhiChu");
  gc.hidden = !nho.length;
  gc.textContent = nho.length ? t("ct1_t_toi_thieu", { ds: nho.map((c) => c.ten).join(", ") }) : "";
}

/* ---- Khung 4: bảng chỉ tiêu đề xuất --------------------------------------------------------- */

function ct1VeBang(d) {
  const bang = el("ct1BangTab");
  const dau = bang.querySelector("thead");
  dau.textContent = "";
  dau.append(ux1aEl("tr", {}, ...[["ct1_bang_clb", ""], ["ct1_bang_cho", "so"], ["ct1_bang_nv1", "so ct1-phu"], ["ct1_bang_chua", "so ct1-phu"],
    ["ct1_bang_trong", "so ct1-phu"], ["ct1_bang_de_xuat", ""]].map(([k, c]) => ux1aEl("th", { scope: "col", class: c, text: t(k) }))));
  const than = bang.querySelector("tbody");
  than.textContent = "";
  d.clb.filter((c) => !c.loai_tru).forEach((c) => {
    const the = c.doi !== 0 ? c.cap_moi + " (" + ct1Dau(c.doi) + ")" : c.cap_moi + " (" + t("ct1_bang_giu") + ")";
    than.append(ux1aEl("tr", {}, ux1aEl("td", { class: "ct1-ten", text: c.ten }),
      ...[c.cap, c.nv1, c.chua_dap, c.trong].map((v, i) => ux1aEl("td", { class: i === 0 ? "so" : "so ct1-phu", text: String(v) })),
      ux1aEl("td", {}, ux1aEl("span", { class: "ct1-tag " + (c.doi > 0 ? "la-tang" : c.doi < 0 ? "la-giam" : "la-giu"), text: the }))));
  });
}

/* ---- Nối dây --------------------------------------------------------------------------------- */

el("btnCt1Mo").addEventListener("click", ct1MoKhung);
el("btnCt1Dong").addEventListener("click", ct1DongKhung);
el("btnCt1ThuXep").addEventListener("click", ct1ThuXep);
el("btnCt1ThemBuoc").addEventListener("click", () => { ct1HienHet = true; ct1VeBuoc(ct1Du); });
el("ct1LienTieuChi").addEventListener("click", (ev) => { ev.preventDefault(); ux1aMoNangCao(); });
el("btnCt1XuatDeXuat").addEventListener("click", () => {
  chayXuat([["ct1_xuat_muc_de_xuat", "export_de_xuat_chi_tieu_csv", [""], (d) => t("ct1_xuat_kq", { path: d.path })]], el("ct1PhanHoi"));
});
el("btnCt1XuatDoiChieu").addEventListener("click", () => {
  chayXuat([["ct1_xuat_muc_doi_chieu", "export_xem_xet_chi_tieu_csv", [""], (d) => t("ct1_xuat_kq", { path: d.path })]], el("ct1PhanHoi"));
});
el("btnCt1ThuXuat").addEventListener("click", () => {
  if (!ct1ThuBuoc) return;
  chayXuat([["ct1_xuat_muc_doi_chieu", "export_xem_xet_chi_tieu_csv", ["", ct1ThuBuoc], (d) => t("ct1_xuat_kq", { path: d.path })]], el("ct1PhanHoi"));
});
window.addEventListener("langchange", () => { if (ct1Mo() && ct1Du) ct1Ve(); });

/* Rời thẻ Kết quả rồi quay lại (hoặc chạy xếp lại) thì bắt đầu từ trang kết quả: số liệu CT1 có thể đã cũ. */
(function () {
  const cu = TAB_LOADERS.results;
  TAB_LOADERS.results = function () {
    if (ct1Mo()) ct1DongKhung();
    ct1ThuDu = null;
    ct1ThuBuoc = null;
    el("ct1ThuKq").hidden = true;
    return cu ? cu.apply(this, arguments) : undefined;
  };
})();
