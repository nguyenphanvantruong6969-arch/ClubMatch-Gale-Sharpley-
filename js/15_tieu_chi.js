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
  hop.hidden = !kd.length;
  hop.textContent = kd.length ? t("gt2_tc_khong_dung") + " " + kd.map((m) => m.chu).join(" ") : "";
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
  el("gt2TcWhartonNhan").textContent = d.lua_chon.wharton.tieu_de[lang];
}

function gt2TcDatGiaTri() {
  const d = gt2TcDuLieu;
  el("gt2TcTiers").value = (d.luat.tiers || []).join("\n");
  el("gt2TcWharton").checked = d.luat.wharton === true;
}

/* Điểm quyết tâm chỉ dùng được khi xếp theo điểm và tính điểm theo từng suất; ngoài ra tự tắt. */
let gt2TcWhartonTruoc = null; /* giá trị ô trước khi bị tắt tự động, để trả lại khi chọn lại */
function gt2TcDongBoWharton(datLai) {
  const o = el("gt2TcWharton");
  if (datLai === true) gt2TcWhartonTruoc = null;
  const khong = el("gt2TcPriority").value === "tier" || el("gt2TcScoreScope").value === "per_person";
  if (khong && !o.disabled) gt2TcWhartonTruoc = o.checked;
  if (khong) o.checked = false;
  else if (o.disabled) {
    const daLuu = !!(gt2TcDuLieu && gt2TcDuLieu.luat && gt2TcDuLieu.luat.wharton === true);
    o.checked = gt2TcWhartonTruoc === null ? daLuu : gt2TcWhartonTruoc;
    gt2TcWhartonTruoc = null;
  }
  o.disabled = khong;
  const goiY = el("gt2TcWhartonGoiY");
  const fa = !!(gt2TcDuLieu && gt2TcDuLieu.luat && gt2TcDuLieu.luat.fa_daa);
  goiY.textContent = khong ? t(fa ? "gt2_tc_wharton_tat_fa" : "gt2_tc_wharton_tat") : "";
  goiY.hidden = !khong;
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
    gt2TcDongBoWharton(true);
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
    wharton: el("gt2TcWharton").checked,
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

function gt2SsTai(chonLai) {
  return callApi("list_lan_chay").then((res) => {
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    gt2SsDs = res.data;
    gt2SsVeLuaChon();
    if (chonLai && gt2SsDs.chinh_thuc) {
      el("gt2ThuB").value = String(gt2SsDs.chinh_thuc.run_id);
      if (gt2SsDs.thu.length) el("gt2ThuA").value = String(gt2SsDs.thu[0].run_id);
    }
  });
}

function gt2SsBang(tieuDe, dau, dong) {
  const h = document.createElement("h3");
  h.textContent = tieuDe;
  const bang = document.createElement("table");
  bang.className = "data-table";
  const hd = document.createElement("thead");
  const tr = document.createElement("tr");
  dau.forEach((c) => {
    const th = document.createElement("th");
    th.textContent = c;
    tr.appendChild(th);
  });
  hd.appendChild(tr);
  bang.appendChild(hd);
  const tb = document.createElement("tbody");
  dong.forEach((d) => {
    const r = document.createElement("tr");
    d.forEach((c) => {
      const td = document.createElement("td");
      td.textContent = c === null || c === undefined ? "—" : String(c).replace(".", ",");
      r.appendChild(td);
    });
    tb.appendChild(r);
  });
  bang.appendChild(tb);
  return [h, bang];
}

const GT2_SS_DOI_TOI_DA = 200;

function gt2SsVeKetQua() {
  const kq = gt2SsKq;
  const khung = el("gt2ThuKetQua");
  clear(khung);
  if (!kq) return;
  const lang = gt2TcLang();
  const la = gt2SsNhan(kq.a);
  const lb = gt2SsNhan(kq.b);
  const them = (cap) => cap.forEach((n) => khung.appendChild(n));
  [kq.a, kq.b].forEach((x) => {
    const p = document.createElement("p");
    const dam = document.createElement("b");
    dam.textContent = gt2SsNhan(x) + ": ";
    p.appendChild(dam);
    p.appendChild(document.createTextNode(
      (lang === "en" ? x.mo_ta_en : x.mo_ta).filter((m) => m.nhom !== "khong_dung").map((m) => m.chu).join(" ")));
    khung.appendChild(p);
  });
  const tg = document.createElement("p");
  tg.className = "hint-text";
  tg.id = "gt2SsKetLuan";
  tg.textContent = kq.so_doi ? t("gt2_ss_co_doi", { n: kq.so_doi }) : t("gt2_ss_khong_doi");
  khung.appendChild(tg);
  const ta = kq.tong.a;
  const tb = kq.tong.b;
  const dong = [
    ["gt2_ss_n", ta.n, tb.n], ["gt2_ss_da_xep", ta.da_xep, tb.da_xep], ["gt2_ss_chua_xep", ta.chua_xep, tb.chua_xep],
    ["gt2_ss_pct_da_xep", ta.pct_da_xep, tb.pct_da_xep], ["gt2_ss_pct_nv1", ta.pct_nv1, tb.pct_nv1],
    ["gt2_ss_pct_top3", ta.pct_top3, tb.pct_top3], ["gt2_ss_hang_tb", ta.hang_tb, tb.hang_tb],
  ].map(([k, a, b]) => [t(k), a, b]);
  them(gt2SsBang(t("gt2_ss_tong"), [t("gt2_ss_chi_so"), la, lb], dong));
  them(gt2SsBang(t("gt2_ss_clb"),
    [t("gt2_ss_ten_clb"), t("gt2_ss_suc_chua"), t("gt2_ss_nhan") + " — " + la, t("gt2_ss_nhan") + " — " + lb,
      t("gt2_ss_chuan") + " — " + la, t("gt2_ss_chuan") + " — " + lb],
    kq.clb.map((c) => [c.ten, c.suc_chua, c.a.da_nhan, c.b.da_nhan, c.a.diem_chuan, c.b.diem_chuan])));
  const dauNhom = (ten) => [ten, t("gt2_ss_n"), t("gt2_ss_pct_da_xep") + " — " + la, t("gt2_ss_pct_da_xep") + " — " + lb,
    t("gt2_ss_pct_nv1") + " — " + la, t("gt2_ss_pct_nv1") + " — " + lb];
  const dongNhom = (ds, trong) => ds.map((x) => [x.khoa || t(trong), x.a.n, x.a.pct_da_xep, x.b.pct_da_xep, x.a.pct_nv1, x.b.pct_nv1]);
  them(gt2SsBang(t("gt2_ss_nhom_tieu_de"), dauNhom(t("gt2_ss_nhom")), dongNhom(kq.nhom, "gt2_ss_khong_nhom")));
  them(gt2SsBang(t("gt2_ss_lop_tieu_de"), dauNhom(t("gt2_ss_lop")), dongNhom(kq.lop, "gt2_ss_khong_lop")));
  const chua = t("gt2_ss_chua_co_cho");
  them(gt2SsBang(t("gt2_ss_doi_tieu_de", { n: kq.so_doi }),
    [t("gt2_ss_ma"), t("gt2_ss_ho_ten"), t("gt2_ss_lop"), t("gt2_ss_buoi"), la, lb],
    kq.doi.slice(0, GT2_SS_DOI_TOI_DA).map((d) => [d.student_id, d.ten, d.lop, d.buoi, d.tu_ten || chua, d.den_ten || chua])));
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
    gt2SsVeLuaChon();
    gt2SsVeKetQua();
  });
}

function khoiTaoTieuChi() {
  khoiTaoThuCauHinh();
  el("gt2TcLuu").addEventListener("click", gt2TcLuu);
  ["gt2TcPriority", "gt2TcScoreScope"].forEach((id) => el(id).addEventListener("change", () => gt2TcDongBoWharton()));
  window.addEventListener("langchange", () => {
    gt2TcVeDanhSach();
    gt2TcVeDieuKhien();
    if (gt2TcDuLieu) { gt2TcDatGiaTri(); gt2TcDongBoWharton(); }
  });
}
