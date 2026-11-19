/* js/19_ux1b_gv.js — UX1B-L4-B: khối "Theo {cohort_l} và báo cáo" ở đầu thẻ Kết quả (#ux1bPanel).
   Chọn {cohort_l} (mở bảng Theo {cohort_l} của lớp đó), "Xuất theo {cohort_l}" (export_theo_lop) và
   "Báo cáo tổng hợp" (export_bao_cao_tong_hop, HTML). Dùng lại chayXuat; không ghi dữ liệu. Script thường. */
"use strict";

function ux1bNapLop() {
  return callApi("list_classes").then((res) => {
    const sel = el("ux1bLop");
    const dangChon = sel.value;
    clear(sel);
    if (res.ok) res.data.classes.forEach((c) => themOption(sel, c.class_id, c.class_id + " (" + c.n + ")"));
    if (dangChon && Array.from(sel.options).some((o) => o.value === dangChon)) sel.value = dangChon;
    sel.disabled = !sel.options.length;
  });
}

function ux1bChonLop() {
  const v = el("ux1bLop").value;
  if (!v) return;
  const nut = document.querySelector('#kqTang1 [data-kq="lop"]');
  if (nut && !nut.hidden) nut.click();
  const o = el("kqChonLop");
  o.value = v;
  o.dispatchEvent(new Event("change"));
}

el("ux1bLop").addEventListener("change", ux1bChonLop);
el("btnUx1bXuatLop").addEventListener("click", () => {
  chayXuat([["xuat_muc_theo_lop", "export_theo_lop", [""],
    (d) => t("xuat_kq_theo_lop", { n: d.n_tep, path: d.thu_muc })]], el("ux1bPhanHoi"));
});
el("btnUx1bBaoCao").addEventListener("click", () => {
  chayXuat([["ux1b_xuat_muc_bao_cao", "export_bao_cao_tong_hop", [""],
    (d) => t("ux1b_xuat_kq_bao_cao", { path: d.path })]], el("ux1bPhanHoi"));
});
document.querySelector('.nav-item[data-tab="results"]').addEventListener("click", ux1bNapLop);
ux1bNapLop();

/* UX1B-L5c: lối thẳng tới khung Cài đặt (thẻ Quản lý, nơi có nút "Quay lại Chia 100 điểm"). Dùng ở thanh "Việc tiếp theo"
   và dòng gộp cảnh báo huy chương. Giáo viên không có thẻ này nên nút chỉ hiện cho quản trị (backend vẫn kiểm quyền). */
function ux1bMoCaiDat() {
  switchTab("admin");
  viecChoRoiLam(() => { const p = el("ux1aCaiDat"); return p && !p.hidden; }, () => {
    el("ux1aCaiDat").scrollIntoView({ block: "start" });
  });
}
