/* js/19_ux1b_gv.js — UX1B-L4-B: khối "Theo {cohort_l} và báo cáo" ở đầu thẻ Kết quả (#ux1bPanel).
   Ô chọn lớp là #kqChonLop (mở bảng Theo {cohort_l} của lớp đó), "Xuất theo {cohort_l}" (export_theo_lop) và
   "Báo cáo tổng hợp" (export_bao_cao_tong_hop, HTML; PDF: export_bao_cao_tong_hop_pdf) và "In phiếu cả {cohort_l}" (PDF). Dùng lại chayXuat; không ghi dữ liệu. Script thường. */
"use strict";

/* UX1F-L4: MỘT ô chọn lớp (#kqChonLop, nạp ở js/09_the_xem.js) dùng cho cả bảng kết quả và "In phiếu cả {cohort_l}".
   "Chưa có lớp" (giá trị rỗng) không phải một lớp để in cả phiếu: nút tạm tắt. */
function ux1bDongBoNut() {
  el("btnUx1bPhieuLop").disabled = !el("kqChonLop").value;
}

el("btnUx1bXuatLop").addEventListener("click", () => {
  chayXuat([["xuat_muc_theo_lop", "export_theo_lop", [""],
    (d) => t("xuat_kq_theo_lop", { n: d.n_tep, path: d.thu_muc })]], el("ux1bPhanHoi"));
});
el("btnUx1bBaoCao").addEventListener("click", () => {
  chayXuat([["ux1b_xuat_muc_bao_cao", "export_bao_cao_tong_hop", [""],
    (d) => t("ux1b_xuat_kq_bao_cao", { path: d.path })]], el("ux1bPhanHoi"));
});
/* UX1I-I3: giáo viên chủ nhiệm in phiếu cả {cohort_l} đang chọn (MỘT tệp PDF của lớp đó) và lấy báo cáo tổng hợp dạng PDF. */
el("btnUx1bPhieuLop").addEventListener("click", () => {
  const lop = el("kqChonLop").value;
  if (!lop) return;
  chayXuat([["ux1i_xuat_muc_phieu_lop", "export_phieu_giai_trinh_pdf", ["", lop, false],
    (d) => t("xp1_kq_mot_tep", { n: d.n_trang, path: d.path })]], el("ux1bPhanHoi"));
});
el("btnUx1bBaoCaoPdf").addEventListener("click", () => {
  chayXuat([["ux1b_xuat_muc_bao_cao", "export_bao_cao_tong_hop_pdf", [""],
    (d) => t("ux1i_xuat_kq_bao_cao_pdf", { n: d.n_trang, path: d.path })]], el("ux1bPhanHoi"));
});
ux1bDongBoNut();

/* UX1B-L5c: lối thẳng tới khung Cài đặt (thẻ Quản lý, nơi có nút "Quay lại Chia 100 điểm"). Dùng ở thanh "Việc tiếp theo"
   và dòng gộp cảnh báo huy chương. Giáo viên không có thẻ này nên nút chỉ hiện cho quản trị (backend vẫn kiểm quyền). */
function ux1bMoCaiDat() {
  switchTab("admin");
  viecChoRoiLam(() => { const p = el("ux1aCaiDat"); return p && !p.hidden; }, () => {
    el("ux1aCaiDat").scrollIntoView({ block: "start" });
  });
}
