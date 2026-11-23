/* ==========================================================================
   16_tai_khoan.js — GT3-L1: đăng nhập + tài khoản (hai vai: quản trị, giáo viên).

   - Chưa có tài khoản nào: KHÔNG có màn đăng nhập; chỉ có nút "Tài khoản" ở thanh bên để tạo tài khoản
     quản trị đầu tiên (bật tính năng).
   - Có tài khoản mà chưa đăng nhập (hoặc phiên hết 15 phút không hoạt động): màn đăng nhập chắn cả giao diện.
   - Đã đăng nhập: thanh bên hiện tên + vai + nút Đăng xuất; hộp "Tài khoản" cho đổi mật khẩu, và (quản trị) tạo / xoá tài khoản.
   Mật khẩu chỉ nằm trong ô nhập, gửi đi một lần, xoá khỏi ô ngay sau đó; không lưu ở đâu trong trang.
   Backend: api_tai_khoan.py. Mọi chuỗi qua t() (khoá tk_*).
   ========================================================================== */
"use strict";

(() => {
  const CHU_KY_HOI_PHIEN_MS = 30000;
  let phien = null;            // data của get_phien_dang_nhap
  let dangMoHop = false;       // hộp "Tài khoản" (đóng được) đang mở
  let theHienTai = "tk";       // GT4-L6: thẻ đang mở của hộp (tk | nk); giữ khi hộp được vẽ lại vì đổi ngôn ngữ
  let vuaTaoDau = false;       // GT4-L3: vừa tạo tài khoản quản trị đầu tiên: hộp mở lại với thẻ "Bước tiếp theo"

  function mot(tag, thuocTinh, ...con) {
    const e = document.createElement(tag);
    Object.entries(thuocTinh || {}).forEach(([k, v]) => {
      if (v === null || v === undefined || v === false) return;
      if (k === "class") e.className = v;
      else if (k === "text") e.textContent = v;
      else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? "" : v);
    });
    con.forEach((c) => c && e.appendChild(typeof c === "string" ? document.createTextNode(c) : c));
    return e;
  }

  function tenVai(vai) {
    return t(vai === "quan_tri" ? "tk_vai_quan_tri" : "tk_vai_giao_vien");
  }

  function oNhap(id, nhan, loai, tuDong) {
    const o = mot("input", { id, type: loai || "text", class: "text-input", autocomplete: tuDong || "off", spellcheck: "false" });
    return { o, nhom: mot("label", { class: "ws-sua-nhan", for: id, style: "display:block;margin:8px 0 2px" }, nhan) };
  }

  /* GT4-L3: ô mật khẩu + ô nhập lại + ô tích "Hiện mật khẩu" (đổi loại cả hai ô). */
  function oMatKhauKep(idMk, nhanMk, tuDong, idHien) {
    const mk = oNhap(idMk, nhanMk, "password", tuDong);
    const mk2 = oNhap(idMk + "2", t("tk_nhap_lai_mk"), "password", tuDong);
    const hien = mot("input", { type: "checkbox", id: idHien });
    hien.addEventListener("change", () => {
      mk.o.type = hien.checked ? "text" : "password";
      mk2.o.type = hien.checked ? "text" : "password";
    });
    const nhomHien = mot("label", { for: idHien, style: "display:block;margin:6px 0 0" }, hien, " " + t("tk_hien_mk"));
    return { mk, mk2, cacPhanTu: [mk.nhom, mk.o, mk2.nhom, mk2.o, nhomHien] };
  }

  function lopPhu() {
    let o = el("tkOverlay");
    if (!o) {
      o = mot("div", { class: "ws-overlay gt-ui", id: "tkOverlay", hidden: true, style: "z-index:120" });
      document.body.appendChild(o);
    }
    return o;
  }

  function dongLopPhu() {
    const o = lopPhu();
    o.hidden = true;
    o.textContent = "";
    o.classList.remove("tk-kin");
    dangMoHop = false;
  }

  /* ------------------------------------------------------------ màn đăng nhập */
  function veManDangNhap(thongBao) {
    const o = lopPhu();
    o.textContent = "";
    o.hidden = false;
    o.classList.add("tk-kin");      // GT4 fix OL1: đăng nhập/đăng xuất thì che kín màn phía sau (tên, mã, CLB học sinh)
    dangMoHop = false;
    const tieuDe = mot("h2", { class: "ws-tieu-de", id: "tkTieuDe", tabindex: "-1", text: t("tk_dang_nhap_tieu_de") });
    const ten = oNhap("tkTen", t("tk_ten"), "text", "username");
    const mk = oNhap("tkMatKhau", t("tk_mat_khau"), "password", "current-password");
    const tin = mot("div", { class: "save-feedback", id: "tkTin", role: "alert" });
    const gui = mot("button", { type: "submit", class: "btn btn-primary", id: "tkNutDangNhap", text: t("tk_nut_dang_nhap") });
    const form = mot("form", {}, ten.nhom, ten.o, mk.nhom, mk.o, mot("div", { style: "margin-top:14px" }, gui), tin);
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const tenGui = ten.o.value, mkGui = mk.o.value;
      mk.o.value = "";
      chayNut(gui, () => callApi("dang_nhap", tenGui, mkGui), (res) => {
        if (!res.ok) { feedbackErrors(tin, res.errors); mk.o.focus(); return; }
        dongLopPhu();
        capNhat();
        taiLaiGiaoDien();
      });
    });
    const hop = mot("div", { class: "ws-hop", role: "dialog", "aria-modal": "true", "aria-labelledby": "tkTieuDe", style: "max-width:420px" },
      tieuDe, thongBao ? mot("p", { class: "hint-text", text: thongBao }) : null, form);
    o.appendChild(hop);
    ten.o.focus();
  }

  /* Sau khi vào được: kéo lại dữ liệu mà màn đăng nhập từng chặn (các thẻ đã tải trước đó vẫn nguyên). */
  function taiLaiGiaoDien() {
    if (typeof loadPipelineTab === "function") loadPipelineTab();
  }

  /* ------------------------------------------------------------ hộp "Tài khoản" */
  function veHop() {
    const o = lopPhu();
    o.textContent = "";
    o.hidden = false;
    o.classList.remove("tk-kin");
    dangMoHop = true;
    const hop = mot("div", { class: "ws-hop", role: "dialog", "aria-modal": "true", "aria-labelledby": "tkTieuDe", style: "max-width:560px" });
    hop.appendChild(mot("h2", { class: "ws-tieu-de", id: "tkTieuDe", tabindex: "-1", text: t("tk_tieu_de_quan_ly") }));
    const vuaTaoQuanTriDau = vuaTaoDau;
    vuaTaoDau = false;
    if (!phien.co_tai_khoan) veTaoDauTien(hop);
    else if (phien.dang_nhap) {
      if (phien.vai === "quan_tri") {
        /* GT4-L6: nhật ký ở thẻ riêng (hộp tài khoản giữ ngắn): hai thẻ "Tài khoản" | "Nhật ký thao tác". */
        const khungTk = mot("div", { id: "tkKhungTaiKhoan", role: "tabpanel" });
        const khungNk = mot("div", { id: "tkKhungNhatKy", role: "tabpanel", hidden: true });
        const nutTk = mot("button", { type: "button", class: "btn btn-secondary", id: "tkTabTaiKhoan", role: "tab",
          "aria-selected": "true", text: t("tk_tab_tai_khoan") });
        const nutNk = mot("button", { type: "button", class: "btn btn-secondary", id: "tkTabNhatKy", role: "tab",
          "aria-selected": "false", text: t("tk_tab_nhat_ky") });
        let daVeNk = false;
        const chon = (nhat) => {
          theHienTai = nhat ? "nk" : "tk";
          khungTk.hidden = nhat; khungNk.hidden = !nhat;
          hop.style.maxWidth = nhat ? "min(960px, 92vw)" : "560px";     // GT4: bảng nhật ký cần rộng hơn
          nutTk.setAttribute("aria-selected", nhat ? "false" : "true");
          nutNk.setAttribute("aria-selected", nhat ? "true" : "false");
          if (nhat && !daVeNk) { daVeNk = true; veNhatKy(khungNk); }
        };
        nutTk.addEventListener("click", () => chon(false));
        nutNk.addEventListener("click", () => chon(true));
        hop.appendChild(mot("div", { role: "tablist", style: "display:flex;gap:8px;margin:8px 0 12px" }, nutTk, nutNk));
        if (vuaTaoQuanTriDau) khungTk.appendChild(veBuocTiep());
        veDanhSach(khungTk);      // GT4: danh sách + "Thêm tài khoản" lên trước, "Đổi mật khẩu" xuống cuối (hộp bớt dài)
        veDoiMatKhau(khungTk);
        hop.append(khungTk, khungNk);
        if (theHienTai === "nk" && !vuaTaoQuanTriDau) chon(true);
      } else {
        veDoiMatKhau(hop);
      }
    }
    hop.appendChild(mot("div", { style: "margin-top:18px" },
      mot("button", { type: "button", class: "btn btn-secondary", id: "tkNutDong", text: t("tk_dong"), onclick: dongLopPhu })));
    o.appendChild(hop);
    const oTen = vuaTaoQuanTriDau ? el("tkTaoTen") : null;   // GT4-L3: sau quản trị đầu tiên, con trỏ ở "Thêm tài khoản"
    if (oTen) oTen.focus();
    else hop.querySelector("input") ? hop.querySelector("input").focus() : el("tkTieuDe").focus();
  }

  /* GT4-L3: ba việc nên làm ngay sau khi tạo quản trị đầu tiên. */
  function veBuocTiep() {
    return mot("div", { id: "tkBuocTiep", class: "hint-text", role: "status", style: "margin:8px 0 12px" },
      mot("h3", { text: t("tk_buoc_tiep_tieu_de") }),
      mot("ol", {}, mot("li", { text: t("tk_buoc_tiep_1") }), mot("li", { text: t("tk_buoc_tiep_2") }),
        mot("li", { text: t("tk_buoc_tiep_3") })));
  }

  function veTaoDauTien(hop) {
    hop.appendChild(mot("p", { class: "hint-text", text: t("tk_tao_dau_tien_ghi") }));
    hop.appendChild(mot("p", { class: "hint-text", id: "tkCanhBaoDauTien", role: "note", style: "font-weight:600",
      text: t("tk_canh_bao_dau_tien") }));
    hop.appendChild(veFormTao("quan_tri", true));
  }

  function veFormTao(vaiCoDinh, laDauTien) {
    const ten = oNhap("tkTaoTen", t("tk_ten"), "text", "off");
    const kep = oMatKhauKep("tkTaoMk", t("tk_mk_moi"), "new-password", "tkTaoHien");
    const mk = kep.mk, mk2 = kep.mk2;
    const vai = mot("select", { id: "tkTaoVai", class: "text-input" },
      mot("option", { value: "giao_vien", text: t("tk_vai_giao_vien") }),
      mot("option", { value: "quan_tri", text: t("tk_vai_quan_tri") }));
    const tin = mot("div", { class: "save-feedback", id: "tkTaoTin", role: "alert" });
    const nut = mot("button", { type: "submit", class: "btn btn-primary", id: "tkNutTao", text: t("tk_tao_nut") });
    const form = mot("form", { id: "tkFormTao", style: "margin-top:8px" }, ten.nhom, ten.o, ...kep.cacPhanTu);
    if (!vaiCoDinh) form.append(mot("label", { class: "ws-sua-nhan", for: "tkTaoVai", style: "display:block;margin:8px 0 2px", text: t("tk_vai") }), vai);
    form.append(mot("div", { style: "margin-top:12px" }, nut), tin);
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const tenGui = ten.o.value, mkGui = mk.o.value, vaiGui = vaiCoDinh || vai.value;
      if (mkGui !== mk2.o.value) { feedback(tin, t("tk_mk_khong_khop"), true); mk2.o.focus(); return; }   // GT4-L3
      mk.o.value = ""; mk2.o.value = "";
      chayNut(nut, () => callApi("tao_tai_khoan", tenGui, mkGui, vaiGui), (res) => {
        if (!res.ok) { feedbackErrors(tin, res.errors); return; }
        showToast(t("tk_da_tao", { ten: res.data.ten }), "success");
        if (laDauTien) vuaTaoDau = true;
        capNhat().then(() => { if (dangMoHop) veHop(); });
      });
    });
    return form;
  }

  function veDoiMatKhau(hop) {
    hop.appendChild(mot("p", { class: "hint-text", text: t("tk_dang_la", { ten: phien.ten, vai: tenVai(phien.vai) }), title: t("tk_dang_la", { ten: phien.ten, vai: tenVai(phien.vai) }) }));
    const cu = oNhap("tkMkCu", t("tk_mk_cu"), "password", "current-password");
    const kep = oMatKhauKep("tkMkMoi", t("tk_mk_moi"), "new-password", "tkMkHien");
    const moi = kep.mk, moi2 = kep.mk2;
    const tin = mot("div", { class: "save-feedback", id: "tkDoiTin", role: "alert" });
    const nut = mot("button", { type: "submit", class: "btn btn-secondary", id: "tkNutDoiMk", text: t("tk_doi_mk_nut") });
    const form = mot("form", { id: "tkFormDoiMk" }, mot("h3", { text: t("tk_doi_mk_tieu_de") }), cu.nhom, cu.o, ...kep.cacPhanTu,
      mot("div", { style: "margin-top:12px" }, nut), tin);
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const cuGui = cu.o.value, moiGui = moi.o.value;
      if (moiGui !== moi2.o.value) { feedback(tin, t("tk_mk_khong_khop"), true); moi2.o.focus(); return; }   // GT4-L3
      cu.o.value = ""; moi.o.value = ""; moi2.o.value = "";
      chayNut(nut, () => callApi("doi_mat_khau", cuGui, moiGui), (res) => {
        if (!res.ok) { feedbackErrors(tin, res.errors); return; }
        feedback(tin, t("tk_da_doi"), false);
      });
    });
    hop.appendChild(form);
  }

  function veDanhSach(hop) {
    const khung = mot("div", { style: "margin-top:20px" }, mot("h3", { text: t("tk_ds_tieu_de") }));
    const bang = mot("div", { id: "tkDanhSach" });
    khung.appendChild(bang);
    khung.appendChild(mot("h3", { style: "margin-top:16px", text: t("tk_tao_tieu_de") }));
    khung.appendChild(veFormTao(null, false));
    hop.appendChild(khung);
    callApi("liet_ke_tai_khoan").then((res) => {
      if (!res.ok) { showErrorToast(res.errors); return; }
      res.data.forEach((tk) => {
        const nutXoa = mot("button", { type: "button", class: "btn btn-secondary", "data-xoa": tk.ten, text: t("tk_xoa") });
        let daBam = false;
        nutXoa.addEventListener("click", () => {
          if (!daBam) { daBam = true; nutXoa.textContent = t("tk_xoa_xac_nhan"); return; }
          chayNut(nutXoa, () => callApi("xoa_tai_khoan", tk.ten), (r) => {
            if (!r.ok) { showErrorToast(r.errors); daBam = false; nutXoa.textContent = t("tk_xoa"); return; }
            showToast(t("tk_da_xoa"), "success");
            capNhat().then(() => { if (!phien.dang_nhap) veManDangNhap(); else if (dangMoHop) veHop(); });
          });
        });
        bang.appendChild(mot("div", { class: "ws-sua-hop", style: "margin:4px 0" },
          mot("span", { text: tk.ten + " — " + tenVai(tk.vai) }), nutXoa));
      });
    });
  }

  /* ------------------------------------------------------------ nhật ký thao tác (GT3-L3, chỉ quản trị) */
  /* GT4-L6: chỉ là cách HIỆN. Tên hành động, vai, mã kết quả và khoá chi tiết đi qua từ điển trong i18n.js
     (nkhd_*, nkvai_*, nkkq_*, nkkey_*); không có trong từ điển thì giữ nguyên chữ gốc. CSV xuất vẫn là dạng thô. */
  function nhanNk(tienTo, goc) {
    if (goc === null || goc === undefined || goc === "") return "";
    const k = tienTo + goc;
    const v = t(k);
    return v === k ? String(goc) : v;
  }

  function gioDiaPhuong(luc) {
    const m = /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/.exec(String(luc || ""));
    return m ? m[3] + "/" + m[2] + "/" + m[1] + " " + m[4] + ":" + m[5] : String(luc || "");
  }

  function chiTietNk(raw) {
    if (!raw) return "";
    let o;
    try { o = JSON.parse(raw); } catch (e) { return String(raw); }
    if (o === null || typeof o !== "object" || Array.isArray(o)) return String(raw);
    return Object.keys(o).map((k) => {
      const v = o[k];
      const chu = v !== null && typeof v === "object" ? JSON.stringify(v) : String(v);
      return nhanNk("nkkey_", k) + ": " + (k === "vai" ? nhanNk("nkvai_", v) : chu);   // GT4: "Quản trị", không "quan_tri"
    }).join("; ");
  }

  function veNhatKy(hop) {
    const trang = { so: 1, nguoi: "", hanhDong: "", tuChoi: false, ngay: "" };
    const khung = mot("div", { style: "margin-top:12px", id: "tkNhatKy" }, mot("h3", { text: t("tk_nk_tieu_de") }),
      mot("p", { class: "hint-text", text: t("tk_nk_ghi_chu") }));
    const locNguoi = oNhap("tkNkNguoi", t("tk_nk_loc_nguoi"), "text");
    const chonHd = mot("select", { id: "tkNkHanhDong", class: "text-input" });
    const nhanHd = mot("label", { class: "ws-sua-nhan", for: "tkNkHanhDong", style: "display:block;margin:8px 0 2px",
      text: t("tk_nk_loc_hanh_dong") });
    const locNgay = oNhap("tkNkNgay", t("tk_nk_loc_ngay"), "date");
    const oTuChoi = mot("input", { type: "checkbox", id: "tkNkTuChoi" });
    const nhanTuChoi = mot("label", { for: "tkNkTuChoi", style: "display:block;margin:8px 0" }, oTuChoi, " " + t("tk_nk_chi_tu_choi"));
    const nutLoc = mot("button", { type: "button", class: "btn btn-secondary", id: "tkNkLoc", text: t("tk_nk_loc_nut") });
    const nutXuat = mot("button", { type: "button", class: "btn btn-secondary", id: "tkNkXuat", text: t("tk_nk_xuat") });
    const bang = mot("div", { id: "tkNkBang" });
    const nutTruoc = mot("button", { type: "button", class: "btn btn-secondary", id: "tkNkTruoc", text: t("tk_nk_truoc") });
    const nutSau = mot("button", { type: "button", class: "btn btn-secondary", id: "tkNkSau", text: t("tk_nk_sau") });
    const nhan = mot("span", { id: "tkNkTrang", class: "hint-text", style: "margin:0 8px" });
    khung.append(mot("div", { class: "nk-loc" },
      mot("div", { class: "nk-loc-o" }, locNguoi.nhom, locNguoi.o),
      mot("div", { class: "nk-loc-o" }, nhanHd, chonHd),
      mot("div", { class: "nk-loc-o" }, locNgay.nhom, locNgay.o)), nhanTuChoi,
      mot("div", { style: "margin:8px 0" }, nutLoc, " ", nutXuat), bang,
      mot("div", { style: "margin-top:8px" }, nutTruoc, nhan, nutSau));
    hop.appendChild(khung);
    let dsHd = null;       // các tên hành động đã nạp vào ô chọn (nạp lại khi ngôn ngữ đổi)
    let dongCuoi = null;

    function napOChon(co) {
      dsHd = co;
      const dang = trang.hanhDong;
      chonHd.textContent = "";
      chonHd.appendChild(mot("option", { value: "", text: t("tk_nk_tat_ca_hanh_dong") }));
      const muc = co.map((k) => [k, nhanNk("nkhd_", k)]).sort((a, b) => a[1].localeCompare(b[1], window.I18N.getLang()));
      muc.forEach(([k, nhanK]) => chonHd.appendChild(mot("option", { value: k, text: nhanK })));
      chonHd.value = dang;
    }

    function veBang(d) {
      bang.textContent = "";
      if (!d.dong.length) bang.appendChild(mot("p", { class: "hint-text", text: t("tk_nk_trong") }));
      else {
        const cot = [["luc", "tk_nk_cot_luc"], ["nguoi", "tk_nk_cot_nguoi"], ["vai", "tk_nk_cot_vai"],
          ["hanh_dong", "tk_nk_cot_hanh_dong"], ["ket_qua", "tk_nk_cot_ket_qua"], ["chi_tiet", "tk_nk_cot_chi_tiet"]];
        const gtri = (r, c) => {
          if (c === "luc") return gioDiaPhuong(r.luc);
          if (c === "nguoi") return r.nguoi == null ? (r.hanh_dong === "tra_cuu_hoc_sinh" ? t("nk_hoc_sinh_tu_tra_cuu") : "") : r.nguoi;
          if (c === "vai") return nhanNk("nkvai_", r.vai);
          if (c === "hanh_dong") return nhanNk("nkhd_", r.hanh_dong);
          if (c === "ket_qua") return nhanNk("nkkq_", r.ket_qua);
          return chiTietNk(r.chi_tiet);
        };
        const tb = mot("table", { class: "data-table", id: "tkNkTable" },
          mot("thead", {}, mot("tr", {}, ...cot.map(([, k]) => mot("th", { text: t(k) })))),
          mot("tbody", {}, ...d.dong.map((r) => mot("tr", {}, ...cot.map(([c]) => mot("td", { text: gtri(r, c) }))))));
        bang.appendChild(mot("div", { style: "overflow-x:auto" }, tb));
      }
      nhan.textContent = t("tk_nk_trang", { trang: d.page, so_trang: d.so_trang, tong: d.tong });
      nutTruoc.disabled = d.page <= 1;
      nutSau.disabled = d.page >= d.so_trang;
    }

    function ve() {
      callApi("get_nhat_ky_thao_tac", trang.so, 20, trang.nguoi || null, trang.hanhDong || null, trang.tuChoi,
        trang.ngay || null).then((res) => {
        if (!res.ok) { showErrorToast(res.errors); return; }
        const d = res.data;
        if (dsHd === null || d.hanh_dong_co.join("|") !== dsHd.join("|")) napOChon(d.hanh_dong_co);
        dongCuoi = d;
        veBang(d);
      });
    }
    function docLoc() {
      trang.so = 1; trang.nguoi = locNguoi.o.value.trim(); trang.hanhDong = chonHd.value;
      trang.tuChoi = oTuChoi.checked; trang.ngay = locNgay.o.value;
    }
    nutLoc.addEventListener("click", () => { docLoc(); ve(); });
    nutTruoc.addEventListener("click", () => { if (trang.so > 1) { trang.so -= 1; ve(); } });
    nutSau.addEventListener("click", () => { trang.so += 1; ve(); });
    nutXuat.addEventListener("click", () => chayNut(nutXuat,
      () => callApi("export_nhat_ky_thao_tac_csv", "", trang.nguoi || null, trang.hanhDong || null, trang.tuChoi,
        trang.ngay || null),
      (res) => { if (!res.ok) { showErrorToast(res.errors); return; } showToast(t("tk_nk_da_xuat", { n: res.data.n_rows }), "success"); }));
    window.addEventListener("langchange", () => {              // nhãn theo ngôn ngữ đang chọn: vẽ lại ô chọn và bảng
      if (!document.body.contains(khung)) return;
      if (dsHd) napOChon(dsHd);
      if (dongCuoi) veBang(dongCuoi);
    });
    ve();
  }

  /* ------------------------------------------------------------ thanh bên */
  function veThanhBen() {
    const hop = el("tkThanhBen");
    if (!hop) return;
    hop.textContent = "";
    if (phien && phien.co_tai_khoan && phien.dang_nhap) {
      hop.appendChild(mot("span", { id: "tkHuyHieu", class: "db-status", text: t("tk_dang_la", { ten: phien.ten, vai: tenVai(phien.vai) }), title: t("tk_dang_la", { ten: phien.ten, vai: tenVai(phien.vai) }) }));
      hop.appendChild(mot("button", { type: "button", class: "btn btn-secondary", id: "tkNutDangXuat", text: t("tk_dang_xuat"),
        onclick: () => callApi("dang_xuat").then(() => capNhat().then(() => veManDangNhap())) }));
    }
    hop.appendChild(mot("button", { type: "button", class: "btn btn-secondary", id: "tkNutMoHop", text: t("tk_nut_thanh_ben"),
      onclick: () => { theHienTai = "tk"; veHop(); } }));
    hop.hidden = false;
  }

  /* Hỏi phiên; vẽ lại thanh bên; bật/tắt màn đăng nhập. Trả Promise để nơi gọi nối tiếp. */
  /* GT3-L2: ghi vai hiện tại lên <body> để CSS ẩn phần của quản trị khỏi giáo viên; nếu tab đang mở bị ẩn thì chuyển sang "Kết quả". */
  function ganVai() {
    const vai = phien && phien.co_tai_khoan && phien.dang_nhap ? phien.vai : "";
    if (document.body.dataset.vai === vai) return;
    document.body.dataset.vai = vai;
    window.dispatchEvent(new Event("ux2vai")); /* UX2-L6: hop rong ve lai theo vai */
    if (vai !== "giao_vien") return;
    const dangMo = document.querySelector(".nav-item.is-active");
    if (dangMo && dangMo.dataset.quyen === "quan_tri") {
      const ketQua = document.querySelector('.nav-item[data-tab="results"]');
      if (ketQua) ketQua.click();
    }
  }

  let luotHoi = 0;
  function capNhat() {
    const luot = ++luotHoi;
    return callApi("get_phien_dang_nhap").then((res) => {
      if (luot !== luotHoi) return;   // I2: trả lời cũ (đã có lần hỏi mới hơn, ví dụ sau khi thoát chế độ học sinh) thì bỏ
      if (!res.ok) {
        if (!phien) showErrorToast(res.errors);   // lần hỏi đầu hỏng thì báo; các lần hỏi định kỳ sau không dội thông báo
        return;
      }
      const truoc = phien;
      phien = res.data;
      window.dispatchEvent(new CustomEvent("tkPhien", { detail: phien }));   // I2: js/14 mở lại lớp phủ học sinh sau khi tải lại trang
      ganVai();
      veThanhBen();
      const canDangNhap = phien.co_tai_khoan && !phien.dang_nhap;
      if (canDangNhap && !el("tkNutDangNhap")) {
        veManDangNhap(truoc && truoc.dang_nhap ? t("tk_het_phien") : null);
      } else if (!canDangNhap && el("tkNutDangNhap")) {
        dongLopPhu();
      }
    });
  }

  function initTaiKhoan() {
    capNhat();
    setInterval(capNhat, CHU_KY_HOI_PHIEN_MS);
    window.addEventListener("tkLamMoi", capNhat);     // I2: vừa thoát chế độ học sinh bằng tài khoản quản trị
    window.addEventListener("langchange", () => {
      veThanhBen();
      if (!lopPhu().hidden) { if (phien && phien.co_tai_khoan && !phien.dang_nhap) veManDangNhap(); else if (dangMoHop) veHop(); }
    });
    document.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape" && dangMoHop) dongLopPhu();
    });
  }

  window.initTaiKhoan = initTaiKhoan;
  /* ST-B-009: js/14 mở hộp tạo tài khoản quản trị đầu tiên khi "Chế độ học sinh" cần có tài khoản mới khoá được. */
  window.tkMoHopTaoDau = () => capNhat().then(() => { if (phien && !phien.co_tai_khoan) veHop(); });
})();
