/* js/dang_ky_nen.js — DK3-L3: nền của cổng đăng ký (dang_ky.html): dựng DOM an toàn, gọi API, đăng nhập, khởi tạo.
   Mọi chữ do người dùng nhập đi qua textContent (không innerHTML). Mỗi khung: tối đa MỘT nút vàng (D37). */
(function (global) {
  "use strict";
  const DK = global.DK = { S: { token: null, vai: null, ten: "", tt: null } };

  /* h("div.lop#id", {thuộc tính}, ...con) — con là chuỗi hoặc nút. */
  DK.h = function (tag, thuoc, ...con) {
    const m = String(tag).match(/^([a-z0-9]+)((?:[.#][\w-]+)*)$/i);
    const el = document.createElement(m ? m[1] : "div");
    (m && m[2] ? m[2].match(/[.#][\w-]+/g) : []).forEach((x) => {
      if (x[0] === ".") el.classList.add(x.slice(1)); else el.id = x.slice(1);
    });
    Object.entries(thuoc || {}).forEach(([k, v]) => {
      if (v === null || v === undefined || v === false) return;
      if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else if (k === "value") el.value = v;
      else el.setAttribute(k, v === true ? "" : v);
    });
    con.flat(Infinity).forEach((c) => { if (c !== null && c !== undefined && c !== false) el.append(c.nodeType ? c : String(c)); });
    return el;
  };
  const h = DK.h;

  DK.loiChu = function (errors) {
    return (errors || []).map((e) => {
      if (typeof e === "string") return e;
      const m = (global.I18N_ERROR_MESSAGES || {})[e.code];
      let t = m ? m.vi : e.code;
      Object.entries(e.params || {}).forEach(([k, v]) => { t = t.replace("{" + k + "}", v); });
      return t;
    }).join(" ");
  };

  DK.goi = async function (ten, ...tham) {
    const r = await global.RBDA.callApi(ten, ...tham);
    if (DK.S.token && !r.ok && r.errors && r.errors.some((e) => e && (e.code === "dk_het_phien_nghi" || e.code === "dk_can_dang_nhap"))) {   // đã đăng xuất (hết giờ) thì lời gọi còn bay không được ghi đè thông báo
      DK.dangXuatCuc(DK.loiChu(r.errors));
    }
    return r;
  };

  DK.thongBao = function (chu, loi) {
    const o = document.getElementById("dkThongBao");
    if (o) { o.textContent = chu || ""; o.className = "dk-thongbao" + (loi ? " la-loi" : chu ? " la-ok" : ""); }
  };

  DK.nutVang = (chu, lam, thuoc) => h("button.btn.btn-primary", Object.assign({ type: "button", onclick: lam }, thuoc), chu);
  DK.nut = (chu, lam, thuoc) => h("button.btn.btn-secondary", Object.assign({ type: "button", onclick: lam }, thuoc), chu);
  DK.nutNhe = (chu, lam, thuoc) => h("button.btn.btn-ghost", Object.assign({ type: "button", onclick: lam }, thuoc), chu);
  DK.truong = (nhan, ten, thuoc) => h("label.dk-truong", {}, h("span", {}, nhan), h("input.dk-nhap", Object.assign({ name: ten }, thuoc)));

  /* Chạy một thao tác của nút: khoá nút khi bận (chống bấm đúp), hiện lỗi/ok ở #dkThongBao. */
  DK.chay = async function (nut, ham, okChu) {
    if (nut) nut.disabled = true;
    try {
      const r = await ham();
      if (r && !r.ok) DK.thongBao(DK.loiChu(r.errors), true);
      else if (okChu) DK.thongBao(okChu);
      return r;
    } finally { if (nut) nut.disabled = false; }
  };

  DK.hien = function (...con) {
    const app = document.getElementById("dkApp");
    const ve = DK.S.vai === "quan_tri"      // DK4-L5: chỉ quản trị thấy lối sang phần mềm xếp (HS/GV ở lại cổng)
      ? h("a.dk-ve-phan-mem#dkVePhanMem", { href: "index.html" + location.search }, "← Mở phần mềm xếp CLB") : null;
    app.replaceChildren(...[ve, ...con.flat()].filter(Boolean), h("p#dkThongBao.dk-thongbao", { role: "status" }));
  };

  DK.khung = (tieuDe, ...con) => h("section.dk-khung", {}, h("h1.dk-tieude", {}, tieuDe), ...con);
  DK.veTrangDau = () => DK.nutNhe("← Về trang chọn vai trò", () => DK.dauTrang());   // D38

  DK.dangXuatCuc = function (chu) {
    clearTimeout(DK.hen);
    if (DK.S.token) DK.goi("dk_dang_xuat", DK.S.token);
    DK.S.token = null; DK.S.vai = null;
    DK.dauTrang().then(() => { if (chu) DK.thongBao(chu, true); });   // sau khi trang đầu dựng xong, nếu không chữ bị xoá theo trang cũ
  };

  /* ---------- trang chọn vai trò, đăng nhập, khởi tạo ---------- */
  DK.dauTrang = async function () {
    DK.S = { token: null, vai: null, ten: "", tt: null };
    const r = await global.RBDA.callApi("dk_trang_thai");
    if (!r.ok) { DK.hien(DK.khung("Cổng đăng ký", h("p", {}, DK.loiChu(r.errors)))); return; }
    DK.S.tt = r.data;
    if (!r.data.khoi_tao) { DK.manKhoiTao(); return; }
    DK.hien(DK.khung("Cổng đăng ký câu lạc bộ",
      h("p.dk-phu", {}, "Chọn vai trò để tiếp tục."),
      h("div.dk-nhom", {},
        DK.nut("Học sinh", () => DK.manDangNhap("hoc_sinh")),
        DK.nut("Giáo viên", () => DK.manDangNhap("giao_vien")),
        DK.nut("Quản trị", () => DK.manDangNhap("quan_tri")))));
  };

  DK.manKhoiTao = function () {
    const f = h("form.dk-form", { novalidate: true },
      DK.truong("Mật khẩu quản trị", "mk", { type: "password", autocomplete: "new-password" }),
      DK.truong("Mã trường (giáo viên dùng để tự đăng ký)", "ma"),
      DK.truong("Các buổi, cách nhau bằng dấu phẩy", "buoi", { value: "Thứ 2, Thứ 3, Thứ 4, Thứ 5, Thứ 6" }),
      DK.truong("Khối thấp nhất", "k1", { type: "number", value: "6" }),
      DK.truong("Khối cao nhất", "k2", { type: "number", value: "12" }));
    const b = DK.nutVang("Thiết lập cổng", () => DK.chay(b, async () => {
      const v = (n) => f.elements[n].value;
      const r = await DK.goi("dk_khoi_tao", v("mk"), v("ma"), v("buoi").split(",").map((x) => x.trim()).filter(Boolean), [+v("k1"), +v("k2")]);
      if (r.ok) DK.dauTrang();
      return r;
    }));
    DK.hien(DK.khung("Thiết lập lần đầu", f, b));
  };

  DK.manDangNhap = function (vai) {
    const la = { hoc_sinh: ["Mã học sinh", "Mã PIN"], giao_vien: ["Tên giáo viên", "Mã PIN"], quan_tri: [null, "Mật khẩu"] }[vai];
    const f = h("form.dk-form", { novalidate: true, onsubmit: (e) => { e.preventDefault(); b.click(); } },
      la[0] ? DK.truong(la[0], "ten", { autocomplete: "off" }) : null,
      DK.truong(la[1], "ma", { type: "password", autocomplete: "off" }));
    const b = DK.nutVang("Đăng nhập", () => DK.chay(b, async () => {
      const r = await DK.goi("dk_dang_nhap", vai, la[0] ? f.elements.ten.value : "", f.elements.ma.value);
      if (r.ok) { DK.S.token = r.data.token; DK.S.vai = vai; DK.S.ten = r.data.ten; DK.S.ma = r.data.id; DK.S.khoi = r.data.khoi; DK.S.lop = r.data.lop; DK.vaoVai(); }
      return r;
    }));
    DK.hien(DK.khung({ hoc_sinh: "Học sinh đăng nhập", giao_vien: "Giáo viên đăng nhập", quan_tri: "Quản trị đăng nhập" }[vai],
      f, b,
      vai === "quan_tri" ? h("p.dk-phu#dkTuKhoa", {}, "Tự khoá sau " + DK.GIAY_NGHI_QUAN_TRI / 60 + " phút không thao tác.") : null,
      vai === "giao_vien" ? DK.nut("Đăng ký tài khoản giáo viên", () => DK.manGvDangKy()) : null,
      DK.veTrangDau()));
  };

  DK.vaoVai = function () {
    if (DK.S.vai === "quan_tri") DK.quanTri();
    else if (DK.S.vai === "giao_vien") DK.giaoVien();
    else DK.hocSinh();
  };

  DK.manGvDangKy = function () {
    const f = h("form.dk-form", { novalidate: true },
      DK.truong("Mã trường", "ma"), DK.truong("Họ và tên giáo viên", "ten"),
      DK.truong("Mã PIN riêng (4 chữ số)", "pin", { type: "password", inputmode: "numeric", maxlength: "4" }));
    const b = DK.nutVang("Đăng ký", () => DK.chay(b, async () => {
      const r = await DK.goi("dk_gv_tu_dang_ky", f.elements.ma.value, f.elements.ten.value, f.elements.pin.value);
      if (r.ok) { DK.manDangNhap("giao_vien"); DK.thongBao("Đã đăng ký. Đăng nhập bằng tên và mã PIN vừa đặt."); }
      return r;
    }));
    DK.hien(DK.khung("Giáo viên tự đăng ký", f, b, DK.veTrangDau()));
  };

  /* Thanh đầu trang sau khi đăng nhập: tên, đăng xuất. */
  DK.thanhDau = (tieuDe) => h("header.dk-dau", {}, h("strong", {}, tieuDe), DK.S.ten && !tieuDe.startsWith(DK.S.ten) ? h("span.dk-phu", {}, DK.S.ten) : null, h("span.dk-gian"),
    DK.nutNhe("Đăng xuất", () => DK.dangXuatCuc()));

  /* Học sinh: tự đăng xuất sau 60 giây không thao tác (D25). Quản trị: máy chủ khoá sau 2 phút. */
  DK.GIAY_NGHI_QUAN_TRI = 120;                     // phải bằng GIAY_NGHI_QUAN_TRI trong api_dang_ky.py (đồng hồ khách bắt đầu trước khi máy chủ làm mới nên khoá trước)
  DK.henGio = function (giay, chu) {
    clearTimeout(DK.hen);
    DK.hen = setTimeout(() => DK.dangXuatCuc(chu || "Phiên đã kết thúc do để lâu không thao tác."), giay * 1000);
  };

  document.addEventListener("DOMContentLoaded", () => global.RBDA.choBackend(
    "dk_trang_thai", () => DK.dauTrang(), () => {}, (cau) => DK.hien(DK.khung("Cổng đăng ký", h("p", {}, cau)))));
})(window);
