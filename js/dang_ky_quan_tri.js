/* js/dang_ky_quan_tri.js — DK3-L3: màn quản trị. Ba thẻ: "Việc bây giờ" · "Danh sách" · "Thêm" (D36).
   Thẻ đầu chỉ hiện việc của giai đoạn hiện tại và đúng MỘT nút vàng. */
(function (global) {
  "use strict";
  const DK = global.DK, h = DK.h;
  const TEN_GD = DK.TEN_GD, THU_TU = DK.THU_TU;          // DK8-L1: dùng chung với thanh trên (dang_ky_nen.js)
  let the = "viec";

  /* DK4-UI: thanh sáu giai đoạn (đã xong ✓ · hiện tại nổi · chưa tới) và hạn chót kèm thời gian còn lại. */
  const thanhGd = (gd) => h("ol.dk-gd", { "aria-label": "Các giai đoạn" }, THU_TU.map((k, n) => {
    const c = THU_TU.indexOf(gd);
    return h("li", n < c ? { class: "xong" } : n === c ? { class: "cur", "aria-current": "step" } : {}, h("span.dk-gd-so", {}, n < c ? "✓" : String(n + 1)), TEN_GD[k]);
  }));
  const conLai = DK.conLai;
  const hanChu = (tt) => tt.han_chot ? h("p.dk-han#dkHan", {}, "Hạn chót ", h("b", {}, String(tt.han_chot).replace("T", " ")), " · " + conLai(tt.han_chot) + ". Đến hạn tự đóng.")
    : h("p.dk-han#dkHan", {}, "Chưa đặt hạn chót. Quản trị đóng đăng ký bằng nút bên dưới.");

  DK.quanTri = async function (tuDong) {          // tuDong = tự làm mới (DKL-M: hỏi dấu vân tay mỗi 5 giây): KHÔNG tính là thao tác, không đặt lại đồng hồ nghỉ
    if (!tuDong) DK.henGio(DK.GIAY_NGHI_QUAN_TRI, "Đã khoá quản lý vì không thao tác.");   // = GIAY_NGHI_QUAN_TRI của api_dang_ky.py (120 s, v8: 2 phút)
    if (DK.QT2) DK.QT2.tuLamMoi(false, !!tuDong);      // DKL-P: vẽ lại do vòng hỏi thì giữ dấu ĐÃ thấy (dauCho) cho lần bật lại
    const tt = (await global.RBDA.callApi("dk_trang_thai")).data;
    if (DK.S.vai !== "quan_tri") return;             // đã tự khoá/đăng xuất trong lúc chờ: không vẽ đè lên trang đầu
    DK.S.tt = tt;
    const thanTheo = { viec: () => viecBayGio(tt), ds: () => danhSach(), cai: () => DK.QT2.caiDat(), them: () => them(tt) };
    const noiDung = h("div.dk-noidung");
    const the3 = [["viec", "Việc bây giờ"], ["ds", "Danh sách"], ["cai", "Cài đặt"], ["them", "Thêm"]];
    const thanh = h("nav.dk-the", { role: "tablist" }, the3.map(([k, t]) =>
      h("button.dk-the-nut", { type: "button", role: "tab", "aria-selected": String(k === the), onclick: () => { the = k; DK.quanTri(); } }, t)));
    DK.hien(DK.thanhDau("Quản trị · " + TEN_GD[tt.giai_doan]), thanhGd(tt.giai_doan), thanh, noiDung);
    const nd = await thanTheo[the]();
    if (DK.S.vai === "quan_tri") noiDung.replaceChildren(nd);
    /* DKL-M + DK6-L1: tự cập nhật ở thẻ «Việc bây giờ» và «Danh sách» của bốn giai đoạn có người khác đang thay đổi dữ liệu
       (giáo viên đăng ký, duyệt, học sinh đăng ký, nhập điểm). KHÔNG tự làm mới: «Cài đặt», «Thêm», giai đoạn Chuẩn bị và Xuất
       (chỉ quản trị đổi chúng; vẽ lại thêm rủi ro mà không thêm giá trị). Mỗi lần vẽ, `tuLamMoi(false)` ở đầu hàm đã tắt vòng cũ. */
    if (DK.S.vai === "quan_tri" && (the === "viec" || the === "ds") && ["gv_dang_ky", "duyet", "hs_dang_ky", "nhap_diem"].includes(tt.giai_doan)) DK.QT2.tuLamMoi(true);
  };

  const bang = (cot, hang) => h("table.dk-bang", {}, h("thead", {}, h("tr", {}, cot.map((c) => h("th", {}, c)))),
    h("tbody", {}, hang.map((r) => h("tr", {}, r.map((c) => h("td", {}, c))))));
  DK.bang = bang;
  const chuyen = (gd, chu) => DK.nutVang(chu, function () {
    DK.chay(this, async () => { const r = await DK.goi("dk_chuyen_giai_doan", DK.S.token, gd); if (r.ok) DK.quanTri(); return r; });
  });
  function khungHan(gd) {
    const han = DK.truong("Hạn chót (tuỳ chọn)", "han", { type: "datetime-local", value: (DK.S.tt || {}).han_chot || "" });
    const nut = DK.nut("Đặt hạn", function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_dat_han", DK.S.token, gd, han.querySelector("input").value || null); if (r.ok) DK.quanTri(); return r; }); });
    return [han, nut];
  }
  const o = (ten, chu, thuoc) => DK.truong(chu, ten, thuoc);

  async function viecBayGio(tt) {
    const gd = tt.giai_doan, T = DK.S.token, goi = DK.goi;
    if (gd === "chuan_bi") {
      const ph = (await goi("dk_phong_danh_sach", T)).data || [];
      const soHs = ((await goi("dk_hs_danh_sach", T)).data || []).length;
      const fp = h("form.dk-form.dk-ngang", { novalidate: true }, o("ten", "Tên phòng"), o("sc", "Sức chứa", { type: "number" }));
      const them = DK.nut("Thêm phòng", function () { DK.chay(this, async () => {
        const r = await goi("dk_phong_luu", T, fp.elements.ten.value, fp.elements.sc.value); if (r.ok) DK.quanTri(); return r; }); });
      const van = h("textarea.dk-nhap", { rows: "5", placeholder: "Mỗi dòng: mã, họ tên, lớp (ví dụ: 10001\tNguyễn An\t10A1)" });
      const ly = [];
      if (!ph.length) ly.push("chưa có phòng");
      if (!soHs) ly.push("chưa có danh sách học sinh");
      return h("div", {}, h("h2", {}, "1. Phòng"), DK.QT2.bangPhong(ph), fp, them,
        h("h2", {}, "2. Danh sách học sinh"), h("p.dk-phu", {}, "Chỉ học sinh có tên ở đây mới đăng nhập được. Mỗi em một PIN in trên phiếu."), van, DK.QT2.napHocSinh(van, hienPin), h("div#dkPin"),
        DK.QT2.kiemTra(ly, chuyen("gv_dang_ky", "Mở đăng ký giáo viên")));
    }
    if (gd === "gv_dang_ky") {
      const van = h("textarea.dk-nhap", { rows: "4", placeholder: "Mỗi dòng một tên giáo viên" });
      const tao = DK.nut("Tạo tài khoản giáo viên", function () { DK.chay(this, async () => {
        const r = await goi("dk_gv_tao_hang_loat", T, van.value); if (r.ok) hienPin(r.data.da_tao.map((x) => ({ ma: x.ten, ten: x.ten, pin: x.pin })), "Mã PIN giáo viên (chỉ hiện lúc này)", "gv"); return r; }); });
      const [han, datHan] = khungHan(tt.giai_doan);
      return h("div", {}, hanChu(tt), h("p.dk-phu", {}, "Mã trường dùng để giáo viên tự đăng ký do quản trị đặt lúc thiết lập."), van, tao, h("div#dkPin"), han, datHan, DK.QT2.giaHan("gv_dang_ky", tt.han_chot),
        chuyen("duyet", "Đóng đăng ký giáo viên"));
    }
    if (gd === "duyet") {
      const ds = (await goi("dk_clb_danh_sach", T)).data || [];
      const ph = (await goi("dk_phong_danh_sach", T)).data || [];
      const soHs = ((await goi("dk_hs_danh_sach", T)).data || []).length;
      return h("div", {}, h("p.dk-phu", {}, "Duyệt hoặc từ chối từng CLB; sửa số nhận và phòng nếu cần. Học sinh chỉ thấy CLB đã duyệt."), DK.QT2.bangDuyet(ds, ph),
        DK.QT2.kiemTra(DK.QT2.lyDoChuaMoHs(ds, ph, soHs), chuyen("hs_dang_ky", "Mở cho học sinh")));
    }
    if (gd === "hs_dang_ky") {
      const tdo = (await goi("dk_tien_do", T)).data;
      const hs = (await goi("dk_hs_danh_sach", T)).data || [];
      const ds = (await goi("dk_clb_danh_sach", T)).data || [];
      const phs = (await goi("dk_phong_danh_sach", T)).data || [];
      return h("div", {}, hanChu(tt), h("h2", {}, "Tiến độ theo lớp (lớp chậm nhất ở trên)"),
        bang(["Lớp", "Đã nộp", "Tổng", ""], tdo.theo_lop.map((x) => [x.lop, x.da_nop, x.tong,
          h("progress.dk-tien", { max: String(x.tong || 1), value: String(x.da_nop || 0), "aria-label": "Lớp " + x.lop + ": " + x.da_nop + "/" + x.tong })])),
        DK.QT2.nhuCau(tdo, hs), DK.QT2.suaSauMo(ds, phs), ...khungHan("hs_dang_ky"), DK.QT2.giaHan("hs_dang_ky", tt.han_chot), chuyen("nhap_diem", "Đóng đăng ký học sinh"));
    }
    if (gd === "nhap_diem") {
      const thieu = (await goi("dk_diem_thieu", T)).data || [];
      return h("div", {}, h("h2", {}, "Nhập điểm bài thi"), h("p", {}, thieu.length ? "Còn " + thieu.length + " bài thi chưa có điểm." : "Mọi bài thi đã có điểm."),
        await DK.QT2.nhapDiem(), nutXep("Chốt và xếp", true));
    }
    const kq = h("p#dkKq");
    const tomTat = (await goi("dk_ket_qua_xep", T)).data || {};
    return h("div", {}, tomTat.da_xep ? bangKetQua(tomTat) : h("p", {}, "Chưa xếp lần nào."), await DK.QT2.xemTruoc(),
      DK.nutVang("Xuất Sổ nhập", function () { DK.chay(this, async () => {
        const r = await goi("dk_xuat_so_nhap", T); if (r.ok) kq.textContent = "Đã ghi " + r.data.duong_dan + " (" + r.data.so_clb + " CLB, " + r.data.so_hs + " học sinh), phiên bản " + r.data.phien_ban + "."; return r; }); }),
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
    /* DK6-L1: "ngoai" = hạng NULL trong match_results (dang_ky_sang_xep._dk_tom_tat_xep): em không vào được CLB nào trong danh sách của mình, được xếp bù vào CLB còn chỗ. */
    const GHI_CHU_NGOAI = "Học sinh không vào được CLB nào trong danh sách của mình, được xếp vào CLB còn chỗ.";
    const nv = (m) => Object.keys(m).sort((a, b) => (a === "ngoai") - (b === "ngoai") || (a < b ? -1 : a > b ? 1 : 0))
      .map((k, i) => [i ? " · " : "", k === "ngoai" ? h("span", { title: GHI_CHU_NGOAI }, "Xếp ngoài nguyện vọng") : "NV" + k, ": " + m[k]]);
    const nvChu = (m) => (Object.keys(m).length ? nv(m) : "—");
    return h("div#dkKetQua", {}, t.da_bat_luat ? h("p#dkLuuY", {}, "Lưu ý: chế độ giữ chỗ và huy chương đã được bật cho kho dữ liệu này.") : "",
      h("p", {}, "Đã xếp " + t.so_hoc_sinh + " học sinh (lần chạy " + t.run_id + ", hạt giống " + t.seed + ")."),
      bang(["Buổi", "Đã xếp", "Chưa xếp", "Theo nguyện vọng"], t.theo_buoi.map((x) => [x.ten_buoi || x.buoi, x.da_xep, x.chua_xep, nvChu(x.theo_nguyen_vong)])));
  }

  function hienPin(ds, tieuDe, vai) {
    const ch = document.getElementById("dkPin");
    if (ch) ch.replaceChildren(DK.QT2.phieuPin(ds, tieuDe, vai));
  }

  const moDs = new Map();      // DK6-L2: trạng thái mở/đóng các thẻ gấp của «Danh sách»
  async function danhSach() {
    const T = DK.S.token;
    const [ph, gv, hs] = (await Promise.all([DK.goi("dk_phong_danh_sach", T), DK.goi("dk_gv_danh_sach", T), DK.goi("dk_hs_danh_sach", T)])).map((r) => r.data || []);
    const datLai = (ham, id, ten) => DK.nutNhe("Đặt lại PIN", function () { DK.chay(this, async () => {
      const r = await DK.goi(ham, T, id); if (r.ok) DK.thongBao("PIN mới của " + ten + ": " + r.data.pin); return r; }); });
    const moKhoa = (vai, ten) => DK.nutNhe("Mở khoá", function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_mo_khoa", T, vai, ten); if (r.ok) { DK.thongBao("Đã mở khoá cho " + ten); DK.quanTri(); } return r; }); });
    const thaoTac = (x, nut, vai, ten) => x.bi_khoa ? h("span.dk-thao-tac", {}, nut, h("span.dk-phu", {}, " Đang khoá "), moKhoa(vai, ten)) : nut;
    const khoa = ["hs_dang_ky", "nhap_diem", "xuat"].includes((DK.S.tt || {}).giai_doan);
    /* DK6-L2: mỗi khối một `<details>` (tiêu đề «Khối 10 · 268 HS · 240 đã nộp»). Trạng thái mở/đóng của MỌI thẻ gấp được giữ trong `moDs`
       (khoá → true/false) nên vẫn còn sau khi tự làm mới (DK6-L1) hoặc bấm nút vẽ lại. */
    const ct = (khoa, macDinh, tieuDe, ...nd) => {
      const d = h("details", { open: moDs.has(khoa) ? moDs.get(khoa) : macDinh }, h("summary", {}, tieuDe), ...nd);
      d.addEventListener("toggle", () => moDs.set(khoa, d.open));
      return d;
    };
    const dongHs = (x) => [x.ma, x.ho_ten, x.lop, x.da_nop ? "Có" : "Chưa", thaoTac(x, datLai("dk_hs_dat_lai_pin", x.ma, x.ho_ten), "hoc_sinh", x.ma)];
    const cotHs = ["Mã", "Họ tên", "Lớp", "Đã nộp", ""];
    const khoiHs = [...new Set(hs.map((x) => x.khoi))].sort((a, b) => a - b);
    const nhomHs = khoiHs.map((k) => { const ds = hs.filter((x) => x.khoi === k);
      return ct("hs-khoi-" + k, khoiHs.length === 1, "Khối " + k + " · " + ds.length + " HS · " + ds.filter((x) => x.da_nop).length + " đã nộp", bang(cotHs, ds.map(dongHs))); });
    return h("div", {}, khoa ? h("p.dk-phu#dkKhoaDs", {}, "Học sinh đã bắt đầu đăng ký nên không thêm hay thay danh sách được nữa.") : null,
      ct("phong", true, "Phòng (" + ph.length + ")", bang(["Phòng", "Sức chứa"], ph.map((x) => [x.ten, x.suc_chua]))),
      ct("gv", false, "Giáo viên (" + gv.length + ")", bang(["Tên", "Cách tạo", ""], gv.map((x) => [x.ten, x.cach_tao === "quan_tri" ? "Quản trị tạo" : "Tự đăng ký", thaoTac(x, datLai("dk_gv_dat_lai_pin", x.gv_id, x.ten), "giao_vien", x.ten)]))),
      ct("hs", false, "Học sinh (" + hs.length + ")", ...(nhomHs.length ? nhomHs : [bang(cotHs, [])])));
  }

  async function them(tt) {
    const nk = (await DK.goi("dk_nhat_ky", DK.S.token, 30)).data || [];
    const i = THU_TU.indexOf(tt.giai_doan);
    return h("div", {}, await DK.QT2.saoLuu(), i > 0 ? DK.nut("Lùi về giai đoạn «" + TEN_GD[THU_TU[i - 1]] + "»", function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_chuyen_giai_doan", DK.S.token, THU_TU[i - 1]); if (r.ok) { the = "viec"; DK.quanTri(); } return r; }); }) : null,
    h("details", {}, h("summary", {}, "Nhật ký (" + nk.length + ")"), bang(["Lúc", "Vai", "Việc", "Chi tiết"], nk.map((x) => [x.luc, x.vai, x.hanh_dong, x.chi_tiet || ""]))));
  }
})(window);
