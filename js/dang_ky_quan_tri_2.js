/* js/dang_ky_quan_tri_2.js — DKL-L2/L4: phần quản trị bổ sung (đối chiếu bản mẫu v8): đóng sớm / gia hạn, nhập điểm, phiếu PIN,
   thay cả danh sách, sửa CLB, nhu cầu theo CLB, danh sách kiểm trước khi đi tiếp. Dùng DK.h / DK.goi / DK.bang của các tệp nền.
   Mã PIN chỉ nằm trong DOM ngay sau khi tạo / đặt lại (máy chủ chỉ lưu băm); không ghi ra nơi khác. */
(function (global) {
  "use strict";
  const DK = global.DK, h = DK.h;
  const QT2 = DK.QT2 = {};
  const T = () => DK.S.token;
  const TIEP = { gv_dang_ky: "duyet", hs_dang_ky: "nhap_diem" };
  const lamMoi = () => DK.quanTri();   // trả Promise: chờ vẽ lại xong rồi mới hiện thông báo

  /* ---------- A1: Đóng ngay · Gia hạn ---------- */
  const pad = (n) => String(n).padStart(2, "0");
  const iso = (d) => d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) + "T" + pad(d.getHours()) + ":" + pad(d.getMinutes());
  QT2.giaHan = function (gd, han) {
    const goc = han && !isNaN(new Date(han).getTime()) && new Date(han).getTime() > Date.now() ? new Date(han) : new Date();
    const them = (ms, chu) => DK.nut(chu, function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_dat_han", T(), gd, iso(new Date(goc.getTime() + ms)));
      if (r.ok) { DK.thongBao("Đã gia hạn."); lamMoi(); } return r; }); });
    /* DK8-L2 (v8): «Gia hạn» + «Đóng ngay» bên phải dòng hạn chót; hai nút gia hạn hiện sẵn (không giấu trong menu) để quản trị bấm một lần. */
    return h("div.dk-han-nut", {}, h("span.dk-phu", {}, "Gia hạn"), them(3600000, "+1 giờ"), them(86400000, "+1 ngày"),
      DK.nut("Đóng ngay", function () { DK.chay(this, async () => {
        const r = await DK.goi("dk_chuyen_giai_doan", T(), TIEP[gd]); if (r.ok) lamMoi(); return r; }); }));
  };

  /* ---------- A3: phiếu PIN in ra ---------- */
  QT2.phieuPin = function (ds, tieuDe, vai) {
    const laCua = (x) => (x.vai || vai) === "gv" ? "Đăng nhập: họ tên + PIN này." : "Đăng nhập: mã học sinh + PIN này.";    // DK9: một phiếu gộp học sinh và giáo viên
    const vung = h("section#dkIn.dk-in", { "aria-label": "Phiếu PIN" }, ds.map((x) => h("div.dk-phieu", {},
      h("b", {}, x.ten || x.ma), x.lop ? h("span", {}, " · " + x.lop) : null, h("div.dk-phieu-ma", {}, "Mã: ", x.ma), h("div.dk-phieu-pin", {}, "PIN ", h("b", {}, x.pin)),
      h("small", {}, laCua(x) + " Giữ kín PIN, không đưa bạn."))));
    const khung = h("div.dk-khung-pin", {}, h("h3", {}, tieuDe),
      DK.bang(["Mã / tên", "PIN"], ds.map((x) => [x.ten ? x.ten : x.ma, x.pin])),
      DK.nut("Xem phiếu PIN", function () { vung.classList.toggle("mo"); }, { id: "dkXemPhieu" }),
      DK.nutNhe("In phiếu", () => { vung.classList.add("mo"); try { global.print(); } catch (e) { DK.thongBao("Trình duyệt chặn in. Dùng nút Chép PIN.", true); } }, { id: "dkInPhieu" }),
      DK.nutNhe("Chép PIN", () => { const t = ds.map((x) => x.ma + "\t" + x.pin).join("\n");
        (global.navigator.clipboard ? global.navigator.clipboard.writeText(t) : Promise.reject()).then(() => DK.thongBao("Đã chép vào bộ nhớ tạm."), () => DK.thongBao("Không chép được. Bôi đen bảng rồi nhấn Ctrl+C.", true)); }),
      vung);
    return khung;
  };

  /* ---------- A4: thêm / thay cả danh sách học sinh ---------- */
  QT2.napHocSinh = function (van, hien) {
    const goiNap = async (che) => {
      const r = await DK.goi("dk_hs_nap_danh_sach", T(), van.value, che);
      if (!r.ok) return r;
      const dsr = (await DK.goi("dk_hs_danh_sach", T())).data || [];
      const ten = {}; dsr.forEach((x) => { ten[x.ma] = x; });
      DK.thongBao("Mới " + r.data.moi + ", đã có " + r.data.da_co + ", lỗi " + r.data.loi.length + ".");
      hien(r.data.pin.map((x) => ({ ma: x.ma, pin: x.pin, ten: (ten[x.ma] || {}).ho_ten, lop: (ten[x.ma] || {}).lop })), "Mã PIN học sinh (chỉ hiện lúc này)", "hs");
      return r;
    };
    const them = DK.nut("Thêm vào danh sách học sinh", function () { DK.chay(this, () => goiNap("them")); });
    const hop = h("div#dkThayHop.dk-xacnhan", { hidden: true }, h("p", {}, "Thay cả danh sách học sinh? Mọi nguyện vọng đã có sẽ bị xoá. Em cũ không có trong danh sách mới sẽ mất tài khoản."),
      DK.nutNhe("Đồng ý, thay", function () { DK.chay(this, async () => { const r = await goiNap("thay"); hop.hidden = true; return r; }); }, { id: "dkThayCo" }),
      DK.nutNhe("Huỷ", () => { hop.hidden = true; }));
    const thay = DK.nutNhe("Thay cả danh sách", () => { hop.hidden = false; }, { id: "dkThay" });
    return h("div", {}, h("div.dk-hang-nut", {}, them, thay), hop);
  };

  /* ---------- A2: nhập điểm ---------- */
  const so = (v) => (v === null || v === undefined ? "" : String(v).replace(".", ","));
  QT2.nhapDiem = async function (ds0) {
    const ds = ds0 || (await DK.goi("dk_diem_danh_sach", T())).data || [];
    if (!ds.length) return h("p.dk-phu", {}, "Không CLB nào có thi. Bấm «Chốt và xếp» để sang bước xếp.");
    const khoi = ds.map((c) => {
      const chip = (hs, o) => {
        const v = parseFloat(String(o.value).replace(",", "."));
        hs.chip.className = "chip " + (o.value === "" ? "wait" : c.diem_san !== null && v < c.diem_san ? "off" : "on");
        hs.chip.textContent = o.value === "" ? "Chưa có" : c.diem_san !== null && v < c.diem_san ? "Dưới sàn" : "Đạt";
      };
      const hang = c.hoc_sinh.map((x) => {
        const o = h("input.dk-nhap.dk-diem", { type: "text", inputmode: "decimal", value: so(x.diem), "aria-label": "Điểm " + x.ma });
        const hs = { chip: h("span.chip") }; chip(hs, o);
        o.addEventListener("change", () => DK.chay(null, async () => {
          const r = await DK.goi("dk_diem_dat", T(), x.ma, c.clb_id, o.value.trim() === "" ? null : o.value);
          if (r.ok) chip(hs, o); else o.classList.add("la-loi"); return r; }));
        return [x.ma, x.ho_ten, x.lop, o, hs.chip];
      });
      const van = h("textarea.dk-nhap", { rows: "3", placeholder: "Mỗi dòng: Mã HS, dấu Tab, điểm. Chép hai cột từ trang tính là đúng dạng." });
      const dan = DK.nut("Lưu điểm đã dán", function () { DK.chay(this, async () => {
        if (!van.value.trim()) return { ok: false, errors: ["Dán ít nhất một dòng trước."] };       // DK8-L5: là lỗi nhập, không phải «xong»
        const r = await DK.goi("dk_diem_dan", T(), c.clb_id, van.value);
        if (r.ok) { const chu = "Đã lưu " + r.data.da_luu + " điểm" + (r.data.loi.length ? ", " + r.data.loi.length + " dòng lỗi (dòng " + r.data.loi.map((e) => e.dong).join(", ") + ")." : "."); await lamMoi(); DK.thongBao(chu); } return r; }); });
      return h("details", { open: ds.length === 1 }, h("summary", {}, c.ten + " (" + c.hoc_sinh.length + " em" + (c.diem_san !== null ? ", điểm sàn " + c.diem_san : "") + ")"),
        h("p.dk-phu", {}, "Điểm từ 0 đến 10, dấu phẩy hoặc chấm (8,5 = 8.5). Không làm bài, hoặc dưới mốc điểm, thì em không được xét vào CLB đó."),
        van, dan, DK.bang(["Mã", "Họ tên", "Lớp", "Điểm", ""], hang));
    });
    const kq = h("p#dkChotDiemKq.dk-phu");
    const chot = DK.nut("Chốt điểm", function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_diem_thieu", T());
      if (r.ok) kq.textContent = r.data.length ? "Còn " + r.data.length + " bài thi chưa có điểm." : "Mọi bài thi đã có điểm. Bấm «Chốt và xếp» để xếp."; return r; }); }, { id: "dkChotDiem" });
    return h("div", {}, ...khoi, chot, kq);
  };

  /* ---------- A5 / A8: phòng và danh sách kiểm ---------- */
  QT2.bangPhong = (ph) => DK.bang(["Phòng", "Sức chứa", ""], ph.map((x) => [x.ten, x.suc_chua, x.dang_dung ? h("span.dk-phu", {}, "Đang có CLB") :
    DK.nutNhe("Xoá", function () { DK.chay(this, async () => { const r = await DK.goi("dk_phong_xoa", T(), x.phong_id); if (r.ok) lamMoi(); return r; }); })]));
  QT2.kiemTra = function (ly, nutDi) {
    return ly.length ? h("p.dk-chua-di#dkChuaDi", { role: "alert" }, h("span.dk-chua-di-bieu", { "aria-hidden": "true" }, "!"), "Chưa đi tiếp được: " + ly.join(", ") + ".") : nutDi;
  };

  /* ---------- A6: duyệt có sửa chỉ tiêu / phòng ---------- */
  QT2.bangDuyet = function (ds, ph) {
    const dong = ds.map((c) => {
      const ct = h("input.dk-nhap.dk-so", { type: "number", min: "1", value: c.chi_tieu !== null ? c.chi_tieu : (c.chi_tieu_gv !== null ? c.chi_tieu_gv : ""), "aria-label": "Chỉ tiêu " + c.ten, disabled: c.loai === "Tự do" || c.trang_thai === "tu_choi" });
      const sel = h("select.dk-nhap", { "aria-label": "Phòng " + c.ten, disabled: c.trang_thai === "tu_choi" }, ph.map((p) => h("option", { value: p.phong_id, selected: p.phong_id === c.phong_id }, p.ten + " (" + p.suc_chua + ")")));
      const dat = (qd) => function () { DK.chay(this, async () => {
        const r = await DK.goi("dk_clb_duyet", T(), c.clb_id, qd, qd === "duyet" ? (ct.value || null) : null, qd === "duyet" ? +sel.value : null, qd === "tu_choi" ? "Không phù hợp" : "");
        if (r.ok) lamMoi(); return r; }); };
      const tt = { cho_duyet: "Chờ duyệt", duyet: "Đã duyệt", tu_choi: "Từ chối" }[c.trang_thai];
      return [c.ten, c.buoi, c.loai, c.giao_vien || "", sel, ct, tt, c.trang_thai === "tu_choi" ? "" : h("span", {}, DK.nut(c.trang_thai === "duyet" ? "Lưu thay đổi" : "Duyệt", dat("duyet")), c.trang_thai === "duyet" ? null : DK.nutNhe("Từ chối", dat("tu_choi")))];
    });
    return DK.bang(["CLB", "Buổi", "Loại", "Giáo viên", "Phòng", "Chỉ tiêu", "Trạng thái", ""], dong);
  };
  QT2.lyDoChuaMoHs = function (ds, ph, soHs) {
    const ly = [];
    if (!ph.length) ly.push("chưa có phòng");
    if (!soHs) ly.push("chưa có danh sách học sinh");
    const cho = ds.filter((c) => c.trang_thai === "cho_duyet").length, duyet = ds.filter((c) => c.trang_thai === "duyet");
    if (cho) ly.push("còn " + cho + " CLB chờ duyệt");
    if (!duyet.length) ly.push("chưa có CLB nào được duyệt");
    else { const thieu = [...new Set(duyet.map((c) => c.buoi))].filter((b) => !duyet.some((c) => c.buoi === b && c.loai === "Tự do")); if (thieu.length) ly.push("buổi " + thieu.join(", ") + " chưa có CLB Tự do"); }
    return ly;
  };

  /* ---------- A6b + A7: giai đoạn học sinh đăng ký ---------- */
  QT2.suaSauMo = function (ds, ph) {
    /* Đổi phòng / xoá sau khi mở cho học sinh: lần gọi đầu chỉ báo "N học sinh bị ảnh hưởng"; đồng ý rồi mới ghi (D19). */
    const xacNhan = async (c, ...tham) => {
      const r = await DK.goi("dk_clb_sua_sau_mo", T(), c.clb_id, ...tham, false);
      if (!r.ok || !r.data.can_xac_nhan) { if (r.ok) lamMoi(); return r; }
      if (global.confirm && !global.confirm(r.data.anh_huong + " học sinh bị ảnh hưởng. Việc này ghi vào nhật ký. Tiếp tục?")) return r;
      const r2 = await DK.goi("dk_clb_sua_sau_mo", T(), c.clb_id, ...tham, true);
      if (r2.ok) lamMoi(); return r2;
    };
    const dong = ds.filter((c) => c.trang_thai === "duyet").map((c) => {
      const ct = h("input.dk-nhap.dk-so", { type: "number", min: String(c.chi_tieu || 1), value: c.chi_tieu !== null ? c.chi_tieu : "", disabled: c.loai === "Tự do", "aria-label": "Chỉ tiêu " + c.ten });
      const sel = h("select.dk-nhap", { "aria-label": "Phòng " + c.ten }, (ph || []).map((p) => h("option", { value: p.phong_id, selected: p.phong_id === c.phong_id }, p.ten + " (" + p.suc_chua + ")")));
      const luu = DK.nutNhe("Tăng chỉ tiêu", function () { DK.chay(this, async () => {
        const r = await DK.goi("dk_clb_sua_sau_mo", T(), c.clb_id, ct.value || null); if (r.ok) { DK.thongBao("Đã lưu."); lamMoi(); } return r; }); });
      const doiPhong = DK.nutNhe("Đổi phòng", function () { DK.chay(this, () => xacNhan(c, null, +sel.value, null, false)); });
      const xoa = DK.nutNhe("Xoá CLB", function () { DK.chay(this, () => xacNhan(c, null, null, null, true)); });
      return [c.ten, c.buoi, c.loai, ct, sel, h("span", {}, luu, doiPhong, xoa)];
    });
    return h("details", {}, h("summary", {}, "Sửa CLB đã duyệt (" + dong.length + ")"), DK.bang(["CLB", "Buổi", "Loại", "Chỉ tiêu", "Phòng", ""], dong));
  };
  QT2.nhuCau = function (tdo, hs) {
    const chua = hs.filter((x) => !x.da_nop);
    const theoLop = {}; chua.forEach((x) => { (theoLop[x.lop] = theoLop[x.lop] || []).push(x); });
    return h("section#dkNhuCau.dk-khung", {}, h("h3", {}, "Nhu cầu theo CLB"), h("p.dk-phu", {}, "Theo dõi lớp nào chưa đăng ký để nhắc. Học sinh không thấy các con số này."),
      DK.bang(["CLB", "Số em chọn"], tdo.theo_clb.map((x) => [x.ten, x.so_em])),
      h("details#dkChuaDangKy", {}, h("summary", {}, "Chưa đăng ký (" + chua.length + " em)"),
        chua.length ? DK.bang(["Lớp", "Chưa nộp"], Object.keys(theoLop).sort().map((l) => [l, theoLop[l].map((x) => x.ma + " " + x.ho_ten).join("; ")])) : h("p.dk-phu", {}, "Mọi em đã gửi.")),
      DK.nutNhe("Làm mới", () => lamMoi(), { id: "dkLamMoi" }));
  };

  /* ---------- DK9: nạp MỘT tệp Excel (học sinh, giáo viên, phòng) ----------
     Chọn / thả tệp -> «Xem trước» (máy chủ chỉ ĐỌC) -> «Nạp» (máy chủ đọc lại tệp, không tin bản xem trước). Mỗi dòng lỗi có số dòng Excel và lý
     do (mã `dk_excel_*` trong i18n_errors.py, đổi chữ bằng DK.loiChu). PIN chỉ hiện ngay sau «Nạp» (phiếu PIN gộp học sinh và giáo viên).
     Giai đoạn học sinh đã bắt đầu đăng ký: trang «Học sinh» bị bỏ qua, như ô dán («không thêm hay thay danh sách được nữa»). */
  const TRANG_XL = [["hoc_sinh", "Học sinh"], ["giao_vien", "Giáo viên"], ["phong", "Phòng"]];
  const TOI_DA_LOI_HIEN = 50, TOI_DA_MB = 5;
  QT2.napExcel = function (c) {
    const khoa = ["hs_dang_ky", "nhap_diem", "xuat"].includes(c.giai_doan);
    let tep = null, xt = null;
    const ten = h("p#dkExcelTen.dk-phu", {}, "Chưa chọn tệp.");
    const xem = h("div#dkExcelXem.dk-excel-xem");
    const pin = h("div#dkPin");
    const nap = DK.nutVang("Nạp", function () { const b = this; DK.chay(b, napDi).then(() => { if (!tep) b.disabled = true; }); }, { id: "dkExcelNap", disabled: true });
    const doc = (f) => new Promise((xong, hong) => { const r = new global.FileReader(); r.onload = () => xong(String(r.result).split(",").slice(1).join(",")); r.onerror = () => hong(r.error); r.readAsDataURL(f); });
    const loiChu = (ma, tham) => DK.thongBao(DK.loiChu([{ code: ma, params: tham || {} }]), true);
    const ve = () => {
      const hang = TRANG_XL.map(([k, tenTrang]) => {
        const m = xt[k];
        if (k === "hoc_sinh" && xt.hs_bi_khoa) return [tenTrang, "Đã khoá", "—", "—", "—"];
        if (!m.co) return [tenTrang, "Không có trang", "—", "—", "—"];
        return [tenTrang, String(m.moi + m.da_co), String(m.moi), String(m.da_co), String(m.loi.length)];
      });
      const soLoi = TRANG_XL.reduce((a, [k]) => a + xt[k].loi.length, 0);
      const chu = xt.co_the_nap ? "Sẽ nạp " + xt.so_hop_le + " dòng hợp lệ" + (soLoi ? ", bỏ qua " + soLoi + " dòng lỗi." : ".")
        : (soLoi ? "Không có dòng hợp lệ nào. Sửa " + soLoi + " dòng lỗi dưới đây rồi chọn lại tệp." : "Tệp chưa có dòng dữ liệu nào (chỉ có hàng tiêu đề).");
      const loi = TRANG_XL.filter(([k]) => xt[k].loi.length).map(([k, tenTrang]) => {
        const ds = xt[k].loi;
        return h("details.dk-excel-loi", { open: true, "data-trang": k }, h("summary", {}, "Trang «" + tenTrang + "»: " + ds.length + " dòng lỗi (bị bỏ qua)"),
          DK.bang(["Dòng", "Lý do"], ds.slice(0, TOI_DA_LOI_HIEN).map((e) => [String(e.dong), DK.loiChu([{ code: e.ly_do, params: e.params }])])),
          ds.length > TOI_DA_LOI_HIEN ? h("p.dk-phu", {}, "…và " + (ds.length - TOI_DA_LOI_HIEN) + " dòng lỗi nữa.") : null);
      });
      xem.replaceChildren(h("p#dkExcelTomTat.dk-excel-tomtat", {}, chu), DK.bang(["Trang", "Hợp lệ", "Mới", "Đã có", "Dòng lỗi"], hang),
        h("p.dk-phu", {}, "«Đã có»: học sinh được cập nhật và giữ nguyên PIN; giáo viên và phòng đã có thì bỏ qua."), ...loi);
    };
    const chon = async (f) => {
      tep = xt = null; nap.disabled = true; pin.replaceChildren(); xem.replaceChildren();
      if (!f) { ten.textContent = "Chưa chọn tệp."; return; }
      ten.textContent = f.name;
      if (!/\.xlsx$/i.test(f.name)) return loiChu("dk_excel_khong_phai_xlsx");
      if (f.size > TOI_DA_MB * 1048576) return loiChu("dk_excel_qua_lon", { max_mb: TOI_DA_MB });
      let b64;
      try { b64 = await doc(f); } catch (e) { return loiChu("dk_excel_khong_phai_xlsx"); }
      const r = await DK.chay(null, () => DK.goi("dk_excel_xem_truoc", T(), b64, f.name, khoa));
      if (!r.ok) return;
      DK.thongBao("");
      tep = { ten: f.name, b64 }; xt = r.data; ve(); nap.disabled = !xt.co_the_nap;
    };
    const napDi = async () => {
      const r = await DK.goi("dk_excel_nap", T(), tep.b64, tep.ten, khoa);
      if (!r.ok) return r;
      const d = r.data, hs = d.hoc_sinh, gv = d.giao_vien;
      const ds = hs.pin.map((x) => ({ ma: x.ma, ten: x.ten, lop: x.lop, pin: x.pin })).concat(gv.pin.map((x) => ({ ma: x.ma, ten: x.ten, pin: x.pin, vai: "gv" })));
      pin.replaceChildren(ds.length ? QT2.phieuPin(ds, "Mã PIN vừa tạo (chỉ hiện lúc này)", "hs") : h("p.dk-phu", {}, "Không có tài khoản mới nên không có PIN mới."));
      DK.thongBao("Đã nạp: học sinh mới " + hs.moi + " (cập nhật " + hs.da_co + "), giáo viên mới " + gv.moi + ", phòng mới " + d.phong.moi + "." + (d.loi.length ? " Bỏ qua " + d.loi.length + " dòng lỗi." : ""));
      tep = xt = null; xem.replaceChildren(); ten.textContent = "Đã nạp. Chọn tệp khác để nạp tiếp.";
      return r;
    };
    const mau = DK.nut("Tải file mẫu", function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_excel_mau", T()); if (!r.ok) return r;
      const bin = global.atob(r.data.file_base64), u8 = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
      const url = global.URL.createObjectURL(new global.Blob([u8], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }));
      const a = h("a", { href: url, download: r.data.ten_tep }); document.body.append(a); a.click(); a.remove();
      global.setTimeout(() => global.URL.revokeObjectURL(url), 2000);
      DK.thongBao("Đã tải " + r.data.ten_tep + "."); return r; }); }, { id: "dkExcelMau" });
    const inp = h("input#dkExcelTep", { type: "file", accept: ".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", hidden: true,
      onchange: () => { const f = inp.files[0]; inp.value = ""; chon(f); } });
    const tha = h("div#dkExcelTha.dk-tha", { role: "group", "aria-label": "Thả tệp Excel vào đây" },
      h("span.dk-tha-chu", {}, "Kéo tệp .xlsx vào đây, hoặc"), DK.nut("Chọn tệp .xlsx", () => inp.click(), { id: "dkExcelChon" }), inp);
    ["dragenter", "dragover"].forEach((ev) => tha.addEventListener(ev, (e) => { e.preventDefault(); tha.classList.add("keo"); }));
    ["dragleave", "drop"].forEach((ev) => tha.addEventListener(ev, (e) => { e.preventDefault(); tha.classList.remove("keo"); }));
    tha.addEventListener("drop", (e) => { chon(e.dataTransfer && e.dataTransfer.files[0]); });
    return h("section#dkExcel.dk-khung", {}, h("h3", {}, "Nạp từ Excel"),
      h("p.dk-phu", {}, "Một tệp .xlsx có ba trang: «Học sinh» (Mã HS, Họ tên, Lớp), «Giáo viên» (Họ tên), «Phòng» (Tên phòng, Sức chứa). Khối suy từ lớp. Nạp lại tệp đã sửa được: học sinh cũ giữ nguyên PIN."),
      khoa ? h("p.dk-phu#dkExcelKhoa", {}, "Học sinh đã bắt đầu đăng ký nên trang «Học sinh» không được nạp.") : null,
      h("div.dk-hang-nut", {}, mau), tha, ten, xem, nap, pin);
  };

  /* ---------- A9: thẻ Cài đặt ---------- */
  QT2.caiDat = async function () {
    const c = (await DK.goi("dk_cai_dat_doc", T())).data || {};
    const sua = c.giai_doan === "chuan_bi";
    const ma = DK.truong("Mã trường (GV tự đăng ký)", "ma_truong", { value: c.ma_truong || "" });
    const luuMa = DK.nut("Lưu mã", function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_cai_dat_doi", T(), ma.querySelector("input").value, null, null); if (r.ok) { DK.thongBao("Đã lưu mã trường."); } return r; }); }, { id: "dkLuuMa" });
    const buoi = DK.truong("Các buổi, cách nhau dấu phẩy", "buoi", { value: (c.buoi || []).join(", "), disabled: !sua });
    const khoi = DK.truong("Khối từ – đến", "khoi", { value: (c.khoi || []).join(" - "), disabled: !sua });
    const luuBk = DK.nut("Lưu buổi và khối", function () { DK.chay(this, async () => {
      const b = buoi.querySelector("input").value.split(",").map((x) => x.trim()).filter(Boolean);
      const k = khoi.querySelector("input").value.split(/[-–,\s]+/).filter(Boolean).map(Number);
      const r = await DK.goi("dk_cai_dat_doi", T(), null, b, k); if (r.ok) { DK.thongBao("Đã lưu buổi và khối."); lamMoi(); } return r; }); }, { id: "dkLuuBuoiKhoi" });
    const nv = DK.truong("Số nguyện vọng tối đa mỗi buổi", "toi_da_nv", { type: "number", min: "1", max: "30", value: c.toi_da_nv });
    const thi = DK.truong("Số bài thi tối đa mỗi buổi", "toi_da_thi", { type: "number", min: "1", max: "30", value: c.toi_da_thi });
    const luuGh = DK.nut("Lưu giới hạn", function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_dat_gioi_han", T(), nv.querySelector("input").value, thi.querySelector("input").value); if (r.ok) DK.thongBao("Đã lưu giới hạn."); return r; }); }, { id: "dkLuuGh" });
    /* DK6-L2: đổi mật khẩu quản trị. Nhập lại phải khớp (kiểm ở máy); mật khẩu cũ do máy chủ kiểm (`dk_mat_khau_cu_sai`). */
    const mkCu = DK.truong("Mật khẩu hiện tại", "mk_cu", { type: "password", autocomplete: "current-password" });
    const mkMoi = DK.truong("Mật khẩu mới (ít nhất 4 ký tự)", "mk_moi", { type: "password", autocomplete: "new-password" });
    const mkLai = DK.truong("Nhập lại mật khẩu mới", "mk_lai", { type: "password", autocomplete: "new-password" });
    const doiMk = DK.nut("Đổi mật khẩu", function () { DK.chay(this, async () => {
      const cu = mkCu.querySelector("input"), moi = mkMoi.querySelector("input"), lai = mkLai.querySelector("input");
      if (moi.value !== lai.value) return { ok: false, errors: ["Hai lần nhập mật khẩu mới không giống nhau."] };       // DK8-L5: là lỗi nhập, không phải «xong»
      const r = await DK.goi("dk_doi_mat_khau", T(), cu.value, moi.value);
      if (r.ok) { cu.value = moi.value = lai.value = ""; chupO(); DK.thongBao("Đã đổi mật khẩu. Các máy quản trị khác phải đăng nhập lại."); } return r; }); }, { id: "dkDoiMk" });
    return h("div", {}, h("div.dk-luoi2", {},
      DK.theCon("Mã trường", h("p.dk-phu", {}, "Giáo viên nhập mã này khi tự tạo tài khoản. Đổi mã nếu bị lộ."), ma, luuMa),
      DK.theCon("Buổi và khối", sua ? h("p.dk-phu", {}, "Chỉ đổi được ở giai đoạn Chuẩn bị, khi chưa có CLB.") : h("p.dk-phu", {}, "Đã khoá: giáo viên đã đăng ký xong."), buoi, khoi, sua ? luuBk : null),
      DK.theCon("Giới hạn cho học sinh", nv, thi, luuGh),
      DK.theCon("Đổi mật khẩu quản trị", h("p.dk-phu", {}, "Mật khẩu mới có hiệu lực ngay; các máy quản trị khác bị đăng xuất."), mkCu, mkMoi, mkLai, doiMk)),
      QT2.napExcel(c),
      h("p.dk-phu", {}, "Quản trị tự khoá sau 2 phút không thao tác. Số lần đã xuất Sổ nhập: " + (c.so_lan_xuat || 0) + "."));
  };

  /* ---------- A10: xem trước bản xuất ---------- */
  QT2.xemTruoc = async function (x0) {
    const x = x0 || (await DK.goi("dk_xuat_xem_truoc", T())).data || { clb: [], hoc_sinh: [], tong_hoc_sinh: 0, so_lan_xuat: 0 };
    return h("details#dkXemTruoc", { open: true }, h("summary", {}, "Xem trước Sổ nhập (" + x.clb.length + " CLB, " + x.tong_hoc_sinh + " học sinh)"),
      h("p.dk-phu", {}, "Đã xuất " + x.so_lan_xuat + " lần. Mỗi lần xuất là một phiên bản mới."),
      h("h3", {}, "1. CLB"), DK.bang(["Tên", "Buổi", "Loại", "Chỉ tiêu", "Điểm sàn", "Mã", "Phòng", "Sức chứa phòng"], x.clb.map((r) => r.map((v) => (v === null ? "" : v)))),
      h("h3", {}, "2. Học sinh"), DK.bang(["Mã", "Họ tên", "Lớp", "Nguyện vọng"], x.hoc_sinh),
      x.tong_hoc_sinh > x.hoc_sinh.length ? h("p.dk-phu", {}, "Hiện " + x.hoc_sinh.length + " em đầu.") : null);
  };

  /* ---------- A11: sao lưu ---------- */
  QT2.saoLuu = async function () {
    const c = (await DK.goi("dk_cai_dat_doc", T())).data || {};
    const phut = c.sao_luu_luc ? (Date.now() - new Date(c.sao_luu_luc).getTime()) / 60000 : null;
    const kq = h("p#dkSaoLuuKq.dk-phu", {}, phut === null || phut > 60 ? "Chưa sao lưu trong 60 phút qua." : "Sao lưu lúc " + c.sao_luu_luc.replace("T", " ") + ".");
    const nut = DK.nut("Sao lưu ngay", function () { DK.chay(this, async () => {
      const r = await DK.goi("dk_sao_luu", T()); if (r.ok) kq.textContent = "Đã tạo bản sao lưu lúc " + r.data.luc.replace("T", " ") + "."; return r; }); }, { id: "dkSaoLuu" });
    return DK.theCon("Sao lưu", h("p.dk-phu", {}, "Sao lưu để không mất dữ liệu khi máy hỏng hoặc mất điện."), nut, kq);
  };
  /* DKL-M: tự cập nhật trong vài giây. Mỗi 5 giây hỏi `dk_dau_van_tay` (công khai, rẻ, KHÔNG làm mới giờ nghỉ của phiên); chỉ vẽ
     lại khi dấu đổi — không có thay đổi thì không tải lại gì. Vẽ lại bằng `DK.quanTri(true)`: không tính là thao tác, không đặt lại
     đồng hồ nghỉ của máy khách.
     DKL-N (checker vòng 2): KHÔNG vẽ lại khi có thứ sẽ mất — (1) phiếu PIN vừa tạo (chỉ hiện một lần, `#dkPin` còn nội dung);
     (2) chữ đã gõ chưa lưu ở bất kỳ ô nhập nào (so với giá trị lúc vẽ), kể cả khi con trỏ đã rời ô; (3) ô nhập đang focus; (4) hộp
     xác nhận đang mở. Dấu cũ được giữ nên vòng sau thử lại; sạch rồi thì vẽ lại bình thường.
     Dấu vân tay = thời điểm sửa + kích thước của app.db (chế độ nhật ký DELETE, không phải WAL). */
  const CHU_KY_LAM_MOI_MS = 5000;
  let dongHo = null, dauCu = null, dauCho = null;
  const layDau = async () => { const r = await global.RBDA.callApi("dk_dau_van_tay"); return r && r.ok ? r.data.dau : null; };
  const cacO = () => document.querySelectorAll(".dk-noidung input, .dk-noidung textarea, .dk-noidung select");
  const chupO = () => cacO().forEach((e) => { e.dataset.v0 = e.value; });          // giá trị lúc vừa vẽ xong
  const coThuSeMat = () => {
    const pin = document.getElementById("dkPin");
    if (pin && pin.childElementCount > 0) return true;                              // phiếu PIN chỉ hiện một lần
    const e = document.activeElement;
    if (e && /^(INPUT|TEXTAREA|SELECT)$/.test(e.tagName)) return true;              // đang ở trong ô nhập
    const hop = document.getElementById("dkThayHop");
    if (hop && !hop.hidden) return true;                                            // hộp xác nhận đang mở
    return Array.from(cacO()).some((x) => x.dataset.v0 !== undefined && x.value !== x.dataset.v0);   // chữ chưa lưu
  };
  QT2.tuLamMoi = function (bat, giuDau) {
    clearInterval(dongHo); dongHo = null;
    if (!bat) { if (!giuDau) dauCho = null; return; }                                           // vẽ lại thủ công / rời màn: bỏ dấu đang chờ
    chupO();
    if (dauCho !== null) { dauCu = dauCho; dauCho = null; }                         // vẽ lại do chính vòng hỏi: dùng dấu ĐÃ thấy, không đọc lại (tránh bỏ sót thay đổi xen giữa)
    else layDau().then((d) => { dauCu = d; });
    dongHo = setInterval(async () => {
      if (DK.S.vai !== "quan_tri") { clearInterval(dongHo); dongHo = null; return; }
      if (coThuSeMat()) return;
      const d = await layDau();
      if (!d || d === dauCu) return;
      dauCho = d;
      DK.quanTri(true);
    }, CHU_KY_LAM_MOI_MS);
  };
})(window);
