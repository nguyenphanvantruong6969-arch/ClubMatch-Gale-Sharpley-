/* js/dang_ky_quan_tri.js — DK3-L3: màn quản trị. Bốn thẻ: "Việc bây giờ" · "Danh sách" · "Cài đặt" · "Thêm ▾" (D36).
   Thẻ đầu chỉ hiện việc của giai đoạn hiện tại và đúng MỘT nút vàng. DK8-L2: thanh thẻ nằm TRÊN; «Việc bây giờ» = một thẻ giai đoạn
   (thanh sáu bước + tiêu đề + giải thích + dòng đếm + hạn chót) rồi các thẻ nội dung, như bản mẫu v8. */
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
  const hanDep = (han) => { const m = String(han).match(/^\d{4}-(\d\d)-(\d\d)[T ](\d\d:\d\d)/); return m ? m[2] + "/" + m[1] + " " + m[3] : String(han).replace("T", " "); };   // v8: «28/11 03:53»
  const hanChu = (tt) => tt.han_chot ? h("p.dk-han#dkHan", {}, "Hạn chót ", h("b.dk-so", {}, hanDep(tt.han_chot)), " · " + conLai(tt.han_chot) + ". Đến hạn tự đóng.")
    : h("p.dk-han#dkHan", {}, "Chưa đặt hạn chót. Quản trị đóng đăng ký bằng nút bên dưới.");

  DK.quanTri = async function (tuDong) {          // tuDong = tự làm mới (DKL-M: hỏi dấu vân tay mỗi 5 giây): KHÔNG tính là thao tác, không đặt lại đồng hồ nghỉ
    if (!tuDong) DK.henGio(DK.GIAY_NGHI_QUAN_TRI, "Đã khoá quản lý vì không thao tác.");   // = GIAY_NGHI_QUAN_TRI của api_dang_ky.py (120 s, v8: 2 phút)
    if (DK.QT2) DK.QT2.tuLamMoi(false, !!tuDong);      // DKL-P: vẽ lại do vòng hỏi thì giữ dấu ĐÃ thấy (dauCho) cho lần bật lại
    const tt = (await global.RBDA.callApi("dk_trang_thai")).data;
    if (DK.S.vai !== "quan_tri") return;             // đã tự khoá/đăng xuất trong lúc chờ: không vẽ đè lên trang đầu
    DK.S.tt = tt;
    const thanTheo = { viec: () => viecBayGio(tt), ds: () => danhSach(), cai: () => DK.QT2.caiDat(), them: () => them(tt) };
    const noiDung = h("div.dk-noidung");
    const the3 = [["viec", "Việc bây giờ"], ["ds", "Danh sách"], ["cai", "Cài đặt"], ["them", "Thêm ▾"]];
    const thanh = h("nav.dk-the", { role: "tablist" }, the3.map(([k, t]) =>
      h("button.dk-the-nut", { type: "button", role: "tab", "aria-selected": String(k === the), onclick: () => { the = k; DK.quanTri(); } }, t)));
    DK.hien(DK.thanhDau("Quản trị · " + TEN_GD[tt.giai_doan]), thanh, noiDung);
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
    return h("details.dk-chon-han", {}, h("summary", {}, "Chọn hạn chót khác"), h("div.dk-hang-nut", {}, han, nut));
  }
  /* DK8-L2: dòng hạn chót của thẻ giai đoạn: chữ bên trái, «Gia hạn +1 giờ / +1 ngày» và «Đóng ngay» bên phải (v8 `waitFrame`). */
  const hangHan = (tt, gd) => h("div.dk-hang-han", {}, hanChu(tt), h("span.dk-gian"), DK.QT2.giaHan(gd, tt.han_chot));
  /* Thẻ giai đoạn (v8: tab «Việc bây giờ» = MỘT thẻ nổi) và thẻ nội dung (`DK.theCon`). */
  const theGd = (gd, tieuDe, mucDich, demChu, ...con) => h("section.dk-khung.dk-gd-the", {}, thanhGd(gd),
    h("div.dk-gd-dau", {}, h("h2", {}, tieuDe), h("p.dk-phu", {}, mucDich), demChu ? h("p.dk-dem", {}, demChu) : null), ...con);
  const o = (ten, chu, thuoc) => DK.truong(chu, ten, thuoc);

  async function viecBayGio(tt) {
    const gd = tt.giai_doan, T = DK.S.token, goi = DK.goi;
    const dsOf = async (ten, ...tham) => (await goi(ten, T, ...tham)).data || [];
    if (gd === "chuan_bi") {
      const [ph, hs, cd] = [await dsOf("dk_phong_danh_sach"), await dsOf("dk_hs_danh_sach"), (await goi("dk_cai_dat_doc", T)).data || {}];
      const fp = h("form.dk-form.dk-ngang", { novalidate: true }, o("ten", "Tên phòng"), o("sc", "Sức chứa", { type: "number" }));
      const them = DK.nut("Thêm phòng", function () { DK.chay(this, async () => {
        const r = await goi("dk_phong_luu", T, fp.elements.ten.value, fp.elements.sc.value); if (r.ok) DK.quanTri(); return r; }); });
      const van = h("textarea.dk-nhap", { rows: "5", placeholder: "Mỗi dòng: mã, họ tên, lớp (ví dụ: 10001\tNguyễn An\t10A1)" });
      const ly = [];
      if (!ph.length) ly.push("chưa có phòng");
      if (!hs.length) ly.push("chưa có danh sách học sinh");
      const toi = (id) => () => { const e = document.getElementById(id); if (e) e.scrollIntoView({ block: "start" }); };
      const muc = (xong, noi, sua) => h("li", {}, h("span.dk-tick" + (xong ? ".on" : ""), { "aria-hidden": "true" }, xong ? "✓" : "!"), h("span.dk-gian", {}, noi), DK.nutNhe("Sửa", sua));
      const kiem = h("ul.dk-kiem", {},
        muc(ph.length, ph.length + " phòng · tổng sức chứa " + ph.reduce((a, x) => a + x.suc_chua, 0), toi("dkKhungPhong")),
        muc(hs.length, hs.length + " học sinh · " + new Set(hs.map((x) => x.lop)).size + " lớp · đã có PIN", toi("dkKhungHs")),
        muc(!!cd.ma_truong, ["Mã trường cho giáo viên: ", h("span.dk-so", {}, cd.ma_truong || "—")], () => { the = "cai"; DK.quanTri(); }));
      return h("div", {},
        theGd(gd, "Chuẩn bị", "Kiểm tra ba mục dưới đây, rồi mở cho giáo viên đăng ký CLB.", "", kiem, DK.QT2.kiemTra(ly, chuyen("gv_dang_ky", "Mở đăng ký giáo viên"))),
        h("section#dkKhungPhong.dk-khung", {}, h("h3", {}, "1. Phòng"), DK.QT2.bangPhong(ph), fp, them),
        h("section#dkKhungHs.dk-khung", {}, h("h3", {}, "2. Danh sách học sinh"), h("p.dk-phu", {}, "Chỉ học sinh có tên ở đây mới đăng nhập được. Mỗi em một PIN in trên phiếu."),
          van, DK.QT2.napHocSinh(van, hienPin), h("div#dkPin")));
    }
    if (gd === "gv_dang_ky") {
      const [gv, ds] = [await dsOf("dk_gv_danh_sach"), await dsOf("dk_clb_danh_sach")];
      const van = h("textarea.dk-nhap", { rows: "4", placeholder: "Mỗi dòng một tên giáo viên" });
      const tao = DK.nut("Tạo tài khoản giáo viên", function () { DK.chay(this, async () => {
        const r = await goi("dk_gv_tao_hang_loat", T, van.value); if (r.ok) hienPin(r.data.da_tao.map((x) => ({ ma: x.ten, ten: x.ten, pin: x.pin })), "Mã PIN giáo viên (chỉ hiện lúc này)", "gv"); return r; }); });
      return h("div", {},
        theGd(gd, "Giáo viên đang đăng ký", "Thầy cô tự tạo tài khoản bằng mã trường và gửi CLB. Không cần làm gì cho tới hạn chót.",
          gv.length + " giáo viên · " + ds.length + " CLB đã gửi", hangHan(tt, gd), khungHan(gd), chuyen("duyet", "Đóng đăng ký giáo viên")),
        DK.theCon("CLB đã gửi", ds.length ? bang(["CLB", "Giáo viên", "Buổi", "Phòng", "Nhận"], ds.map((c) => [c.ten, c.giao_vien || "", c.buoi, c.phong || "",
          c.loai === "Tự do" ? "Mọi em" : String(c.chi_tieu !== null && c.chi_tieu !== undefined ? c.chi_tieu : (c.chi_tieu_gv === null || c.chi_tieu_gv === undefined ? "" : c.chi_tieu_gv))]))
          : h("div.dk-rong", {}, "Chưa có CLB nào. Danh sách hiện ở đây khi giáo viên gửi.")),
        DK.theCon("Tạo hộ tài khoản giáo viên", h("p.dk-phu", {}, "Mã trường dùng để giáo viên tự đăng ký do quản trị đặt lúc thiết lập. Hoặc dán tên (mỗi dòng một giáo viên) để tạo hộ; phần mềm tạo PIN 4 số cho từng người."),
          van, tao, h("div#dkPin")));
    }
    if (gd === "duyet") {
      const [ds, ph, hs] = [await dsOf("dk_clb_danh_sach"), await dsOf("dk_phong_danh_sach"), await dsOf("dk_hs_danh_sach")];
      const dem = (k) => ds.filter((c) => c.trang_thai === k).length;
      return h("div", {}, theGd(gd, "Duyệt CLB", "Duyệt hoặc từ chối từng CLB; sửa số nhận và phòng nếu cần. Học sinh chỉ thấy CLB đã duyệt.",
        dem("cho_duyet") + " chờ duyệt · " + dem("duyet") + " đã duyệt · " + dem("tu_choi") + " từ chối", DK.QT2.bangDuyet(ds, ph),
        DK.QT2.kiemTra(DK.QT2.lyDoChuaMoHs(ds, ph, hs.length), chuyen("hs_dang_ky", "Mở cho học sinh"))));
    }
    if (gd === "hs_dang_ky") {
      const [tdo, hs, ds, phs] = [(await goi("dk_tien_do", T)).data, await dsOf("dk_hs_danh_sach"), await dsOf("dk_clb_danh_sach"), await dsOf("dk_phong_danh_sach")];
      return h("div", {},
        theGd(gd, "Học sinh đang đăng ký", "Theo dõi lớp nào chưa đăng ký để nhắc. Học sinh không thấy các con số này.",
          hs.filter((x) => x.da_nop).length + "/" + hs.length + " em đã gửi", hangHan(tt, gd), khungHan("hs_dang_ky"), chuyen("nhap_diem", "Đóng đăng ký học sinh")),
        h("div.dk-luoi2", {},
          DK.theCon("Tiến độ theo lớp (lớp chậm nhất ở trên)", bang(["Lớp", "Đã nộp", "Tổng", ""], tdo.theo_lop.map((x) => [x.lop, x.da_nop, x.tong,
            h("progress.dk-tien", { max: String(x.tong || 1), value: String(x.da_nop || 0), "aria-label": "Lớp " + x.lop + ": " + x.da_nop + "/" + x.tong })]))),
          DK.QT2.nhuCau(tdo, hs)),
        h("section.dk-khung", {}, DK.QT2.suaSauMo(ds, phs)));
    }
    if (gd === "nhap_diem") {
      const [thieu, dsd] = [await dsOf("dk_diem_thieu"), await dsOf("dk_diem_danh_sach")];
      const tong = dsd.reduce((a, c) => a + c.hoc_sinh.length, 0), co = dsd.reduce((a, c) => a + c.hoc_sinh.filter((x) => x.diem !== null && x.diem !== undefined).length, 0);
      return h("div", {}, theGd(gd, "Nhập điểm", "Nhập điểm bài kiểm tra (0–10) từ Google Forms. Dưới điểm sàn hoặc không có điểm thì em không được xét vào CLB Tuyển chọn đó.",
        co + "/" + tong + " bài đã có điểm", nutXep("Chốt và xếp", true)),
      h("section.dk-khung", {}, h("p", {}, thieu.length ? "Còn " + thieu.length + " bài thi chưa có điểm." : "Mọi bài thi đã có điểm."), await DK.QT2.nhapDiem(dsd)));
    }
    const kq = h("p#dkKq");
    const tomTat = (await goi("dk_ket_qua_xep", T)).data || {};
    const xt = (await goi("dk_xuat_xem_truoc", T)).data || { clb: [], hoc_sinh: [], tong_hoc_sinh: 0, so_lan_xuat: 0 };
    return h("div", {}, theGd(gd, "Xuất Sổ nhập" + (xt.so_lan_xuat ? " · v" + xt.so_lan_xuat : ""), "Ghi Sổ nhập rồi nạp vào phần mềm xếp CLB. Xếp lại cùng hạt giống cho cùng kết quả.",
      xt.clb.length + " CLB · " + xt.tong_hoc_sinh + " học sinh",
      h("div.dk-hang-nut", {}, DK.nutVang("Xuất Sổ nhập", function () { DK.chay(this, async () => {
        const r = await goi("dk_xuat_so_nhap", T); if (r.ok) kq.textContent = "Đã ghi " + r.data.duong_dan + " (" + r.data.so_clb + " CLB, " + r.data.so_hs + " học sinh), phiên bản " + r.data.phien_ban + "."; return r; }); }),
      tomTat.da_xep ? DK.nut("Xem kết quả trong phần mềm", () => { location.href = "index.html" + location.search + "#ket-qua"; }, { id: "dkXemKq" }) : null,
      nutXep("Xếp lại (cùng hạt giống)", false)), kq),
    DK.theCon("Kết quả xếp", tomTat.da_xep ? bangKetQua(tomTat) : h("p", {}, "Chưa xếp lần nào.")),
    h("section.dk-khung", {}, await DK.QT2.xemTruoc(xt)));
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
    return h("div", {}, h("section.dk-khung", {}, h("div.dk-gd-dau", {}, h("h2", {}, "Danh sách"),
        h("p.dk-phu", {}, "Phòng, giáo viên và học sinh. Chỉ học sinh có tên ở đây mới đăng nhập được; mỗi em một PIN in trên phiếu."),
        h("p.dk-dem", {}, ph.length + " phòng · " + gv.length + " giáo viên · " + hs.length + " học sinh · " + hs.filter((x) => x.da_nop).length + " đã gửi nguyện vọng")),
      khoa ? h("p.dk-phu#dkKhoaDs", {}, "Học sinh đã bắt đầu đăng ký nên không thêm hay thay danh sách được nữa.") : null,
      ct("phong", true, "Phòng (" + ph.length + ")", bang(["Phòng", "Sức chứa"], ph.map((x) => [x.ten, x.suc_chua]))),
      ct("gv", false, "Giáo viên (" + gv.length + ")", bang(["Tên", "Cách tạo", ""], gv.map((x) => [x.ten, x.cach_tao === "quan_tri" ? "Quản trị tạo" : "Tự đăng ký", thaoTac(x, datLai("dk_gv_dat_lai_pin", x.gv_id, x.ten), "giao_vien", x.ten)]))),
      ct("hs", false, "Học sinh (" + hs.length + ")", ...(nhomHs.length ? nhomHs : [bang(cotHs, [])]))));
  }

  async function them(tt) {
    const nk = (await DK.goi("dk_nhat_ky", DK.S.token, 30)).data || [];
    const i = THU_TU.indexOf(tt.giai_doan);
    return h("div", {}, await DK.QT2.saoLuu(),
      DK.theCon("Lùi giai đoạn", h("p.dk-phu", {}, "Dùng khi cần sửa: mở lại đăng ký, hoặc mở khoá điểm đã chốt. Không xoá dữ liệu; có ghi nhật ký."),
        i > 0 ? DK.nut("Lùi về giai đoạn «" + TEN_GD[THU_TU[i - 1]] + "»", function () { DK.chay(this, async () => {
          const r = await DK.goi("dk_chuyen_giai_doan", DK.S.token, THU_TU[i - 1]); if (r.ok) { the = "viec"; DK.quanTri(); } return r; }); }) : h("p.dk-phu", {}, "Đang ở giai đoạn đầu tiên.")),
      DK.theCon("Nhật ký", h("details", {}, h("summary", {}, "Nhật ký (" + nk.length + ")"), bang(["Lúc", "Vai", "Việc", "Chi tiết"], nk.map((x) => [x.luc, x.vai, x.hanh_dong, x.chi_tiet || ""])))));
  }
})(window);
