/* js/15_tieu_chi.js — GT2: khung "Tiêu chí xếp" ở thẻ Quản lý.

   Hiện thứ tự tiêu chí HIỆU LỰC bằng lời thường (do get_tieu_chi dựng), và cho chọn lại CHỈ trong
   các lựa chọn có sẵn (cùng danh sách get_tieu_chi trả về). Lưu đi qua update_workspace_config:
   không có đường lưu mới. Không có ô nào đọc thứ hạng nguyện vọng, kết quả kỳ trước hay hoàn
   cảnh cá nhân. Script thường, dùng chung phạm vi với các tệp js/ khác. */
"use strict";

let gt2TcDuLieu = null;

function gt2TcLang() {
  return window.I18N.getLang() === "en" ? "en" : "vi";
}

/* Vẽ thứ tự hai tầng + dòng "chưa dùng" từ dữ liệu get_tieu_chi theo ngôn ngữ hiện tại. */
function gt2TcVeDanhSach() {
  const d = gt2TcDuLieu;
  if (!d) return;
  const lang = gt2TcLang();
  const mo = lang === "en" ? d.mo_ta_en : d.mo_ta;
  const khung = el("gt2TcDanhSach");
  clear(khung);
  ["tang_1", "tang_2"].forEach((tang) => {
    const dong = mo.filter((m) => m.nhom === tang);
    if (!dong.length) return;
    const h = document.createElement("h3");
    h.textContent = d.tang[tang][lang];
    h.dataset.tang = tang;
    const ol = document.createElement("ol");
    ol.dataset.tang = tang;
    dong.forEach((m) => {
      const li = document.createElement("li");
      li.dataset.ma = m.ma;
      li.textContent = m.chu;
      ol.appendChild(li);
    });
    khung.appendChild(h);
    khung.appendChild(ol);
  });
  const kd = mo.filter((m) => m.nhom === "khong_dung");
  const hop = el("gt2TcKhongDung");
  clear(hop);
  hop.hidden = !kd.length;
  if (kd.length) {                       /* GT4-L7: từng dòng "chưa có tác dụng" là một mục, màu xám */
    const tde = document.createElement("strong");
    tde.textContent = t("gt2_tc_khong_dung");
    const ul = document.createElement("ul");
    kd.forEach((m) => {
      const li = document.createElement("li");
      li.textContent = m.chu;
      ul.appendChild(li);
    });
    hop.appendChild(tde);
    hop.appendChild(ul);
  }
  el("gt2TcGhiChu").textContent = d.ghi_chu[lang];
}

function gt2TcVeDieuKhien() {
  const d = gt2TcDuLieu;
  if (!d) return;
  const lang = gt2TcLang();
  [["priority", "gt2TcPriority"], ["tier_mode", "gt2TcTierMode"], ["score_scope", "gt2TcScoreScope"]]
    .forEach(([khoa, id]) => {
      const lc = d.lua_chon[khoa];
      const sel = el(id);
      clear(sel);
      lc.gia_tri.forEach((gt) => {
        const o = document.createElement("option");
        o.value = gt;
        o.textContent = lc.nhan[gt][lang];
        sel.appendChild(o);
      });
      sel.value = d.luat[khoa];
      el(id + "Nhan").textContent = lc.tieu_de[lang];
    });
  el("gt2TcTiersNhan").textContent = d.lua_chon.tiers.tieu_de[lang];
}

function gt2TcDatGiaTri() {
  const d = gt2TcDuLieu;
  el("gt2TcTiers").value = (d.luat.tiers || []).join("\n");
}

/* GT4-L7: nhắc (không chặn) khi các lựa chọn đang hiện làm cấu hình thử thành vô nghĩa. */
function gt2CanhBao() {
  const o = el("gt2ThuCanhBao");
  const rong = !el("gt2TcTiers").value.split("\n").some((x) => x.trim());
  let khoa = "";
  if (el("gt2TcPriority").value === "tier" && rong) khoa = "gt2_canh_khong_nhom";
  else if (el("gt2TcTierMode").value === "strict" && rong) khoa = "gt2_canh_nhom_rong";
  o.hidden = !khoa;
  o.textContent = khoa ? t(khoa) : "";
}

function taiTieuChi() {
  return chayTai(callApi("get_tieu_chi"), (res) => {
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    gt2TcDuLieu = res.data;
    gt2TcVeDanhSach();
    gt2TcVeDieuKhien();
    gt2TcDatGiaTri();
    gt2CanhBao();
    return gt2SsTai(false);
  });
}

/* Chỉ gửi khoá của luật xếp mà người dùng có thể chọn; khoá khác giữ nguyên như đã lưu. */
function gt2TcLuatDangChon() {
  const nhom = el("gt2TcTiers").value.split("\n").map((x) => x.trim()).filter((x) => x);
  return {
    priority: el("gt2TcPriority").value,
    tier_mode: el("gt2TcTierMode").value,
    score_scope: el("gt2TcScoreScope").value,
    tiers: nhom,
    /* UX1A-L2b: cờ điểm quyết tâm do thẻ ở trang Cài đặt giữ. Ở đây chỉ tự tắt khi lựa chọn đang
       hiện làm nó không dùng được (xếp chỉ theo nhóm / tính điểm theo từng người). */
    ...(el("gt2TcPriority").value === "tier" || el("gt2TcScoreScope").value === "per_person"
      ? { wharton: false } : {}),
  };
}

function gt2TcLuu() {
  const phanHoi = el("gt2TcPhanHoi");
  return callApi("update_workspace_config", { rules: gt2TcLuatDangChon() }).then((res) => {
    if (!res.ok) {
      feedbackErrors(phanHoi, res.errors);
      return;
    }
    feedback(phanHoi, t("gt2_tc_da_luu"), false);
    return taiTieuChi();
  });
}

/* ---- GT2-L3: thử cấu hình. Chữ lấy từ dữ liệu (tên, mô tả) chỉ vào textContent. ---- */
let gt2SsDs = null; /* kết quả list_lan_chay */
let gt2SsKq = null; /* kết quả so_sanh_lan_chay đang hiện */

function gt2SsNhan(x) {
  return t(x.nhan === "thu" ? "gt2_thu_lan_thu" : "gt2_thu_lan_chinh_thuc", { id: x.run_id });
}

function gt2SsVeLuaChon() {
  const ds = gt2SsDs;
  const co = !!(ds && ds.chinh_thuc);
  el("gt2ThuChuaCo").hidden = co;
  el("gt2ThuChon").hidden = !co;
  el("gt2ThuNut").hidden = !co;
  if (!co) return;
  const luaChon = [ds.chinh_thuc].concat(ds.thu);
  ["gt2ThuA", "gt2ThuB"].forEach((id) => {
    const sel = el(id);
    const cu = sel.value;
    clear(sel);
    luaChon.forEach((x) => {
      const o = document.createElement("option");
      o.value = String(x.run_id);
      o.textContent = gt2SsNhan(x) + (x.run_at ? " — " + dinhDangGio(x.run_at) : "");
      sel.appendChild(o);
    });
    if (cu && luaChon.some((x) => String(x.run_id) === cu)) sel.value = cu;
  });
}

/* ---- GT2-L4: dùng tiêu chí của một lần chạy thử. Chỉ LƯU cấu hình; không chạy, không chép kết quả. ---- */
function gt2AdTomTat(x) {
  const mo = gt2TcLang() === "en" ? x.mo_ta_en : x.mo_ta;
  return mo.filter((m) => m.nhom !== "khong_dung").map((m) => m.chu);
}

function gt2AdVeDanhSach() {
  const ds = gt2SsDs ? gt2SsDs.thu : [];
  el("gt2ThuApDung").hidden = !ds.length;
  const ul = el("gt2ThuApDungDs");
  clear(ul);
  ds.forEach((x) => {
    const li = document.createElement("li");
    const ten = document.createElement("span");
    ten.textContent = gt2SsNhan(x);
    const nut = document.createElement("button");
    nut.type = "button";
    nut.className = "btn";
    nut.dataset.runId = String(x.run_id);
    nut.textContent = t("gt2_ad_nut");
    nut.addEventListener("click", () => gt2AdHoi(x));
    li.appendChild(ten);
    li.appendChild(nut);
    ul.appendChild(li);
  });
}

function gt2AdHoi(x) {
  const bar = el("gt2ThuApDungXacNhan");
  clear(bar);
  bar.hidden = false;
  const tieuDe = document.createElement("p");
  tieuDe.textContent = t("gt2_ad_hoi", { id: x.run_id });
  const ol = document.createElement("ol");
  gt2AdTomTat(x).forEach((chu) => {
    const li = document.createElement("li");
    li.textContent = chu;
    ol.appendChild(li);
  });
  const dong = document.createElement("button");
  dong.type = "button";
  dong.className = "btn btn-primary";
  dong.id = "gt2ThuApDungXacNhanNut";
  dong.textContent = t("gt2_ad_xac_nhan");
  dong.addEventListener("click", () => chayNut(dong, () => callApi("ap_dung_tieu_chi", x.run_id), (res) => {
    bar.hidden = true;
    const o = el("gt2ThuApDungPhanHoi");
    if (!res.ok) {
      feedbackErrors(o, res.errors);
      return;
    }
    feedback(o, t("gt2_ad_da_luu"), false);
    return taiTieuChi();
  }));
  const huy = document.createElement("button");
  huy.type = "button";
  huy.className = "btn";
  huy.textContent = t("gt2_ad_huy");
  huy.addEventListener("click", () => { bar.hidden = true; });
  [tieuDe, ol, dong, huy].forEach((n) => bar.appendChild(n));
}

function gt2SsTai(chonLai) {
  return callApi("list_lan_chay").then((res) => {
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    gt2SsDs = res.data;
    gt2SsVeLuaChon();
    gt2AdVeDanhSach();
    if (chonLai && gt2SsDs.chinh_thuc) {
      el("gt2ThuB").value = String(gt2SsDs.chinh_thuc.run_id);
      if (gt2SsDs.thu.length) el("gt2ThuA").value = String(gt2SsDs.thu[0].run_id);
    }
  });
}

/* GT4-L7: chênh lệch B − A bằng CHỮ ("+3", "−2") kèm màu; cùng quy tắc với `tieu_chi.chenh` (tệp HTML xuất ra). */
function gt2SsChenh(a, b) {
  if (typeof a !== "number" || typeof b !== "number") return "";
  const d = Math.round((b - a) * 100) / 100;
  if (d === 0) return "";
  const xau = String(Math.abs(d));
  return (d > 0 ? "+" : "−") + (gt2TcLang() === "vi" ? xau.replace(".", ",") : xau);
}

function gt2SsSo(v, hau) {
  if (v === null || v === undefined) return "—";
  return String(v).replace(".", gt2TcLang() === "vi" ? "," : ".") + (hau || "");
}

/* Một ô số: giá trị + (tuỳ chọn) chênh lệch so với lần A. `cho` = {v, a, hau}: có `a` thì kèm chênh lệch. */
function gt2SsO(td, cho) {
  td.className = "so";
  td.appendChild(document.createTextNode(gt2SsSo(cho.v, cho.hau)));
  if (cho.a !== undefined) {
    const c = gt2SsChenh(cho.a, cho.v);
    if (c) {
      const sp = document.createElement("span");
      sp.className = "gt2-delta " + (c.charAt(0) === "+" ? "len" : "xuong");
      sp.textContent = c + (cho.hau || "");
      td.appendChild(sp);
    }
  }
}

/* `dong`: mỗi dòng là mảng ô; ô là chuỗi (chữ, căn trái) hoặc {v, a, hau} (số, căn phải, có chênh lệch nếu có `a`). */
function gt2SsBang(tieuDe, dau, dong) {
  const h = document.createElement("h3");
  h.textContent = tieuDe;
  const bang = document.createElement("table");
  bang.className = "data-table";
  const hd = document.createElement("thead");
  const tr = document.createElement("tr");
  dau.forEach((c, i) => {
    const th = document.createElement("th");
    th.textContent = c;
    if (i > 0 && typeof (dong[0] || [])[i] === "object") th.className = "so";
    tr.appendChild(th);
  });
  hd.appendChild(tr);
  bang.appendChild(hd);
  const tb = document.createElement("tbody");
  dong.forEach((d) => {
    const r = document.createElement("tr");
    d.forEach((c) => {
      const td = document.createElement("td");
      if (c !== null && typeof c === "object") gt2SsO(td, c);
      else td.textContent = c === null || c === undefined ? "—" : String(c);
      r.appendChild(td);
    });
    tb.appendChild(r);
  });
  bang.appendChild(tb);
  const cuon = document.createElement("div");
  cuon.className = "gt2-bang-cuon";
  cuon.appendChild(bang);
  return [h, cuon];
}

const GT2_SS_DOI_TOI_DA = 200;

/* Thẻ một lần chạy: tiêu đề, ngày, tiêu chí HAI TẦNG tách riêng (không gộp một đoạn). */
function gt2SsTheLan(x) {
  const lang = gt2TcLang();
  const the = document.createElement("section");
  the.className = "gt2-the gt2-the-lan";
  const h = document.createElement("h4");
  h.textContent = gt2SsNhan(x);
  the.appendChild(h);
  if (x.run_at) {
    const ngay = document.createElement("p");
    ngay.className = "gt2-ngay";
    ngay.textContent = dinhDangGio(x.run_at);
    the.appendChild(ngay);
  }
  const mo = (lang === "en" ? x.mo_ta_en : x.mo_ta).filter((m) => m.nhom !== "khong_dung");
  ["tang_1", "tang_2"].forEach((tang) => {
    const dong = mo.filter((m) => m.nhom === tang);
    if (!dong.length) return;
    const h5 = document.createElement("h5");
    h5.textContent = x.tang[tang][lang];
    const ol = document.createElement("ol");
    ol.dataset.tang = tang;
    dong.forEach((m) => {
      const li = document.createElement("li");
      li.textContent = m.chu;
      ol.appendChild(li);
    });
    the.appendChild(h5);
    the.appendChild(ol);
  });
  return the;
}

function gt2SsNhanBuoi(buoi) {
  return !buoi || buoi === BUOI_MAC_DINH ? t("gt2_ss_buoi_mac_dinh") : nhanBuoi(buoi);
}

function gt2SsVeKetQua() {
  const kq = gt2SsKq;
  const khung = el("gt2ThuKetQua");
  clear(khung);
  if (!kq) return;
  const lang = gt2TcLang();
  const la = gt2SsNhan(kq.a);
  const lb = gt2SsNhan(kq.b);
  const them = (cap) => cap.forEach((n) => khung.appendChild(n));
  const tg = document.createElement("p");                    /* một câu, chỉ có số (do backend dựng: tieu_chi.tom_tat_so_sanh) */
  tg.className = "gt2-tom-tat";
  tg.id = "gt2SsKetLuan";
  tg.textContent = kq.tom_tat[lang];
  khung.appendChild(tg);
  const luoi = document.createElement("div");
  luoi.className = "gt2-luoi-lan";
  luoi.appendChild(gt2SsTheLan(kq.a));
  luoi.appendChild(gt2SsTheLan(kq.b));
  khung.appendChild(luoi);
  const ta = kq.tong.a;
  const tb = kq.tong.b;
  const dong = [
    ["gt2_ss_n", "n", ""], ["gt2_ss_da_xep", "da_xep", ""], ["gt2_ss_chua_xep", "chua_xep", ""],
    ["gt2_ss_pct_da_xep", "pct_da_xep", "%"], ["gt2_ss_pct_nv1", "pct_nv1", "%"], ["gt2_ss_pct_top3", "pct_top3", "%"],
    ["gt2_ss_hang_tb", "hang_tb", ""],
  ].map(([k, f, hau]) => [t(k), { v: ta[f], hau: hau }, { v: tb[f], a: ta[f], hau: hau }]);
  them(gt2SsBang(t("gt2_ss_tong"), [t("gt2_ss_chi_so"), la, lb], dong));
  them(gt2SsBang(t("gt2_ss_clb"),
    [t("gt2_ss_ten_clb"), t("gt2_ss_suc_chua"), t("gt2_ss_nhan") + " — " + la, t("gt2_ss_nhan") + " — " + lb,
      t("gt2_ss_chuan") + " — " + la, t("gt2_ss_chuan") + " — " + lb],
    kq.clb.map((c) => [c.ten, { v: c.suc_chua }, { v: c.a.da_nhan }, { v: c.b.da_nhan, a: c.a.da_nhan },
      { v: c.a.diem_chuan }, { v: c.b.diem_chuan, a: c.a.diem_chuan }])));
  const dauNhom = (ten) => [ten, t("gt2_ss_n"), t("gt2_ss_pct_da_xep") + " — " + la, t("gt2_ss_pct_da_xep") + " — " + lb,
    t("gt2_ss_pct_nv1") + " — " + la, t("gt2_ss_pct_nv1") + " — " + lb];
  const dongNhom = (ds, trong) => ds.map((x) => [x.khoa || t(trong), { v: x.a.n },
    { v: x.a.pct_da_xep, hau: "%" }, { v: x.b.pct_da_xep, a: x.a.pct_da_xep, hau: "%" },
    { v: x.a.pct_nv1, hau: "%" }, { v: x.b.pct_nv1, a: x.a.pct_nv1, hau: "%" }]);
  them(gt2SsBang(t("gt2_ss_nhom_tieu_de"), dauNhom(t("gt2_ss_nhom")), dongNhom(kq.nhom, "gt2_ss_khong_nhom")));
  them(gt2SsBang(t("gt2_ss_lop_tieu_de"), dauNhom(t("gt2_ss_lop")), dongNhom(kq.lop, "gt2_ss_khong_lop")));
  /* Danh sách học sinh đổi chỗ: gập mặc định, nút hiện số dòng; cột Buổi chỉ khi có nhiều buổi. */
  const chua = t("gt2_ss_chua_co_cho");
  const nhieuBuoi = (kq.buoi_chung || []).length > 1;
  const dauDoi = [t("gt2_ss_ma"), t("gt2_ss_ho_ten"), t("gt2_ss_lop")].concat(nhieuBuoi ? [t("gt2_ss_buoi")] : []).concat([la, lb]);
  const dongDoi = kq.doi.slice(0, GT2_SS_DOI_TOI_DA).map((d) => [d.student_id, d.ten, d.lop]
    .concat(nhieuBuoi ? [gt2SsNhanBuoi(d.buoi)] : []).concat([d.tu_ten || chua, d.den_ten || chua]));
  const [hDoi, bangDoi] = gt2SsBang(t("gt2_ss_doi_tieu_de", { n: kq.so_doi }), dauDoi, dongDoi);
  bangDoi.id = "gt2SsDoiBang";
  bangDoi.hidden = true;
  const nut = document.createElement("button");
  nut.type = "button";
  nut.id = "gt2SsDoiNut";
  nut.className = "btn btn-secondary";
  nut.setAttribute("aria-expanded", "false");
  nut.setAttribute("aria-controls", "gt2SsDoiBang");
  const veNut = () => { nut.textContent = t(bangDoi.hidden ? "gt2_ss_hien_ds" : "gt2_ss_an_ds", { n: kq.so_doi }); };
  veNut();
  nut.addEventListener("click", () => {
    bangDoi.hidden = !bangDoi.hidden;
    nut.setAttribute("aria-expanded", bangDoi.hidden ? "false" : "true");
    veNut();
  });
  khung.appendChild(hDoi);
  khung.appendChild(nut);
  khung.appendChild(bangDoi);
  if (kq.doi.length > GT2_SS_DOI_TOI_DA) {
    const p = document.createElement("p");
    p.className = "hint-text";
    p.textContent = t("gt2_ss_con_nua", { n: kq.doi.length - GT2_SS_DOI_TOI_DA });
    khung.appendChild(p);
  }
}

function gt2SsChon() {
  return [Number(el("gt2ThuA").value), Number(el("gt2ThuB").value)];
}

function gt2SsSoSanh() {
  const [a, b] = gt2SsChon();
  return callApi("so_sanh_lan_chay", a, b).then((res) => {
    if (!res.ok) {
      gt2SsKq = null;
      gt2SsVeKetQua();
      feedbackErrors(el("gt2ThuPhanHoi"), res.errors);
      return;
    }
    gt2SsKq = res.data;
    gt2SsVeKetQua();
  });
}

function gt2SsChayThu() {
  return chayNut(el("gt2ThuChay"), () => callApi("run_thu", gt2TcLuatDangChon()), (res) => {
    const o = el("gt2ThuPhanHoi");
    if (!res.ok) {
      feedbackErrors(o, res.errors);
      return;
    }
    feedback(o, t("gt2_thu_da_chay"), false);
    return gt2SsTai(true).then(() => gt2SsSoSanh());
  });
}

function gt2SsXuat(ham, khoaMuc) {
  const [a, b] = gt2SsChon();
  chayXuat([[khoaMuc, ham, ["", a, b], (d) => t("gt2_thu_da_xuat", { path: d.path })]], el("gt2ThuXuat"));
}

function khoiTaoThuCauHinh() {
  el("gt2ThuChay").addEventListener("click", gt2SsChayThu);
  el("gt2ThuSoSanh").addEventListener("click", () => chayNut(el("gt2ThuSoSanh"), () => gt2SsSoSanh(), () => {}));
  el("gt2ThuXuatHtml").addEventListener("click", () => gt2SsXuat("export_so_sanh_html", "gt2_thu_xuat_html"));
  el("gt2ThuXuatCsv").addEventListener("click", () => gt2SsXuat("export_so_sanh_csv", "gt2_thu_xuat_csv"));
  window.addEventListener("langchange", () => {
    el("gt2ThuApDungXacNhan").hidden = true;
    gt2AdVeDanhSach();
    gt2SsVeLuaChon();
    gt2SsVeKetQua();
  });
}

function khoiTaoTieuChi() {
  khoiTaoThuCauHinh();
  el("gt2TcLuu").addEventListener("click", gt2TcLuu);
  ["gt2TcPriority", "gt2TcTierMode"].forEach((id) => el(id).addEventListener("change", gt2CanhBao));
  el("gt2TcTiers").addEventListener("input", gt2CanhBao);
  window.addEventListener("langchange", () => {
    gt2TcVeDanhSach();
    gt2TcVeDieuKhien();
    if (gt2TcDuLieu) gt2TcDatGiaTri();
    gt2CanhBao();
  });
}
