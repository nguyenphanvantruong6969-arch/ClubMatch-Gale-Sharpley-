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
function gt2TcDongBoWharton() {
  const o = el("gt2TcWharton");
  const khong = el("gt2TcPriority").value === "tier" || el("gt2TcScoreScope").value === "per_person";
  if (khong) o.checked = false;
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
    gt2TcDongBoWharton();
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

function khoiTaoTieuChi() {
  el("gt2TcLuu").addEventListener("click", gt2TcLuu);
  ["gt2TcPriority", "gt2TcScoreScope"].forEach((id) => el(id).addEventListener("change", gt2TcDongBoWharton));
  window.addEventListener("langchange", () => {
    gt2TcVeDanhSach();
    gt2TcVeDieuKhien();
    if (gt2TcDuLieu) { gt2TcDatGiaTri(); gt2TcDongBoWharton(); }
  });
}
