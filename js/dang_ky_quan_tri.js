/* js/dang_ky_quan_tri.js — DK3-L3: màn quản trị. Ba thẻ: "Việc bây giờ" · "Danh sách" · "Thêm" (D36).
   Thẻ đầu chỉ hiện việc của giai đoạn hiện tại và đúng MỘT nút vàng. */
(function (global) {
  "use strict";
  const DK = global.DK, h = DK.h;
  const TEN_GD = { chuan_bi: "Chuẩn bị", gv_dang_ky: "Giáo viên đăng ký", duyet: "Duyệt CLB", hs_dang_ky: "Học sinh đăng ký",
    nhap_diem: "Nhập điểm", xuat: "Xuất" };
  const THU_TU = Object.keys(TEN_GD);
  let the = "viec";

  DK.quanTri = async function () {
    DK.henGio(110);
    const tt = (await global.RBDA.callApi("dk_trang_thai")).data;
    DK.S.tt = tt;
    const thanTheo = { viec: () => viecBayGio(tt), ds: () => danhSach(), them: () => them(tt) };
    const noiDung = h("div.dk-noidung");
    const the3 = [["viec", "Việc bây giờ"], ["ds", "Danh sách"], ["them", "Thêm"]];
    const thanh = h("nav.dk-the", { role: "tablist" }, the3.map(([k, t]) =>
      h("button.dk-the-nut", { type: "button", role: "tab", "aria-selected": String(k === the), onclick: () => { the = k; DK.quanTri(); } }, t)));
    DK.hien(DK.thanhDau("Quản trị · " + TEN_GD[tt.giai_doan]), thanh, noiDung);
    noiDung.replaceChildren(await thanTheo[the]());
  };

  const bang = (cot, hang) => h("table.dk-bang", {}, h("thead", {}, h("tr", {}, cot.map((c) => h("th", {}, c)))),
    h("tbody", {}, hang.map((r) => h("tr", {}, r.map((c) => h("td", {}, c))))));
  const chuyen = (gd, chu) => DK.nutVang(chu, function () {
    DK.chay(this, async () => { const r = await DK.goi("dk_chuyen_giai_doan", DK.S.token, gd); if (r.ok) DK.quanTri(); return r; });
  });
  const o = (ten, chu, thuoc) => DK.truong(chu, ten, thuoc);

  async function viecBayGio(tt) {
    const gd = tt.giai_doan, T = DK.S.token, goi = DK.goi;
    if (gd === "chuan_bi") {
      const ph = (await goi("dk_phong_danh_sach", T)).data || [];
      const fp = h("form.dk-form.dk-ngang", { novalidate: true }, o("ten", "Tên phòng"), o("sc", "Sức chứa", { type: "number" }));
      const them = DK.nut("Thêm phòng", function () { DK.chay(this, async () => {
        const r = await goi("dk_phong_luu", T, fp.elements.ten.value, fp.elements.sc.value); if (r.ok) DK.quanTri(); return r; }); });
      const van = h("textarea.dk-nhap", { rows: "5", placeholder: "Mỗi dòng: mã, họ tên, lớp (ví dụ: 10001\tNguyễn An\t10A1)" });
      const nap = DK.nut("Thêm vào danh sách học sinh", function () { DK.chay(this, async () => {
        const r = await goi("dk_hs_nap_danh_sach", T, van.value, "them");
        if (r.ok) { DK.thongBao("Mới " + r.data.moi + ", đã có " + r.data.da_co + ", lỗi " + r.data.loi.length + "."); hienPin(r.data.pin, "Mã PIN học sinh (chỉ hiện lúc này)"); }
        return r; }); });
      return h("div", {}, h("h2", {}, "1. Phòng"), bang(["Phòng", "Sức chứa"], ph.map((x) => [x.ten, x.suc_chua])), fp, them,
        h("h2", {}, "2. Danh sách học sinh"), van, nap, h("div#dkPin"), chuyen("gv_dang_ky", "Mở đăng ký giáo viên"));
    }
    if (gd === "gv_dang_ky") {
      const van = h("textarea.dk-nhap", { rows: "4", placeholder: "Mỗi dòng một tên giáo viên" });
      const tao = DK.nut("Tạo tài khoản giáo viên", function () { DK.chay(this, async () => {
        const r = await goi("dk_gv_tao_hang_loat", T, van.value); if (r.ok) hienPin(r.data.da_tao.map((x) => ({ ma: x.ten, pin: x.pin })), "Mã PIN giáo viên (chỉ hiện lúc này)"); return r; }); });
      const han = o("han", "Hạn chót (tuỳ chọn)", { type: "datetime-local" });
      const datHan = DK.nut("Đặt hạn", function () { DK.chay(this, () => goi("dk_dat_han", T, "gv_dang_ky", han.querySelector("input").value || null), "Đã lưu hạn."); });
      return h("div", {}, h("p.dk-phu", {}, "Mã trường dùng để giáo viên tự đăng ký do quản trị đặt lúc thiết lập."), van, tao, h("div#dkPin"), han, datHan,
        chuyen("duyet", "Đóng đăng ký giáo viên"));
    }
    if (gd === "duyet") {
      const ds = (await goi("dk_clb_danh_sach", T)).data || [];
      const dong = ds.map((c) => [c.ten, c.buoi, c.loai, c.giao_vien || "", c.phong || "", c.chi_tieu_gv === null ? "—" : c.chi_tieu_gv,
        { cho_duyet: "Chờ duyệt", duyet: "Đã duyệt", tu_choi: "Từ chối" }[c.trang_thai],
        c.trang_thai === "cho_duyet" ? h("span", {}, DK.nut("Duyệt", function () { DK.chay(this, async () => { const r = await goi("dk_clb_duyet", T, c.clb_id, "duyet"); if (r.ok) DK.quanTri(); return r; }); }),
          DK.nutNhe("Từ chối", function () { DK.chay(this, async () => { const r = await goi("dk_clb_duyet", T, c.clb_id, "tu_choi", null, null, "Không phù hợp"); if (r.ok) DK.quanTri(); return r; }); })) : ""]);
      return h("div", {}, bang(["CLB", "Buổi", "Loại", "Giáo viên", "Phòng", "Chỉ tiêu", "Trạng thái", ""], dong), chuyen("hs_dang_ky", "Mở cho học sinh"));
    }
    if (gd === "hs_dang_ky") {
      const tdo = (await goi("dk_tien_do", T)).data;
      return h("div", {}, h("h2", {}, "Tiến độ theo lớp (lớp chậm nhất trước)"),
        bang(["Lớp", "Đã nộp", "Tổng"], tdo.theo_lop.map((x) => [x.lop, x.da_nop, x.tong])), chuyen("nhap_diem", "Đóng đăng ký học sinh"));
    }
    if (gd === "nhap_diem") {
      const thieu = (await goi("dk_diem_thieu", T)).data || [];
      return h("div", {}, h("p", {}, thieu.length ? "Còn " + thieu.length + " bài thi chưa có điểm." : "Đã đủ điểm."),
        bang(["Mã", "Họ tên", "CLB"], thieu.map((x) => [x.ma, x.ho_ten, x.clb])), nutXep("Chốt và xếp", true));
    }
    const kq = h("p#dkKq");
    const tomTat = (await goi("dk_ket_qua_xep", T)).data || {};
    return h("div", {}, tomTat.da_xep ? bangKetQua(tomTat) : h("p", {}, "Chưa xếp lần nào."),
      DK.nutVang("Xuất Sổ nhập", function () { DK.chay(this, async () => {
        const r = await goi("dk_xuat_so_nhap", T); if (r.ok) kq.textContent = "Đã ghi " + r.data.duong_dan + " (" + r.data.so_clb + " CLB, " + r.data.so_hs + " học sinh)."; return r; }); }),
      tomTat.da_xep ? DK.nut("Xem kết quả trong phần mềm", () => { location.href = "index.html" + location.search + "#ket-qua"; }, { id: "dkXemKq" }) : null,
      nutXep("Xếp lại (cùng hạt giống)", false), kq);
  }

  /* DK4-L4: "Chốt và xếp" — một nút; xong thì vẽ lại màn (giai đoạn Xuất kèm bảng tóm tắt). */
  function nutXep(chu, vang) {
    const lam = function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_chot_va_xep", DK.S.token); if (r.ok) DK.quanTri(); return r; }); };
    return vang ? DK.nutVang(chu, lam, { id: "dkChot" }) : DK.nutNhe(chu, lam);
  }

  function bangKetQua(t) {
    const nv = (m) => Object.keys(m).sort().map((k) => "NV" + k + ": " + m[k]).join(" · ") || "—";
    return h("div#dkKetQua", {}, h("p", {}, "Đã xếp " + t.so_hoc_sinh + " học sinh (lần chạy " + t.run_id + ", hạt giống " + t.seed + ")."),
      t.da_bat_luat ? h("p#dkBatLuat.dk-phu", {}, "Lần này phần mềm đã tự bật hai luật cần cho đăng ký: giữ chỗ (fa_daa) và huy chương (wharton).") : null,
      bang(["Buổi", "Đã xếp", "Chưa xếp", "Theo nguyện vọng"], t.theo_buoi.map((x) => [x.buoi, x.da_xep, x.chua_xep, nv(x.theo_nguyen_vong)])));
  }

  function hienPin(ds, tieuDe) {
    const ch = document.getElementById("dkPin");
    if (ch) ch.replaceChildren(h("h3", {}, tieuDe), bang(["Mã / tên", "PIN"], ds.map((x) => [x.ma, x.pin])));
  }

  async function danhSach() {
    const T = DK.S.token;
    const [ph, gv, hs] = (await Promise.all([DK.goi("dk_phong_danh_sach", T), DK.goi("dk_gv_danh_sach", T), DK.goi("dk_hs_danh_sach", T)])).map((r) => r.data || []);
    const datLai = (ham, id, ten) => DK.nutNhe("Đặt lại PIN", function () { DK.chay(this, async () => {
      const r = await DK.goi(ham, T, id); if (r.ok) DK.thongBao("PIN mới của " + ten + ": " + r.data.pin); return r; }); });
    const moKhoa = (vai, ten) => DK.nutNhe("Mở khoá", function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_mo_khoa", T, vai, ten); if (r.ok) { DK.thongBao("Đã mở khoá cho " + ten); DK.quanTri(); } return r; }); });
    const thaoTac = (x, nut, vai, ten) => x.bi_khoa ? h("span.dk-thao-tac", {}, nut, h("span.dk-phu", {}, " Đang khoá "), moKhoa(vai, ten)) : nut;
    return h("div", {}, h("details", { open: true }, h("summary", {}, "Phòng (" + ph.length + ")"), bang(["Phòng", "Sức chứa"], ph.map((x) => [x.ten, x.suc_chua]))),
      h("details", {}, h("summary", {}, "Giáo viên (" + gv.length + ")"), bang(["Tên", "Cách tạo", ""], gv.map((x) => [x.ten, x.cach_tao === "quan_tri" ? "Quản trị tạo" : "Tự đăng ký", thaoTac(x, datLai("dk_gv_dat_lai_pin", x.gv_id, x.ten), "giao_vien", x.ten)]))),
      h("details", {}, h("summary", {}, "Học sinh (" + hs.length + ")"), bang(["Mã", "Họ tên", "Lớp", "Đã nộp", ""], hs.map((x) => [x.ma, x.ho_ten, x.lop, x.da_nop ? "Có" : "Chưa", thaoTac(x, datLai("dk_hs_dat_lai_pin", x.ma, x.ho_ten), "hoc_sinh", x.ma)]))));
  }

  async function them(tt) {
    const nk = (await DK.goi("dk_nhat_ky", DK.S.token, 30)).data || [];
    const i = THU_TU.indexOf(tt.giai_doan);
    return h("div", {}, i > 0 ? DK.nut("Lùi về giai đoạn «" + TEN_GD[THU_TU[i - 1]] + "»", function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_chuyen_giai_doan", DK.S.token, THU_TU[i - 1]); if (r.ok) { the = "viec"; DK.quanTri(); } return r; }); }) : null,
    h("details", {}, h("summary", {}, "Nhật ký (" + nk.length + ")"), bang(["Lúc", "Vai", "Việc", "Chi tiết"], nk.map((x) => [x.luc, x.vai, x.hanh_dong, x.chi_tiet || ""]))));
  }
})(window);
