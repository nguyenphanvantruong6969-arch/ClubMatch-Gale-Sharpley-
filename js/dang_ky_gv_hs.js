/* js/dang_ky_gv_hs.js — DK3-L3 / DK4-UI: màn giáo viên (ba bước, D15) và màn học sinh (từng buổi: Xếp nguyện vọng → Đặt huy chương →
   Bài kiểm tra, rồi Xem lại và gửi; D39). Học sinh không thấy số đông (D26). Huy chương: mặc định theo thứ tự xếp, ghi đè bằng ô chọn
   (D2 đường A). Mỗi khung đúng một nút vàng = nút "bước kế tiếp". */
(function (global) {
  "use strict";
  const DK = global.DK, h = DK.h;
  const HC = ["Vàng", "Bạc", "Đồng"], HC_LOP = ["vang", "bac", "dong"];
  const SAU_HS = ["nhap_diem", "xuat"];
  const TRANG_THAI = { cho_duyet: "Chờ duyệt", duyet: "Đã duyệt", tu_choi: "Bị từ chối" };
  const THU = ["Chủ nhật", "thứ Hai", "thứ Ba", "thứ Tư", "thứ Năm", "thứ Sáu", "thứ Bảy"];

  /* "2026-11-25T14:05:33" → "14:05, thứ Tư 25/11" (không đổi múi giờ: lấy đúng chữ máy chủ ghi). */
  DK.guiLuc = function (nop) {
    const m = String(nop || "").match(/^(\d{4})-(\d\d)-(\d\d)[T ](\d\d):(\d\d)/);
    if (!m) return String(nop || "");
    return m[4] + ":" + m[5] + ", " + THU[new Date(+m[1], +m[2] - 1, +m[3]).getDay()] + " " + m[3] + "/" + m[2];
  };
  const TOI_DA_THE = 7;                              // D37: tối đa 7 thẻ CLB mỗi khung trước nút "Xem thêm"
  const chip = (chu, lop) => h("span.dk-chip" + (lop ? "." + lop : ""), {}, chu);
  const khoiChu = (a, b) => (a === b ? "khối " + a : "khối " + a + "–" + b);
  /* Chip ngắn theo loại: "Tự do" · "Giới hạn · 15 chỗ" · "Tuyển chọn · 15 chỗ". */
  const chipLoai = (c) => c.loai === "Tự do" ? chip("Tự do", "on")
    : chip(c.loai + (c.chi_tieu ? " · " + c.chi_tieu + " chỗ" : ""), c.loai === "Tuyển chọn" ? "wait" : "");
  const ghiChuLoai = (c) => c.loai === "Tự do" ? "Em chắc chắn có chỗ."
    : c.loai === "Tuyển chọn" ? "Có kiểm tra đầu vào. Dưới " + (c.diem_san === null || c.diem_san === undefined ? "điểm sàn" : c.diem_san + " điểm") + " thì không được xét."
      : "Không kiểm tra. Nếu đông, xét huy chương rồi bốc thăm.";
  const thanhBuoc = (nhan, cur, them) => h("ol.dk-buoc", { "aria-label": "Các bước" }, them || null,
    nhan.map((t, i) => h("li", Object.assign({}, i === cur ? { "aria-current": "step" } : {}, i === cur ? { class: "cur" } : {}), (i + 1) + ". " + t)));

  /* ============================== giáo viên ============================== */
  DK.giaoVien = async function (sua) {
    const T = DK.S.token;
    const tt = (await global.RBDA.callApi("dk_trang_thai")).data;
    const ds = (await DK.goi("dk_clb_danh_sach", T)).data || [];
    const mo = tt.giai_doan === "gv_dang_ky";
    const danh = h("ul.dk-ds", {}, ds.map((c) => h("li", {}, h("span.dk-than", {}, h("strong", {}, c.ten), " · " + c.buoi + " · " + c.loai,
      c.ly_do_tu_choi ? h("span.dk-phu", {}, " (" + c.ly_do_tu_choi + ")") : null),
      chip(TRANG_THAI[c.trang_thai], c.trang_thai === "duyet" ? "on" : c.trang_thai === "tu_choi" ? "off" : "wait"),
      mo && c.trang_thai !== "duyet" ? h("span.dk-thao-tac", {}, DK.nutNhe("Sửa", () => DK.giaoVien(c), { "aria-label": "Sửa " + c.ten }),
        DK.nutNhe("Xoá", function () { DK.chay(this, async () => { const r = await DK.goi("dk_clb_xoa", T, c.clb_id); if (r.ok) DK.giaoVien(); return r; }); }, { "aria-label": "Xoá " + c.ten })) : null)));
    const phan = [DK.thanhDau("Giáo viên"), DK.khung("CLB của tôi", ds.length ? danh : h("p.dk-phu", {}, "Chưa có CLB nào."),
      mo ? h("p.dk-phu", {}, "Giáo viên chỉ chọn được phòng còn trống ở buổi của CLB, và không nhận quá sức chứa. Quên PIN: nhờ quản trị bấm «Đặt lại PIN».")
        : h("p.dk-phu", {}, "Giáo viên không đăng ký hay sửa CLB được nữa. Cần thay đổi thì liên hệ quản lý."))];
    if (!mo) phan.push(h("p.dk-phu", {}, "Đăng ký CLB hiện đã đóng."));
    else phan.push(await formClb(tt, sua || null));
    DK.hien(...phan);
  };

  /* Kiểm từng bước (v8). Trả chuỗi lỗi hoặc "" nếu ổn. */
  const kiemBuoc = (b, d) => {
    const nguyen = (v) => /^\d+$/.test(String(v).trim());
    if (b === 1) {
      if (!d.buoi) return "Chọn buổi.";
      if (!d.phong_id) return "Chọn phòng.";
      if (d.loai !== "Tự do" && (!nguyen(d.chi_tieu === undefined || d.chi_tieu === null ? "" : d.chi_tieu) || +d.chi_tieu < 1)) return "Chỉ tiêu là số nguyên từ 1.";
    } else if (b === 2) {
      if (!nguyen(d.khoi_tu) || !nguyen(d.khoi_den) || +d.khoi_tu > +d.khoi_den) return "Chọn khối được tham gia.";
      if (d.loai === "Tuyển chọn") {
        if (!nguyen(d.diem_san === undefined || d.diem_san === null ? "" : d.diem_san) || +d.diem_san > 10) return "Điểm sàn là số nguyên từ 0 đến 10.";
        if (!/^https:\/\//i.test(String(d.link_forms || "").trim())) return "CLB Tuyển chọn cần link bài kiểm tra Google Forms (bắt đầu bằng https://).";
      }
    } else if (!String(d.ten || "").trim()) return "Nhập tên CLB.";
    return "";
  };

  async function formClb(tt, sua) {
    let buoc = 1;
    const TEN_BUOC = ["Lịch và phòng", "Ai được tham gia", "Giới thiệu"];
    const d = sua ? { ten: sua.ten, buoi: sua.buoi, loai: sua.loai, phong_id: sua.phong_id, chi_tieu: sua.chi_tieu_gv === null ? "" : sua.chi_tieu_gv,
      khoi_tu: sua.khoi_tu, khoi_den: sua.khoi_den, diem_san: sua.diem_san === null ? "" : sua.diem_san, link_forms: sua.link_forms, mo_ta: sua.mo_ta, yeu_cau: sua.yeu_cau }
      : { buoi: tt.buoi[0], loai: "Giới hạn", phong_id: "", khoi_tu: tt.khoi[0], khoi_den: tt.khoi[1] };
    const phongTheo = {};
    const taiPhong = async (b) => {
      if (!phongTheo[b]) phongTheo[b] = ((await DK.goi("dk_phong_danh_sach", DK.S.token, b, sua ? sua.clb_id : null)).data || []).filter((p) => !p.ban);
      if (!phongTheo[b].some((p) => String(p.phong_id) === String(d.phong_id))) d.phong_id = phongTheo[b][0] ? phongTheo[b][0].phong_id : "";
    };
    await taiPhong(d.buoi);
    const hop = h("section.dk-khung");
    const chon = (nhan, k, lua, doi) => h("label.dk-truong", {}, h("span", {}, nhan),
      h("select.dk-nhap", { onchange: async (e) => { d[k] = e.target.value; if (doi) await doi(); ve(); } }, lua.map(([v, t]) => h("option", { value: v, selected: String(d[k]) === String(v) }, t))));
    const nhap = (nhan, k, thuoc) => h("label.dk-truong", {}, h("span", {}, nhan),
      h("input.dk-nhap", Object.assign({ value: d[k] === undefined ? "" : d[k], oninput: (e) => { d[k] = e.target.value; } }, thuoc)));
    function ve() {
      const phong = phongTheo[d.buoi] || [];
      const b1 = [chon("Buổi", "buoi", tt.buoi.map((b) => [b, b]), () => taiPhong(d.buoi)),
        chon("Loại CLB", "loai", [["Tự do", "Tự do"], ["Giới hạn", "Giới hạn"], ["Tuyển chọn", "Tuyển chọn"]]),
        chon("Phòng (chỉ hiện phòng trống buổi này)", "phong_id", phong.map((p) => [p.phong_id, p.ten + " (" + p.suc_chua + " chỗ)"])),
        d.loai === "Tự do" ? h("p.dk-ghichu", {}, "CLB Tự do nhận mọi em đăng ký, không cần chỉ tiêu.") : nhap("Chỉ tiêu", "chi_tieu", { type: "number", min: "1" })];
      const b2 = [h("div.dk-nhom", {}, nhap("Từ khối", "khoi_tu", { type: "number" }), nhap("Đến khối", "khoi_den", { type: "number" })),
        d.loai === "Tuyển chọn" ? [nhap("Điểm sàn (0–10)", "diem_san", { type: "number", min: "0", max: "10" }), nhap("Đường dẫn bài thi", "link_forms")]
          : h("p.dk-ghichu", {}, "CLB " + d.loai + " không có bài kiểm tra. Muốn kiểm tra đầu vào thì chọn loại Tuyển chọn ở bước 1.")];
      const b3 = [nhap("Tên CLB", "ten"), nhap("Mô tả ngắn", "mo_ta"), nhap("Yêu cầu", "yeu_cau")];
      const noi = [b1, b2, b3][buoc - 1];
      const nutTrai = buoc > 1 ? DK.nutNhe("← Quay lại", () => { buoc--; ve(); }) : null;
      const kiem = () => { const loi = kiemBuoc(buoc, d); DK.thongBao(loi, !!loi); return !loi; };
      const nutPhai = buoc < 3 ? DK.nutVang("Tiếp theo", () => { if (kiem()) { buoc++; ve(); } }) : DK.nutVang(sua ? "Lưu thay đổi" : "Gửi duyệt", function () {
        if (!kiem()) return;
        DK.chay(this, async () => { const r = await DK.goi("dk_clb_luu", DK.S.token, Object.assign({}, d, { phong_id: +d.phong_id }), sua ? sua.clb_id : null);
          if (r.ok) DK.giaoVien(); return r; }); });
      hop.replaceChildren(h("h2.dk-tieude", {}, (sua ? "Sửa CLB «" + sua.ten + "»" : "Đăng ký CLB mới") + " · Bước " + buoc + "/3 · " + TEN_BUOC[buoc - 1]),
        thanhBuoc(TEN_BUOC, buoc - 1),
        h("form.dk-form", { novalidate: true, onsubmit: (e) => e.preventDefault() }, noi),
        h("div.dk-hang-nut", {}, nutTrai, sua ? DK.nutNhe("+ Đăng ký CLB mới", () => DK.giaoVien(), { id: "dkCLBMoi" }) : null, h("span.dk-gian"), nutPhai));
    }
    ve();
    return hop;
  }

  /* ============================== học sinh ============================== */
  DK.hocSinh = async function () {
    const T = DK.S.token;
    const tt = (await global.RBDA.callApi("dk_trang_thai")).data;
    if (tt.giai_doan !== "hs_dang_ky") {
      DK.hien(DK.thanhDau("Học sinh"), DK.khung(SAU_HS.includes(tt.giai_doan) ? "Đã hết hạn đăng ký" : "Chưa mở đăng ký",
        h("p#dkHsDong", {}, SAU_HS.includes(tt.giai_doan) ? "Đã hết hạn đăng ký. Nguyện vọng em đã gửi vẫn được tính." : "Chưa mở đăng ký cho học sinh. Em quay lại khi thầy cô thông báo."),
        DK.nutNhe("Về trang đầu", () => DK.dangXuatCuc())));
      return;
    }
    const clb = ((await DK.goi("dk_hs_clb_hop_le", T)).data || []);
    const cu = (await DK.goi("dk_hs_nguyen_vong", T)).data || { nguyen_vong: [], nop_luc: null };
    const theo = {}; tt.buoi.forEach((b) => { theo[b] = []; });
    cu.nguyen_vong.forEach((x) => { (theo[x.buoi] = theo[x.buoi] || []).push({ clb_id: x.clb_id, thi: x.thi, hc: x.huy_chuong }); });
    if (!DK.S.daXacNhan) {                          // DKL-G1: "Đúng là em chứ?" trước khi vào xếp nguyện vọng (v8 `confirm`)
      DK.henGio(60);
      DK.hien(DK.thanhDau("Học sinh"), DK.khung("Đúng là em chứ?",
        h("p.dk-ten-hs", {}, h("strong", {}, DK.S.ten)),
        h("p#dkThongTinHs", {}, "Lớp " + DK.S.lop + " · Khối " + DK.S.khoi + " · Mã " + DK.S.ma),
        cu.nop_luc ? h("p.dk-ghichu#dkDaGui", {}, "Em đã gửi lúc " + DK.guiLuc(cu.nop_luc) + ". Em có thể sửa rồi gửi lại; lần gửi cuối cùng được tính.") : null,
        h("div.dk-hang-nut", {}, DK.nutVang("Đúng là em", () => { DK.S.daXacNhan = true; DK.hocSinh(); }),
          DK.nutNhe("Không phải em", () => DK.dangXuatCuc()))));
      return;
    }
    const tay = new Set();
    const moHet = new Set();                         // DKL-G4 (D37): buổi đã bấm "Xem thêm"
    const cua = (id) => clb.find((c) => c.clb_id === id) || {};
    const macDinh = (ds) => { const r = {}; let i = 0; ds.forEach((x) => { r[x.clb_id] = cua(x.clb_id).loai !== "Tự do" && i < 3 ? HC[i++] : null; }); return r; };
    tt.buoi.forEach((b) => {                       // Đã lưu huy chương khác mặc định = em đã chỉnh tay
      const md = macDinh(theo[b]);
      if (theo[b].some((x) => (x.hc || null) !== (md[x.clb_id] || null))) tay.add(b);
    });
    let i = 0, bc = "rank", nopXong = !!cu.nop_luc;
    const N = tt.buoi.length;
    DK.henGio(60);
    ["pointerdown", "keydown"].forEach((s) => document.addEventListener(s, () => DK.S.vai === "hoc_sinh" && DK.henGio(60), { passive: true }));

    const hcCua = (b, x) => (tay.has(b) ? x.hc : macDinh(theo[b])[x.clb_id]) || "";
    const di = (buoc, buoi) => { bc = buoc; if (buoi !== undefined) i = buoi; ve(); window.scrollTo(0, 0); };

    function bar() {
      if (bc === "review" || bc === "receipt")
        return h("ol.dk-buoc", { "aria-label": "Các bước" }, h("li", {}, "Đã xong " + N + "/" + N + " buổi"), h("li.cur", { "aria-current": "step" }, "Xem lại và gửi"));
      const ten = ["rank", "medals", "tests"], nh = ["Xếp nguyện vọng", "Đặt huy chương", "Bài kiểm tra"];
      return h("ol.dk-buoc", { "aria-label": "Các bước", "data-buoi": String(i + 1) },
        h("li.dk-buoc-buoi", {}, h("strong", {}, "Buổi " + (i + 1) + "/" + N + " · " + tt.buoi[i])),
        nh.map((t, k) => h("li", ten[k] === bc ? { class: "cur", "aria-current": "step" } : {}, (k + 1) + ". " + t)),
        h("li", {}, "Xem lại và gửi"));
    }

    /* ---- bước 1: xếp nguyện vọng ---- */
    function vRank() {
      const b = tt.buoi[i], ds = theo[b];
      const chua = clb.filter((c) => c.buoi === b && !ds.some((x) => x.clb_id === c.clb_id));
      const day = ds.length >= tt.toi_da_nv;
      const doi = (k, j) => { const t = ds[k]; ds[k] = ds[j]; ds[j] = t; ve(); };
      const the = (c) => h("li.dk-the-clb", {}, h("div.dk-than", {},
        h("strong.dk-ten-clb", {}, c.ten), chipLoai(c), h("span.dk-phu", {}, ghiChuLoai(c)),
        h("span.dk-phu", {}, [c.giao_vien, c.phong, khoiChu(c.khoi_tu, c.khoi_den)].filter(Boolean).join(" · ")),
        c.mo_ta ? h("span.dk-mota", {}, c.mo_ta) : null,
        c.yeu_cau && c.yeu_cau.trim().toLowerCase() !== "không" ? h("span.dk-mota", {}, h("b", {}, "Yêu cầu: "), c.yeu_cau) : null),
      DK.nut("+ Thêm", () => { ds.push({ clb_id: c.clb_id, thi: false, hc: null }); ve(); }, { disabled: day, title: day ? "Buổi " + b + " đã đủ " + tt.toi_da_nv + " CLB. Bấm ✕ ở cột bên cạnh để bỏ bớt một CLB." : null }));
      const hang = ds.map((x, k) => h("li.dk-hang", {}, h("span.dk-nv", {}, "NV" + (k + 1)),
        h("span.dk-nm", {}, cua(x.clb_id).ten, h("span.dk-phu", {}, " · " + cua(x.clb_id).loai)),
        DK.nutNhe("↑", () => doi(k, k - 1), { "aria-label": "Lên", disabled: k === 0 }),
        DK.nutNhe("↓", () => doi(k, k + 1), { "aria-label": "Xuống", disabled: k === ds.length - 1 }),
        DK.nutNhe("✕", () => { ds.splice(k, 1); ve(); }, { "aria-label": "Bỏ" })));
      const thieuTuDo = ds.length && !ds.some((x) => cua(x.clb_id).loai === "Tự do") && clb.some((c) => c.buoi === b && c.loai === "Tự do");
      return [bar(), h("h1.dk-tieude", {}, "Buổi " + b + " · Xếp nguyện vọng"),
        h("p.dk-phu", {}, "Xếp đúng thứ tự em thích. Xếp CLB khó vào lên đầu không làm em mất cơ hội ở CLB sau. Mỗi buổi tối đa " + tt.toi_da_nv +
          " CLB, em vào nhiều nhất một CLB; buổi để trống là em không học buổi đó."),
        nopXong ? h("p.dk-ghichu#dkDaGui", {}, "Đã gửi lúc " + DK.guiLuc(cu.nop_luc) + ". Em có thể sửa rồi gửi lại; lần gửi cuối cùng được tính.") : null,
        thieuTuDo ? h("p.dk-ghichu", {}, "Thêm một CLB Tự do để chắc chắn có chỗ ở buổi này.") : null,
        h("div.dk-chia", {},
          h("section.dk-khung", {}, h("h2", {}, "CLB cho khối " + DK.S.khoi + " · " + b),
            chua.length ? h("ul.dk-ds.dk-cac-the", {}, (moHet.has(b) ? chua : chua.slice(0, TOI_DA_THE)).map(the)) : h("div.dk-rong", {}, ds.length ? "Em đã thêm hết CLB của buổi này." : "Buổi này không có CLB nào cho khối của em."),
            chua.length > TOI_DA_THE && !moHet.has(b) ? DK.nutNhe("Xem thêm (" + (chua.length - TOI_DA_THE) + ")", () => { moHet.add(b); ve(); }) : null),
          h("section.dk-khung", {}, h("h2", {}, "Nguyện vọng " + b + " ", h("span.dk-phu.dk-so", {}, ds.length + "/" + tt.toi_da_nv)),
            h("p.dk-phu", {}, "Giới hạn " + tt.toi_da_nv + " CLB tính riêng cho từng buổi (không phải cả tuần): sang buổi khác em chọn lại từ đầu."),
            ds.length ? h("ol.dk-xep", {}, hang) : h("div.dk-rong", {}, "Chưa chọn. Bấm \"+ Thêm\" ở bên cạnh."),
            day ? h("p.dk-ghichu", {}, "Buổi " + b + " đã đủ " + tt.toi_da_nv + " CLB (giới hạn tính riêng cho từng buổi). Muốn thêm CLB khác, bấm ✕ để bỏ bớt một CLB.") : null)),
        h("div.dk-hang-nut", {}, i > 0 ? DK.nutNhe("← Buổi trước", () => di("tests", i - 1)) : null, h("span.dk-gian"),
          DK.nutVang("Tiếp: đặt huy chương", () => di("medals"))),
      ];
    }

    /* ---- bước 2: đặt huy chương ---- */
    function vMedals() {
      const b = tt.buoi[i], ds = theo[b], opts = ds.filter((x) => cua(x.clb_id).loai !== "Tự do");
      let than = h("div.dk-rong", {}, "Nguyện vọng buổi này chỉ có CLB Tự do (luôn có chỗ) hoặc để trống, nên không cần huy chương. Em bấm tiếp.");
      if (opts.length) {
        const dat = (m, v) => {
          if (!tay.has(b)) { const md = macDinh(ds); ds.forEach((q) => { q.hc = md[q.clb_id] || null; }); tay.add(b); }
          ds.forEach((q) => { if (q.hc === m) q.hc = null; });
          if (v) ds.find((q) => String(q.clb_id) === v).hc = m;
          ve();
        };
        than = h("section.dk-khung", {},
          h("div.dk-hang-nut", {}, h("h2.dk-gian", {}, b), tay.has(b)
            ? DK.nutNhe("Đặt lại theo nguyện vọng", () => { tay.delete(b); ds.forEach((q) => { q.hc = null; }); ve(); })
            : chip("Đang đặt theo thứ tự nguyện vọng")),
          tay.has(b) ? h("p.dk-phu", {}, "Em đã tự đổi huy chương buổi này. Đổi thứ tự nguyện vọng sẽ không làm huy chương đổi theo.") : null,
          HC.map((m, k) => h("label.dk-huychuong.m-" + HC_LOP[k], {}, h("span.dk-hc-ten", {}, h("span.dk-cham", { "aria-hidden": "true" }), h("b", {}, m)),
            h("select.dk-nhap", { "aria-label": "Huy chương " + m, onchange: (e) => dat(m, e.target.value) },
              h("option", { value: "" }, "Không đặt"),
              opts.map((x) => h("option", { value: String(x.clb_id), selected: hcCua(b, x) === m }, "NV" + (ds.indexOf(x) + 1) + " · " + cua(x.clb_id).ten))))));
      }
      return [bar(), h("h1.dk-tieude", {}, "Buổi " + b + " · Đặt huy chương"),
        h("p.dk-phu", {}, "Mỗi buổi em có một huy chương Vàng, một Bạc, một Đồng. Khi CLB có nhiều bạn muốn vào hơn số chỗ, huy chương giúp em được ưu tiên: Vàng mạnh nhất. " +
          "Mỗi CLB nhận tối đa một huy chương. CLB Tự do luôn có chỗ nên không cần huy chương."),
        h("p.dk-ghichu", {}, "Đã đặt sẵn theo thứ tự nguyện vọng. Em đổi nếu muốn dồn huy chương cho CLB khác; thứ tự nguyện vọng vẫn giữ nguyên."),
        than,
        h("div.dk-hang-nut", {}, DK.nutNhe("← Quay lại", () => di("rank")), h("span.dk-gian"), DK.nutVang("Tiếp: bài kiểm tra", () => di("tests")))];
    }

    /* ---- bước 3: bài kiểm tra ---- */
    function vTests() {
      const b = tt.buoi[i], ds = theo[b], ung = ds.filter((x) => cua(x.clb_id).loai === "Tuyển chọn");
      const dem = ds.filter((x) => x.thi).length, cuoi = i === N - 1;
      const chuaTick = ung.filter((x) => !x.thi).map((x) => cua(x.clb_id).ten);
      return [bar(), h("h1.dk-tieude", {}, "Buổi " + b + " · Bài kiểm tra"),
        h("p.dk-phu", {}, "CLB Tuyển chọn có bài kiểm tra trên Google Forms; link hiện sau khi em gửi. Mỗi buổi tick tối đa " + tt.toi_da_thi +
          " CLB em sẽ làm bài. ", h("b", {}, "Không làm bài, hoặc dưới mốc điểm, thì em không được xét vào CLB đó"), " và phần mềm xét nguyện vọng tiếp theo."),
        h("p.dk-phu", {}, "Giới hạn " + tt.toi_da_thi + " bài thi tính riêng cho từng buổi (không phải cả tuần)."),
        dem >= tt.toi_da_thi ? h("p.dk-ghichu", {}, "Buổi " + b + " đã tick đủ " + tt.toi_da_thi + " bài thi (giới hạn tính riêng cho từng buổi). Muốn chọn CLB khác, bỏ tick một CLB trước.") : null,
        chuaTick.length ? h("p.dk-ghichu", {}, "CLB Tuyển chọn em xếp nhưng chưa tick sẽ không được xét: " + chuaTick.join(", ") + ".") : null,
        h("section.dk-khung", {}, h("div.dk-hang-nut", {}, h("h2.dk-gian", {}, "CLB Tuyển chọn trong nguyện vọng"), chip(dem + "/" + tt.toi_da_thi, dem >= tt.toi_da_thi ? "off" : "wait")),
          ung.length ? h("div.dk-cac-the", {}, ung.map((x) => h("label.dk-thi.dk-the-clb", {},
            h("input", { type: "checkbox", checked: x.thi, disabled: !x.thi && dem >= tt.toi_da_thi, title: !x.thi && dem >= tt.toi_da_thi ? "Đã đủ " + tt.toi_da_thi + " bài thi cho buổi này. Bỏ tick một CLB khác trước." : null, onchange: (e) => { x.thi = e.target.checked; ve(); } }),
            h("span.dk-than", {}, h("strong", {}, cua(x.clb_id).ten), " ", cua(x.clb_id).diem_san === null || cua(x.clb_id).diem_san === undefined ? null : h("span.chip.off.dk-san", {}, "Dưới " + cua(x.clb_id).diem_san + " thì không xét"), h("span.dk-phu", {}, ghiChuLoai(cua(x.clb_id)))))))
            : h("div.dk-rong", {}, "Nguyện vọng buổi này không có CLB Tuyển chọn nào. Em bấm tiếp.")),
        h("div.dk-hang-nut", {}, DK.nutNhe("← Quay lại", () => di("medals")), h("span.dk-gian"),
          DK.nutVang(cuoi ? "Tiếp: xem lại và gửi" : "Tiếp: " + tt.buoi[i + 1], () => (cuoi ? di("review") : di("rank", i + 1))))];
    }

    /* ---- bước 4: xem lại; biên nhận ---- */
    function tomTat() {
      const hang = tt.buoi.map((b) => {
        const ds = theo[b];
        return [b, ds.length ? h("span.dk-tt", {}, ds.map((x, k) => {
          const m = hcCua(b, x);
          return h("span.dk-tt-dong", {}, "NV" + (k + 1) + " " + cua(x.clb_id).ten, m ? chip(m, "m-" + HC_LOP[HC.indexOf(m)]) : null,
            x.thi ? chip("Thi", "wait") : null);
        })) : h("span.dk-phu", {}, "Không học buổi này")];
      });
      const thi = [].concat(...tt.buoi.map((b) => theo[b].filter((x) => x.thi).map((x) => cua(x.clb_id))));
      return [h("table.dk-bang", {}, h("thead", {}, h("tr", {}, h("th", {}, "Buổi"), h("th", {}, "Nguyện vọng"))),
        h("tbody", {}, hang.map((r) => h("tr", {}, h("td", {}, r[0]), h("td", {}, r[1]))))),
      h("h3", {}, "Bài kiểm tra (" + thi.length + ")"),
      thi.length ? h("ul.dk-ds", {}, thi.map((c) => h("li", {}, c.ten, bc === "receipt" && c.link_forms
        ? h("a", { href: c.link_forms, target: "_blank", rel: "noopener" }, "Làm bài thi") : null))) : h("p.dk-phu", {}, "Không làm bài kiểm tra nào.")];
    }
    function vReview() {
      const co = tt.buoi.some((b) => theo[b].length);
      return [bar(), h("h1.dk-tieude", {}, "Xem lại và gửi"),
        co ? null : h("p.dk-ghichu", {}, "Em chưa chọn CLB nào. Gửi như vậy nghĩa là em không tham gia CLB nào học kỳ này."),
        h("section.dk-khung", {}, tomTat()),
        h("div.dk-hang-nut", {}, DK.nutNhe("← Quay lại", () => di("tests", N - 1)), h("span.dk-gian"),
          DK.nutVang(nopXong ? "Gửi lại nguyện vọng" : "Gửi nguyện vọng", function () { nop(this); }, { id: "dkGui" }))];
    }
    function vReceipt() {
      return [bar(), h("section.dk-khung", {}, h("h1.dk-tieude", {}, "Đã gửi"),
        h("p#dkBienNhan.dk-bien-nhan", {}, "Đã gửi lúc " + DK.guiLuc(cu.nop_luc)), tomTat(),
        h("p.dk-phu", {}, "Em có thể đăng nhập lại để sửa trước hạn chót" + (tt.han_chot ? " (" + String(tt.han_chot).replace("T", " ") + ")" : "") + ". Máy sẽ tự thoát sau 30 giây."),
        h("div.dk-hang-nut", {}, h("span.dk-gian"), DK.nutVang("Xong, thoát", () => DK.dangXuatCuc())))];
    }

    function ve() {
      const noi = { rank: vRank, medals: vMedals, tests: vTests, review: vReview, receipt: vReceipt }[bc]();
      DK.hien(DK.thanhDau("Học sinh · " + DK.S.lop), ...noi);
    }
    async function nop(nut) {
      const nv = [], buoiTay = [...tay];
      tt.buoi.forEach((b) => theo[b].forEach((x) => nv.push({ clb_id: x.clb_id, thi: x.thi, huy_chuong: hcCua(b, x) || null })));
      await DK.chay(nut, async () => {
        const r = await DK.goi("dk_hs_luu", DK.S.token, nv, buoiTay);
        if (r.ok) {
          cu.nop_luc = r.data.nop_luc; nopXong = true; bc = "receipt"; ve();
          DK.thongBao("Đã nộp lúc " + r.data.nop_luc.slice(11, 16) + "." + (r.data.canh_bao.length ? " " + DK.loiChu(r.data.canh_bao) : ""));
          setTimeout(() => DK.S.vai === "hoc_sinh" && DK.dangXuatCuc(), 30000);
        }
        return r;
      });
    }
    ve();
  };
})(window);
