/* js/2x_phuong_an.js — CB1-L3: khung "Văn bản phương án xếp" ở tab Cách xếp của Quản lý (#paPanel, chỉ quản trị).

   Ba việc: "Chốt phương án" (hộp xác nhận hiện luật sẽ chốt; chốt lại cũng hỏi lại), "Xuất bản dự kiến", "Xuất bản chốt"
   (khoá kèm lý do cho tới khi đủ điều kiện) và ô "In hạt giống" (tắt mặc định; chỉ bật được cho bản chốt khi số bốc thăm
   đã khoá). Chỉ giao diện: dữ liệu và luật nằm ở backend (get_phuong_an_xep, chot_phuong_an, export_van_ban_phuong_an_pdf).
   Script thường (không ES module). */
"use strict";

let paDuLieu = null;
let paLan = 0;

function paBo() { const b = el("paXacNhan"); if (b) { b.hidden = true; clear(b); } }

function paVe() {
  const d = paDuLieu;
  if (!d) return;
  const tt = el("paTrangThai");
  if (!d.co_chot) tt.textContent = t("cb1_chua_chot");
  else if (d.chot && d.chot.nguoi) tt.textContent = t("cb1_da_chot", { nguoi: d.chot.nguoi, luc: d.chot.luc });
  else tt.textContent = t("cb1_da_chot_an", { luc: d.chot ? d.chot.luc : "" });
  const cb = el("paCanhBao");
  clear(cb);
  (d.canh_bao || []).forEach((ma) => {
    const p = document.createElement("p");
    p.textContent = t("cb1_canh_bao_" + ma);
    cb.appendChild(p);
  });
  cb.hidden = !(d.canh_bao || []).length;
  el("paChot").textContent = t(d.co_chot ? "cb1_chot_lai" : "cb1_chot");
  const chotDuoc = !!d.co_the_xuat.chot;
  el("paXuatChot").disabled = !chotDuoc;
  el("paLyDo").textContent = chotDuoc ? "" : t("cb1_ly_do_chot");
  el("paLyDo").hidden = chotDuoc;
  const hat = el("paHatGiong");
  const hatDuoc = chotDuoc && !!d.co_the_in_hat_giong;
  hat.disabled = !hatDuoc;
  if (!hatDuoc) hat.checked = false;
  el("paLyDoHat").textContent = hatDuoc ? t("cb1_ghi_chu_hat") : t("cb1_ly_do_hat");
}

function paTai() {
  /* Giáo viên không thấy khung này và backend từ chối: không gọi để khỏi để lại dòng "bị từ chối" trong nhật ký. */
  if (!el("paPanel") || document.body.dataset.vai === "giao_vien") return Promise.resolve();
  const lan = ++paLan;
  return callApi("get_phuong_an_xep").then((res) => {
    if (lan !== paLan) return;
    if (!res.ok) {
      const o = el("paTrangThai");
      o.textContent = trErrs(res.errors).join(" ");
      return;
    }
    paDuLieu = res.data;
    paVe();
  }).catch(baoLoiGiaoDien);
}

function paHoiChot() {
  const d = paDuLieu;
  if (!d) return;
  const bar = el("paXacNhan");
  clear(bar);
  const hoi = document.createElement("p");
  hoi.textContent = t(d.co_chot ? "cb1_xac_nhan_lai" : "cb1_xac_nhan");
  const ds = document.createElement("ul");
  if (d.muc_tieu) {
    const li = document.createElement("li");
    li.textContent = t("cb1_muc_tieu", { ten: d.muc_tieu.tieu_de });
    ds.appendChild(li);
  }
  (d.tom_tat_luat || []).forEach((c) => {
    const li = document.createElement("li");
    li.textContent = c;
    ds.appendChild(li);
  });
  const dongY = document.createElement("button");
  dongY.type = "button";
  dongY.className = "btn btn-primary";
  dongY.id = "paXacNhanChot";
  dongY.textContent = t("cb1_chot_nut");
  const huy = document.createElement("button");
  huy.type = "button";
  huy.className = "btn btn-ghost";
  huy.id = "paHuy";
  huy.textContent = t("btn_cancel");
  dongY.addEventListener("click", () => chayNut(dongY, () => callApi("chot_phuong_an"), (res) => {
    paBo();
    if (res.ok) { feedback(el("paPhanHoi"), t("cb1_da_chot_xong"), false); return paTai(); }
    feedbackErrors(el("paPhanHoi"), res.errors);
  }));
  huy.addEventListener("click", () => { paBo(); el("paChot").focus(); });
  bar.addEventListener("keydown", (ev) => { if (ev.key === "Escape") { paBo(); el("paChot").focus(); } });
  bar.append(hoi, ds, dongY, huy);
  bar.hidden = false;
  huy.focus();
}

function paXuat(ban) {
  const hat = ban === "chot" && el("paHatGiong").checked;
  chayXuat([["cb1_tieu_de", "export_van_ban_phuong_an_pdf", ["", ban, hat],
    (d) => t("cb1_da_xuat", { path: d.path })]], el("paPhanHoi"));
}

function initPhuongAn() {
  if (!el("paPanel")) return;
  el("paChot").addEventListener("click", paHoiChot);
  el("paXuatDuKien").addEventListener("click", () => paXuat("du_kien"));
  el("paXuatChot").addEventListener("click", () => paXuat("chot"));
  el("paPanel").addEventListener("pointerenter", () => { paTai(); });
  window.addEventListener("langchange", paVe);
  paTai();
}
