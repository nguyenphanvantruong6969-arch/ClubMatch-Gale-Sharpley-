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

  function lopPhu() {
    let o = el("tkOverlay");
    if (!o) {
      o = mot("div", { class: "ws-overlay", id: "tkOverlay", hidden: true, style: "z-index:120" });
      document.body.appendChild(o);
    }
    return o;
  }

  function dongLopPhu() {
    const o = lopPhu();
    o.hidden = true;
    o.textContent = "";
    dangMoHop = false;
  }

  /* ------------------------------------------------------------ màn đăng nhập */
  function veManDangNhap(thongBao) {
    const o = lopPhu();
    o.textContent = "";
    o.hidden = false;
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
    dangMoHop = true;
    const hop = mot("div", { class: "ws-hop", role: "dialog", "aria-modal": "true", "aria-labelledby": "tkTieuDe", style: "max-width:560px" });
    hop.appendChild(mot("h2", { class: "ws-tieu-de", id: "tkTieuDe", tabindex: "-1", text: t("tk_tieu_de_quan_ly") }));
    if (!phien.co_tai_khoan) veTaoDauTien(hop);
    else if (phien.dang_nhap) {
      veDoiMatKhau(hop);
      if (phien.vai === "quan_tri") { veDanhSach(hop); veNhatKy(hop); }
    }
    hop.appendChild(mot("div", { style: "margin-top:18px" },
      mot("button", { type: "button", class: "btn btn-secondary", id: "tkNutDong", text: t("tk_dong"), onclick: dongLopPhu })));
    o.appendChild(hop);
    hop.querySelector("input") ? hop.querySelector("input").focus() : el("tkTieuDe").focus();
  }

  function veTaoDauTien(hop) {
    hop.appendChild(mot("p", { class: "hint-text", text: t("tk_tao_dau_tien_ghi") }));
    hop.appendChild(veFormTao("quan_tri", true));
  }

  function veFormTao(vaiCoDinh, laDauTien) {
    const ten = oNhap("tkTaoTen", t("tk_ten"), "text", "off");
    const mk = oNhap("tkTaoMk", t("tk_mk_moi"), "password", "new-password");
    const vai = mot("select", { id: "tkTaoVai", class: "text-input" },
      mot("option", { value: "giao_vien", text: t("tk_vai_giao_vien") }),
      mot("option", { value: "quan_tri", text: t("tk_vai_quan_tri") }));
    const tin = mot("div", { class: "save-feedback", id: "tkTaoTin", role: "alert" });
    const nut = mot("button", { type: "submit", class: "btn btn-primary", id: "tkNutTao", text: t("tk_tao_nut") });
    const form = mot("form", { id: "tkFormTao", style: "margin-top:8px" }, ten.nhom, ten.o, mk.nhom, mk.o);
    if (!vaiCoDinh) form.append(mot("label", { class: "ws-sua-nhan", for: "tkTaoVai", style: "display:block;margin:8px 0 2px", text: t("tk_vai") }), vai);
    form.append(mot("div", { style: "margin-top:12px" }, nut), tin);
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const tenGui = ten.o.value, mkGui = mk.o.value, vaiGui = vaiCoDinh || vai.value;
      mk.o.value = "";
      chayNut(nut, () => callApi("tao_tai_khoan", tenGui, mkGui, vaiGui), (res) => {
        if (!res.ok) { feedbackErrors(tin, res.errors); return; }
        showToast(t("tk_da_tao", { ten: res.data.ten }), "success");
        capNhat().then(() => { if (dangMoHop) veHop(); });
      });
    });
    return form;
  }

  function veDoiMatKhau(hop) {
    hop.appendChild(mot("p", { class: "hint-text", text: t("tk_dang_la", { ten: phien.ten, vai: tenVai(phien.vai) }) }));
    const cu = oNhap("tkMkCu", t("tk_mk_cu"), "password", "current-password");
    const moi = oNhap("tkMkMoi", t("tk_mk_moi"), "password", "new-password");
    const tin = mot("div", { class: "save-feedback", id: "tkDoiTin", role: "alert" });
    const nut = mot("button", { type: "submit", class: "btn btn-secondary", id: "tkNutDoiMk", text: t("tk_doi_mk_nut") });
    const form = mot("form", { id: "tkFormDoiMk" }, mot("h3", { text: t("tk_doi_mk_tieu_de") }), cu.nhom, cu.o, moi.nhom, moi.o,
      mot("div", { style: "margin-top:12px" }, nut), tin);
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const cuGui = cu.o.value, moiGui = moi.o.value;
      cu.o.value = ""; moi.o.value = "";
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
  function veNhatKy(hop) {
    const trang = { so: 1, nguoi: "", hanhDong: "" };
    const khung = mot("div", { style: "margin-top:24px", id: "tkNhatKy" }, mot("h3", { text: t("tk_nk_tieu_de") }),
      mot("p", { class: "hint-text", text: t("tk_nk_ghi_chu") }));
    const locNguoi = oNhap("tkNkNguoi", t("tk_nk_loc_nguoi"), "text");
    const locHd = oNhap("tkNkHanhDong", t("tk_nk_loc_hanh_dong"), "text");
    const nutLoc = mot("button", { type: "button", class: "btn btn-secondary", id: "tkNkLoc", text: t("tk_nk_loc_nut") });
    const nutXuat = mot("button", { type: "button", class: "btn btn-secondary", id: "tkNkXuat", text: t("tk_nk_xuat") });
    const bang = mot("div", { id: "tkNkBang" });
    const nutTruoc = mot("button", { type: "button", class: "btn btn-secondary", id: "tkNkTruoc", text: t("tk_nk_truoc") });
    const nutSau = mot("button", { type: "button", class: "btn btn-secondary", id: "tkNkSau", text: t("tk_nk_sau") });
    const nhan = mot("span", { id: "tkNkTrang", class: "hint-text", style: "margin:0 8px" });
    khung.append(locNguoi.nhom, locNguoi.o, locHd.nhom, locHd.o,
      mot("div", { style: "margin:8px 0" }, nutLoc, " ", nutXuat), bang,
      mot("div", { style: "margin-top:8px" }, nutTruoc, nhan, nutSau));
    hop.appendChild(khung);

    function ve() {
      callApi("get_nhat_ky_thao_tac", trang.so, 20, trang.nguoi || null, trang.hanhDong || null).then((res) => {
        if (!res.ok) { showErrorToast(res.errors); return; }
        const d = res.data;
        bang.textContent = "";
        if (!d.dong.length) bang.appendChild(mot("p", { class: "hint-text", text: t("tk_nk_trong") }));
        else {
          const cot = [["luc", "tk_nk_cot_luc"], ["nguoi", "tk_nk_cot_nguoi"], ["vai", "tk_nk_cot_vai"],
            ["hanh_dong", "tk_nk_cot_hanh_dong"], ["ket_qua", "tk_nk_cot_ket_qua"], ["chi_tiet", "tk_nk_cot_chi_tiet"]];
          const tb = mot("table", { class: "data-table", id: "tkNkTable" },
            mot("thead", {}, mot("tr", {}, ...cot.map(([, k]) => mot("th", { text: t(k) })))),
            mot("tbody", {}, ...d.dong.map((r) => mot("tr", {}, ...cot.map(([c]) => mot("td", { text: r[c] == null ? "" : String(r[c]) }))))));
          bang.appendChild(mot("div", { style: "overflow-x:auto" }, tb));
        }
        nhan.textContent = t("tk_nk_trang", { trang: d.page, so_trang: d.so_trang, tong: d.tong });
        nutTruoc.disabled = d.page <= 1;
        nutSau.disabled = d.page >= d.so_trang;
      });
    }
    nutLoc.addEventListener("click", () => { trang.so = 1; trang.nguoi = locNguoi.o.value.trim(); trang.hanhDong = locHd.o.value.trim(); ve(); });
    nutTruoc.addEventListener("click", () => { if (trang.so > 1) { trang.so -= 1; ve(); } });
    nutSau.addEventListener("click", () => { trang.so += 1; ve(); });
    nutXuat.addEventListener("click", () => chayNut(nutXuat,
      () => callApi("export_nhat_ky_thao_tac_csv", "", trang.nguoi || null, trang.hanhDong || null),
      (res) => { if (!res.ok) { showErrorToast(res.errors); return; } showToast(t("tk_nk_da_xuat", { n: res.data.n_rows }), "success"); }));
    ve();
  }

  /* ------------------------------------------------------------ thanh bên */
  function veThanhBen() {
    const hop = el("tkThanhBen");
    if (!hop) return;
    hop.textContent = "";
    if (phien && phien.co_tai_khoan && phien.dang_nhap) {
      hop.appendChild(mot("span", { id: "tkHuyHieu", class: "db-status", text: t("tk_dang_la", { ten: phien.ten, vai: tenVai(phien.vai) }) }));
      hop.appendChild(mot("button", { type: "button", class: "btn btn-secondary", id: "tkNutDangXuat", text: t("tk_dang_xuat"),
        onclick: () => callApi("dang_xuat").then(() => capNhat().then(() => veManDangNhap())) }));
    }
    hop.appendChild(mot("button", { type: "button", class: "btn btn-secondary", id: "tkNutMoHop", text: t("tk_nut_thanh_ben"), onclick: veHop }));
    hop.hidden = false;
  }

  /* Hỏi phiên; vẽ lại thanh bên; bật/tắt màn đăng nhập. Trả Promise để nơi gọi nối tiếp. */
  /* GT3-L2: ghi vai hiện tại lên <body> để CSS ẩn phần của quản trị khỏi giáo viên; nếu tab đang mở bị ẩn thì chuyển sang "Kết quả". */
  function ganVai() {
    const vai = phien && phien.co_tai_khoan && phien.dang_nhap ? phien.vai : "";
    if (document.body.dataset.vai === vai) return;
    document.body.dataset.vai = vai;
    if (vai !== "giao_vien") return;
    const dangMo = document.querySelector(".nav-item.is-active");
    if (dangMo && dangMo.dataset.quyen === "quan_tri") {
      const ketQua = document.querySelector('.nav-item[data-tab="results"]');
      if (ketQua) ketQua.click();
    }
  }

  function capNhat() {
    return callApi("get_phien_dang_nhap").then((res) => {
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
})();
