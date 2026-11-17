/* ==========================================================================
   14_giai_trinh.js — thẻ "Kết quả", khung "Tra cứu một học sinh" (GT1-L2).
   Quản trị / giáo viên gõ mã hoặc tên (có dấu hay không đều được), chọn một em, rồi xem vì sao em có / không có
   từng CLB: nguyện vọng, điểm của chính em, chỗ, mức vào được, câu giải thích. Dữ liệu: get_giai_trinh_hoc_sinh
   (chỉ ĐỌC). Sau khi chọn, danh sách gợi ý bị xoá để thẻ chỉ chứa dữ liệu của MỘT em.
   ========================================================================== */
"use strict";

(() => {
  let dangXem = null;          // {res, sid} gần nhất, để vẽ lại khi đổi ngôn ngữ
  let daNapLop = false;
  let luotTim = 0;             // mỗi lần chọn một em là huỷ mọi lần tìm đang bay (kết quả về muộn bị bỏ)

  function mot(tag, lop, chu) {
    const n = document.createElement(tag);
    if (lop) n.className = lop;
    if (chu !== undefined) n.textContent = chu;
    return n;
  }

  function oDiem(x) {
    return x === null || x === undefined ? t("gt_khong_co") : String(x);
  }

  function oChuan(x) {
    if (x.diem_chuan_loai === "diem" && x.diem_chuan !== null && x.diem_chuan !== undefined) {
      return t("gt_chuan_diem", { n: x.diem_chuan });
    }
    if (x.diem_chuan_loai === "boc_tham") return t("gt_chuan_boc_tham");
    if (x.diem_chuan_loai === "con_cho") return t("gt_chuan_con_cho");
    return t("gt_khong_co");
  }

  function veBuoi(b, hienNhan) {
    const khung = mot("div", "gt-buoi");
    if (hienNhan) khung.appendChild(mot("h3", "", nhanBuoi(b.buoi)));
    khung.appendChild(mot("p", "gt-ket-qua", b.ket_qua
      ? t("gt_buoi_dc_xep", { clb: b.ten_clb || b.ket_qua })
      : t("gt_buoi_chua_xep")));
    if (b.cau_tom_tat) khung.appendChild(mot("p", "gt-tom-tat", b.cau_tom_tat));
    if (b.cac_lua_chon.length) {
      const bang = mot("table", "data-table gt-bang");
      const dau = mot("tr");
      ["gt_th_hang", "gt_th_clb", "gt_th_diem", "gt_th_cho", "gt_th_chuan", "gt_th_ly_do"].forEach((k) => {
        dau.appendChild(mot("th", "", t(k)));
      });
      const th = mot("thead");
      th.appendChild(dau);
      bang.appendChild(th);
      const than = mot("tbody");
      b.cac_lua_chon.forEach((x) => {
        const hang = mot("tr", x.duoc_xep ? "gt-duoc-xep" : "");
        if (x.duoc_xep) hang.setAttribute("aria-current", "true");
        hang.appendChild(mot("td", "", x.hang === null || x.hang === undefined ? t("gt_ngoai_nv") : String(x.hang)));
        hang.appendChild(mot("td", "", x.ten_clb));
        hang.appendChild(mot("td", "", x.chon_loc ? oDiem(x.diem_em) : t("gt_khong_co")));
        hang.appendChild(mot("td", "", (x.da_nhan === null || x.da_nhan === undefined ? "?" : x.da_nhan) +
          " / " + oDiem(x.suc_chua)));
        hang.appendChild(mot("td", "", oChuan(x)));
        let cau = x.cau || "";
        if (x.vi_tri_cho) cau += (cau ? " " : "") + t("gt_cho_cho", { n: x.vi_tri_cho });
        hang.appendChild(mot("td", "", cau));
        than.appendChild(hang);
      });
      bang.appendChild(than);
      const cuon = mot("div", "scroll-x");
      cuon.appendChild(bang);
      khung.appendChild(cuon);
    }
    return khung;
  }

  /* `g`: chỗ vẽ thẻ; `quanTri` false = thẻ trong chế độ học sinh (không có nút quản trị). */
  function ve(d, g = el("gtKetQua"), quanTri = true) {
    g.textContent = "";
    const ten = d.lop ? t("gt_the_ten", { ten: d.ten, ma: d.student_id, lop: d.lop })
                      : t("gt_the_ten_khong_lop", { ten: d.ten, ma: d.student_id });
    g.appendChild(mot("h3", "gt-ten", ten));
    if (d.du_lieu_da_doi) {
      const c = mot("p", "gt-canh-bao", t("gt_da_doi"));
      c.setAttribute("role", "alert");
      g.appendChild(c);
    }
    const r = d.run || {};
    g.appendChild(mot("p", "gt-lan-chay", t("gt_lan_chay", { gio: dinhDangGio(r.run_at), seed: r.seed })));
    let tc = d.fa_bat ? t("gt_tieu_chi_fa") : t("gt_tieu_chi_thuong");
    if (!d.fa_bat && r.luat_xep && r.luat_xep.wharton) tc += t("gt_tieu_chi_diem_quyet_tam");
    g.appendChild(mot("p", "gt-tieu-chi", tc));
    d.buoi.forEach((b) => g.appendChild(veBuoi(b, d.buoi.length > 1 || b.buoi !== BUOI_MAC_DINH)));
    if (quanTri) {
      el("gtIn").hidden = false;
      el("btnGtInLop").hidden = !d.lop;
    }
  }

  function xem(sid) {
    luotTim += 1;
    el("gtDs").textContent = "";
    el("gtIn").hidden = true;
    el("gtKetQua").textContent = "";     // không để thẻ của em trước lẫn với em đang tải
    dangXem = null;
    callApiMoiNhat("gt_xem", "get_giai_trinh_hoc_sinh", sid).then((res) => {
      const g = el("gtKetQua");
      if (!res.ok) {
        dangXem = null;
        el("gtIn").hidden = true;
        g.textContent = trErrs(res.errors).join(" ");
        return;
      }
      dangXem = res.data;
      ve(res.data);
    });
  }

  function veDanhSach(ds) {
    const u = el("gtDs");
    u.textContent = "";
    if (!ds.length) {
      u.appendChild(mot("li", "gt-khong-thay", t("gt_khong_thay")));
      return;
    }
    ds.forEach((h) => {
      const li = mot("li");
      const nut = mot("button", "btn btn-secondary gt-chon", h.name ? h.name + " (" + h.student_id + ")" : h.student_id);
      nut.type = "button";
      nut.dataset.studentId = h.student_id;
      nut.addEventListener("click", () => xem(h.student_id));
      li.appendChild(nut);
      u.appendChild(li);
    });
  }

  function tim() {
    const luot = (luotTim += 1);
    const lop = el("gtLop").value;
    const args = lop ? [el("gtTim").value, lop] : [el("gtTim").value];
    callApiMoiNhat("gt_tim", "search_students", ...args).then((res) => {
      if (luot !== luotTim) return;
      if (!res.ok) {
        el("gtDs").textContent = trErrs(res.errors).join(" ");
        return;
      }
      veDanhSach(res.data);
    });
  }

  function napLop() {
    if (daNapLop) return;
    daNapLop = true;
    callApi("list_classes").then((res) => {
      if (!res.ok || !res.data.classes.length) return;
      const o = el("gtLop");
      o.textContent = "";
      const tat = mot("option", "", t("gt_tat_ca_lop"));
      tat.value = "";
      o.appendChild(tat);
      res.data.classes.forEach((c) => {
        const op = mot("option", "", c.class_id);
        op.value = c.class_id;
        o.appendChild(op);
      });
      o.hidden = false;
    });
  }

  /* Phiếu in: MỘT tệp HTML, mỗi em một trang (export_phieu_giai_trinh). */
  function inPhieu(doiSo) {
    chayXuat([["gt_in_muc", "export_phieu_giai_trinh", doiSo,
      (d) => t("gt_in_xong", { n: d.n_trang, path: d.path })]], el("gtXuatPhanHoi"));
  }
  el("btnGtInMot").addEventListener("click", () => { if (dangXem) inPhieu(["", [dangXem.student_id]]); });
  el("btnGtInLop").addEventListener("click", () => { if (dangXem && dangXem.lop) inPhieu(["", null, dangXem.lop]); });

  /* Mã tra cứu: tạo (chỉ em chưa có), xuất CSV để in phiếu. KHÔNG hiện mã trên màn hình quản trị. */
  el("btnGtTaoMa").addEventListener("click", () => {
    callApi("tao_ma_tra_cuu", true).then((res) => {
      const o = el("gtMaPhanHoi");
      o.textContent = res.ok ? t("gt_tao_ma_xong", { n: res.data.n_tao, co: res.data.n_co_san })
                             : trErrs(res.errors).join(" ");
    });
  });
  el("btnGtXuatMa").addEventListener("click", () => {
    chayXuat([["gt_xuat_ma_muc", "export_ma_tra_cuu_csv", [""],
      (d) => t("gt_xuat_ma_xong", { n: d.n_dong, path: d.path })]], el("gtMaPhanHoi"));
  });

  /* ---- Chế độ học sinh tự tra cứu (toàn màn hình) ----
     Chỉ có hai ô, một nút Xem và nút Thoát (có hỏi lại). Các phần còn lại của ứng dụng bị `inert` nên không bấm
     hay Tab tới được. Thẻ chỉ chứa dữ liệu của MỘT em và bị xoá sau 60 giây không thao tác. */
  const GIAY_NHAN = 60000;
  let henGio = null;
  let hsDangMo = false;
  let luotHs = 0;      // mỗi lần gửi, xoá thẻ, mở hay thoát là bỏ mọi phản hồi đang bay (không để thẻ em này hiện cho em khác)

  function xoaThe() {
    luotHs += 1;
    el("gtHsKetQua").textContent = "";
    el("gtHsLoi").textContent = "";
    el("gtHsMa").value = "";
    el("gtHsMaTra").value = "";
    el("gtHsQtMk").value = "";
  }

  function datHenGio() {
    clearTimeout(henGio);
    if (!hsDangMo) return;
    henGio = setTimeout(() => {
      const coThe = el("gtHsKetQua").childElementCount > 0;
      xoaThe();
      if (coThe) el("gtHsLoi").textContent = t("gt_hs_het_gio");
    }, GIAY_NHAN);
  }

  function khoaPhanConLai(bat) {
    Array.from(document.body.children).forEach((n) => {
      if (n.id === "gtHs" || n.tagName === "SCRIPT") return;
      if (bat) n.setAttribute("inert", ""); else n.removeAttribute("inert");
    });
  }

  let vaoXong = Promise.resolve({ ok: true, data: { khoa: false } });   // phản hồi của vao_che_do_hoc_sinh

  function moHs() {
    /* I2: mở lớp phủ ngay (như trước); có tài khoản thì backend khoá mọi hàm trừ tra cứu của học sinh. Backend
       từ chối (phiên hết hạn...) thì đóng lại. */
    moLopHs();
    vaoXong = callApi("vao_che_do_hoc_sinh");
    vaoXong.then((res) => {
      if (!res.ok && hsDangMo) { thoatHs(); showErrorToast(res.errors); }
    });
  }

  function moLopHs() {
    hsDangMo = true;
    xoaThe();
    el("gtHsXacNhan").hidden = true;
    khoaPhanConLai(true);
    /* role chỉ có khi đang mở: nơi khác (và test) coi mọi [role=dialog] trong DOM là hộp thoại đang hiện. */
    el("gtHs").setAttribute("role", "dialog");
    el("gtHs").setAttribute("aria-modal", "true");
    el("gtHsQuanTri").hidden = true;
    el("gtHs").hidden = false;
    el("gtHsMa").focus();
    datHenGio();
  }

  function thoatHs() {
    hsDangMo = false;
    clearTimeout(henGio);
    xoaThe();
    el("gtHs").hidden = true;
    el("gtHs").removeAttribute("role");
    el("gtHs").removeAttribute("aria-modal");
    khoaPhanConLai(false);
  }

  el("btnGtCheDoHs").addEventListener("click", moHs);
  el("btnGtHsThoat").addEventListener("click", () => { el("gtHsXacNhan").hidden = false; });
  el("btnGtHsKhong").addEventListener("click", () => { el("gtHsXacNhan").hidden = true; });
  /* I2: tải lại trang khi backend còn khoá chế độ học sinh -> mở lại lớp phủ (không gọi vao lần nữa). */
  window.addEventListener("tkPhien", (e) => {
    if (e.detail && e.detail.che_do_hs && !hsDangMo) {
      vaoXong = Promise.resolve({ ok: true, data: { khoa: true } });
      moLopHs();
    }
  });

  /* I2: không có tài khoản thì thoát như cũ; có tài khoản thì hỏi tài khoản quản trị (backend mới là nơi quyết định). */
  function laiPhien() { window.dispatchEvent(new Event("tkLamMoi")); }
  el("btnGtHsCo").addEventListener("click", () => {
    vaoXong.then((v) => {
      if (v.ok && v.data.khoa) {
        el("gtHsXacNhan").hidden = true;
        el("gtHsQtLoi").textContent = "";
        el("gtHsQuanTri").hidden = false;
        el("gtHsQtTen").focus();
        return;
      }
      if (!v.ok) return;                                  // lớp phủ đã đóng ở moHs
      thoatHs();
      callApi("thoat_che_do_hoc_sinh", "", "");           // không có tài khoản: chỉ để backend xoá cờ
    });
  });
  el("gtHsQuanTri").addEventListener("submit", (e) => {
    e.preventDefault();
    const ten = el("gtHsQtTen").value;
    const mk = el("gtHsQtMk").value;
    el("gtHsQtMk").value = "";                    // mật khẩu không nằm lại trên màn hình
    el("gtHsQtLoi").textContent = "";
    callApi("thoat_che_do_hoc_sinh", ten, mk).then((res) => {
      if (!res.ok) { el("gtHsQtLoi").textContent = trErrs(res.errors).join(" "); return; }
      el("gtHsQtTen").value = "";
      thoatHs();
      laiPhien();
    });
  });
  ["input", "click", "keydown", "pointerdown"].forEach((ev) => el("gtHs").addEventListener(ev, datHenGio));
  el("gtHsForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const ma = el("gtHsMa").value;
    const maTra = el("gtHsMaTra").value;
    el("gtHsKetQua").textContent = "";
    el("gtHsLoi").textContent = "";
    const luot = (luotHs += 1);
    callApi("tra_cuu_hoc_sinh", ma, maTra).then((res) => {
      if (!hsDangMo || luot !== luotHs) return;
      el("gtHsMaTra").value = "";             // không để mã nằm lại trên màn hình
      if (!res.ok) {
        el("gtHsLoi").textContent = trErrs(res.errors).join(" ");
        return;
      }
      ve(res.data, el("gtHsKetQua"), false);
    });
  });
  window.addEventListener("langchange", () => {
    if (hsDangMo && el("gtHsKetQua").childElementCount) el("gtHsKetQua").textContent = "";
  });

  el("gtTim").addEventListener("input", tim);
  el("gtTim").addEventListener("focus", () => { napLop(); if (!el("gtDs").children.length) tim(); });
  el("gtLop").addEventListener("change", tim);
  window.addEventListener("langchange", () => {
    if (dangXem) ve(dangXem);
    const o = el("gtLop");
    if (o.options.length) o.options[0].textContent = t("gt_tat_ca_lop");
  });
})();
