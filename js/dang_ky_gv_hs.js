/* js/dang_ky_gv_hs.js — DK3-L3: màn giáo viên (ba bước, D15) và màn học sinh (từng buổi, D39).
   Học sinh không thấy số đông (D26). Huy chương: mặc định theo thứ tự xếp, ghi đè bằng ô chọn (D2 đường A). */
(function (global) {
  "use strict";
  const DK = global.DK, h = DK.h;
  const HC = ["Vàng", "Bạc", "Đồng"];
  const TRANG_THAI = { cho_duyet: "Chờ duyệt", duyet: "Đã duyệt", tu_choi: "Bị từ chối" };

  /* ============================== giáo viên ============================== */
  DK.giaoVien = async function () {
    const T = DK.S.token;
    const tt = (await global.RBDA.callApi("dk_trang_thai")).data;
    const [dsr, phr] = await Promise.all([DK.goi("dk_clb_danh_sach", T), DK.goi("dk_phong_danh_sach", T)]);
    const ds = dsr.data || [], phong = phr.data || [];
    const mo = tt.giai_doan === "gv_dang_ky";
    const danh = h("ul.dk-ds", {}, ds.map((c) => h("li", {}, c.ten + " · " + c.buoi + " · " + c.loai + " · " + TRANG_THAI[c.trang_thai] +
      (c.ly_do_tu_choi ? " (" + c.ly_do_tu_choi + ")" : ""))));
    const phan = [DK.thanhDau("Giáo viên"), DK.khung("CLB của tôi", ds.length ? danh : h("p.dk-phu", {}, "Chưa có CLB nào."))];
    if (!mo) phan.push(h("p.dk-phu", {}, "Đăng ký CLB hiện đã đóng."));
    else phan.push(formClb(tt, phong));
    DK.hien(...phan);
  };

  function formClb(tt, phong) {
    let buoc = 1;
    const d = { buoi: tt.buoi[0], loai: "Giới hạn", phong_id: phong[0] ? phong[0].phong_id : "", khoi_tu: tt.khoi[0], khoi_den: tt.khoi[1] };
    const hop = h("section.dk-khung");
    const chon = (nhan, k, lua) => h("label.dk-truong", {}, h("span", {}, nhan),
      h("select.dk-nhap", { onchange: (e) => { d[k] = e.target.value; ve(); } }, lua.map(([v, t]) => h("option", { value: v, selected: String(d[k]) === String(v) }, t))));
    const nhap = (nhan, k, thuoc) => h("label.dk-truong", {}, h("span", {}, nhan),
      h("input.dk-nhap", Object.assign({ value: d[k] === undefined ? "" : d[k], oninput: (e) => { d[k] = e.target.value; } }, thuoc)));
    function ve() {
      const b1 = [chon("Buổi", "buoi", tt.buoi.map((b) => [b, b])), chon("Loại CLB", "loai", [["Tự do", "Tự do"], ["Giới hạn", "Giới hạn"], ["Tuyển chọn", "Tuyển chọn"]]),
        chon("Phòng", "phong_id", phong.map((p) => [p.phong_id, p.ten + " (" + p.suc_chua + " chỗ)"])),
        d.loai === "Tự do" ? null : nhap("Chỉ tiêu", "chi_tieu", { type: "number", min: "1" })];
      const b2 = [nhap("Từ khối", "khoi_tu", { type: "number" }), nhap("Đến khối", "khoi_den", { type: "number" }),
        d.loai === "Tuyển chọn" ? [nhap("Điểm sàn (0–10)", "diem_san", { type: "number", min: "0", max: "10" }), nhap("Đường dẫn bài thi", "link_forms")] : null];
      const b3 = [nhap("Tên CLB", "ten"), nhap("Mô tả ngắn", "mo_ta"), nhap("Yêu cầu", "yeu_cau")];
      const noi = [b1, b2, b3][buoc - 1];
      const nutTrai = buoc > 1 ? DK.nutNhe("← Quay lại", () => { buoc--; ve(); }) : null;
      const nutPhai = buoc < 3 ? DK.nut("Tiếp theo", () => { buoc++; ve(); }) : DK.nutVang("Gửi duyệt", function () {
        DK.chay(this, async () => { const r = await DK.goi("dk_clb_luu", DK.S.token, Object.assign({}, d, { phong_id: +d.phong_id }));
          if (r.ok) DK.giaoVien(); return r; }); });
      hop.replaceChildren(h("h2.dk-tieude", {}, "Đăng ký CLB mới · Bước " + buoc + "/3 · " + ["Lịch và phòng", "Ai được tham gia", "Giới thiệu"][buoc - 1]),
        h("form.dk-form", { novalidate: true, onsubmit: (e) => e.preventDefault() }, noi), nutTrai, nutPhai);
    }
    ve();
    return hop;
  }

  /* ============================== học sinh ============================== */
  DK.hocSinh = async function () {
    const T = DK.S.token;
    const tt = (await global.RBDA.callApi("dk_trang_thai")).data;
    if (tt.giai_doan !== "hs_dang_ky") {
      DK.hien(DK.thanhDau("Học sinh"), DK.khung("Chưa mở đăng ký", h("p", {}, "Cổng đăng ký học sinh hiện chưa mở hoặc đã đóng."), DK.nutNhe("Về trang đầu", () => DK.dangXuatCuc())));
      return;
    }
    const clb = ((await DK.goi("dk_hs_clb_hop_le", T)).data || []);
    const cu = (await DK.goi("dk_hs_nguyen_vong", T)).data || { nguyen_vong: [], nop_luc: null };
    const theo = {}; tt.buoi.forEach((b) => { theo[b] = []; });
    cu.nguyen_vong.forEach((x) => { (theo[x.buoi] = theo[x.buoi] || []).push({ clb_id: x.clb_id, thi: x.thi, hc: x.huy_chuong }); });
    const tay = new Set();
    const loaiCua = (id) => (clb.find((c) => c.clb_id === id) || {}).loai;
    const macDinh = (ds) => { const r = {}; let i = 0; ds.forEach((x) => { r[x.clb_id] = loaiCua(x.clb_id) !== "Tự do" && i < 3 ? HC[i++] : null; }); return r; };
    tt.buoi.forEach((b) => {                       // Đã lưu huy chương khác mặc định = em đã chỉnh tay
      const md = macDinh(theo[b]);
      if (theo[b].some((x) => (x.hc || null) !== (md[x.clb_id] || null))) tay.add(b);
    });
    let i = 0, nopXong = !!cu.nop_luc;
    DK.henGio(60);
    ["pointerdown", "keydown"].forEach((s) => document.addEventListener(s, () => DK.S.vai === "hoc_sinh" && DK.henGio(60), { passive: true }));

    function ve() {
      const b = tt.buoi[i], ds = theo[b], md = macDinh(ds), cuoi = i === tt.buoi.length - 1;
      const hcCua = (x) => (tay.has(b) ? x.hc : md[x.clb_id]) || "";
      const chua = clb.filter((c) => c.buoi === b && !ds.some((x) => x.clb_id === c.clb_id));
      const dem = ds.filter((x) => x.thi).length;
      const doi = (k, j) => { const t = ds[k]; ds[k] = ds[j]; ds[j] = t; ve(); };
      const hang = ds.map((x, k) => {
        const c = clb.find((q) => q.clb_id === x.clb_id);
        return h("li.dk-hang", {}, h("span.dk-thu", {}, String(k + 1)), h("span.dk-ten", {}, c.ten, " ", h("em.dk-loai", {}, c.loai)),
          c.loai === "Tuyển chọn" ? h("label.dk-thi", {}, h("input", { type: "checkbox", checked: x.thi, disabled: !x.thi && dem >= tt.toi_da_thi,
            onchange: (e) => { x.thi = e.target.checked; ve(); } }), " Thi") : null,
          c.loai !== "Tự do" ? h("select.dk-nhap.dk-hc", { "aria-label": "Huy chương", onchange: (e) => {
            if (!tay.has(b)) ds.forEach((q) => { q.hc = md[q.clb_id] || null; });
            tay.add(b); const v = e.target.value || null;
            ds.forEach((q) => { if (v && q !== x && q.hc === v) q.hc = null; });
            x.hc = v; ve(); } }, [["", "—"]].concat(HC.map((q) => [q, q])).map(([v, t]) => h("option", { value: v, selected: hcCua(x) === v }, t))) : null,
          h("span.dk-dieu", {}, DK.nutNhe("↑", () => k > 0 && doi(k, k - 1), { "aria-label": "Lên" }),
            DK.nutNhe("↓", () => k < ds.length - 1 && doi(k, k + 1), { "aria-label": "Xuống" }),
            DK.nutNhe("✕", () => { ds.splice(k, 1); ve(); }, { "aria-label": "Bỏ" })));
      });
      const co = ds.length >= tt.toi_da_nv;
      const khungDieu = [i > 0 ? DK.nutNhe("← Buổi trước", () => { i--; ve(); }) : null,
        cuoi ? DK.nutVang(nopXong ? "Nộp lại nguyện vọng" : "Nộp nguyện vọng", function () { nop(this); }) : DK.nut("Buổi tiếp theo →", () => { i++; ve(); })];
      DK.hien(DK.thanhDau("Học sinh · " + DK.S.lop),
        DK.khung("Buổi " + b + " (" + (i + 1) + "/" + tt.buoi.length + ")",
          h("p.dk-phu", {}, "Xếp CLB theo thứ tự muốn vào nhất. Phải có ít nhất một CLB Tự do để được xếp chắc chỗ."),
          h("ol.dk-ds", {}, hang.length ? hang : h("li.dk-phu", {}, "Chưa chọn CLB nào trong buổi này.")),
          ds.some((x) => tay.has(b)) || tay.has(b) ? DK.nutNhe("Đặt lại huy chương theo thứ tự xếp", () => { tay.delete(b); ds.forEach((q) => { q.hc = null; }); ve(); }) : null,
          h("h2", {}, "CLB có thể chọn"),
          h("ul.dk-ds", {}, chua.map((c) => h("li", {}, h("span", {}, c.ten, " ", h("em.dk-loai", {}, c.loai),
            c.loai === "Tuyển chọn" ? " · điểm sàn " + c.diem_san : ""), co ? null : DK.nut("+ Thêm", () => { ds.push({ clb_id: c.clb_id, thi: false, hc: null }); ve(); }))))),
        h("div.dk-nhom", {}, khungDieu),
        nopXong ? h("p.dk-phu", {}, "Đã gửi lúc " + (cu.nop_luc || "").replace("T", " ") + ". Có thể sửa đến hết hạn.") : null);
    }
    async function nop(nut) {
      const nv = [], buoiTay = [...tay];
      tt.buoi.forEach((b) => theo[b].forEach((x) => nv.push({ clb_id: x.clb_id, thi: x.thi, huy_chuong: x.hc })));
      await DK.chay(nut, async () => {
        const r = await DK.goi("dk_hs_luu", DK.S.token, nv, buoiTay);
        if (r.ok) {
          cu.nop_luc = r.data.nop_luc; nopXong = true; ve();
          DK.thongBao("Đã nộp lúc " + r.data.nop_luc.slice(11, 16) + "." + (r.data.canh_bao.length ? " " + DK.loiChu(r.data.canh_bao) : ""));
          setTimeout(() => DK.S.vai === "hoc_sinh" && DK.dangXuatCuc(), 30000);
        }
        return r;
      });
    }
    ve();
  };
})(window);
