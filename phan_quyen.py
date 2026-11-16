"""GT3-L2: cổng phân quyền trung tâm cho `PipelineAPI`.

Một bảng `QUYEN` phân MỌI hàm công khai của `PipelineAPI` vào một trong ba mức:
`cong_khai` (đăng nhập / đăng xuất / hỏi phiên), `giao_vien` (xem, xuất, nhập điểm và điểm danh),
`quan_tri` (mọi thứ ghi dữ liệu, cấu hình, xoá, tài khoản).

Chỉ áp dụng khi bảng `tai_khoan` có ít nhất một dòng. Chưa có tài khoản thì mọi hàm chạy y như trước
(kết quả và ngoại lệ không đổi). Có tài khoản mà hàm KHÔNG có trong bảng thì bị từ chối (đóng khi lỗi).
Hàm bị bọc ở cấp lớp, nên cả pywebview lẫn `browser_host.py` đều đi qua cùng một cổng. Cổng chỉ chặn ở
lời gọi ngoài cùng: hàm công khai gọi hàm công khai khác bên trong thì không kiểm lại.
Chỉ là điều khiển truy cập, không dính `compute_club_priority` (bất biến 2).
"""

import functools
import inspect
import threading
import types

from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail

CONG_KHAI = "cong_khai"
GIAO_VIEN = "giao_vien"
QUAN_TRI = "quan_tri"

# Hàm tự kiểm quyền bên trong (api_tai_khoan.py): tài khoản đầu tiên không cần đăng nhập, v.v.
_CONG_KHAI = ("dang_nhap dang_xuat get_phien_dang_nhap tao_tai_khoan doi_mat_khau").split()

# Chỉ đọc, xuất, và việc của giáo viên (nhập điểm, điểm danh, nhập hộ học sinh tại chỗ, khiếu nại / phản hồi).
_GIAO_VIEN = """
check_data_integrity chuan_hoa_buoi chuan_hoa_nhom_du_tru detect_csv_kind dat_tieu_de_cua_so
export_bang_dang_xem export_bang_nhu_cau export_bien_ban_boc_tham export_csv export_dashboard export_diem_danh
export_du_lieu_dau_vao export_goi_y_chi_tieu export_hoc_sinh_csv export_ket_qua export_khieu_nai
export_ly_do_csv export_phan_hoi export_thay_doi_ket_qua export_theo_lop export_wharton_can_sua
get_bo_bieu_mau get_club_applicants_for_scoring get_club_fill_stats get_danh_sach_buoi get_danh_sach_clb
get_dashboard get_dashboard_status get_data_health_report get_diem_chuan get_diem_chuan_clb get_diem_danh
get_do_phu get_em_chua_co_cho get_fa_duong get_forms_buoc_12 get_forms_nap get_khieu_nai get_last_run_info
get_ly_do_ket_qua get_match_results get_moi_cho_trong get_person_scoring_list get_phan_bo_nguyen_vong
get_phan_hoi_tong_hop get_pipeline_run_warning get_run_history get_scoring_overview get_so_boc_tham_theo_buoi
get_stb_lock_status get_student_entry_state get_suat_du_tru get_tai_theo_buoi get_thay_doi_ket_qua
get_thoi_khoa_bieu get_trang_thai_ket_qua get_vong_2 get_vong_doi_cho get_wharton_lock_status
get_wharton_nhat_ky get_workspace_config get_workspace_state gui_khieu_nai gui_phan_hoi
kiem_chi_tieu_ky_sau lay_so_nhap_nap
list_classes list_clubs list_clubs_admin list_reserve_groups_in_use list_students_admin list_templates
list_wharton_admin list_wharton_canh_bao list_workspaces luu_diem_danh mo_thu_muc nhan_dien_tep_forms
preview_import_csv search_students submit_club_scores submit_huy_chuong submit_person_scores
submit_preferences submit_test_selection tai_mau_de_thi tao_so_nhap_mau xem_truoc_so_nhap xlsx_to_csv_text
xuat_ket_qua_list
""".split()

# Ghi dữ liệu, cấu hình, xoá, đổi chỗ, nạp tệp, tài khoản.
_QUAN_TRI = """
admin_save_wharton ai_chua_dang_ky bulk_set_reserve_group chay_vong_2_api chuyen_tep_forms clear_wharton
create_or_update_club create_student_if_missing create_workspace dat_fa_duong delete_club delete_student
delete_workspace doi_chieu_hai_lan duplicate_workspace export_workspace
import_clubs_csv import_csv_auto import_preferences_csv import_so_nhap import_test_selection_csv
import_workspace liet_ke_tai_khoan luu_gioi_han_gv mo_khoa_wharton nap_de_thi nap_phieu_clb
nhap_phan_hoi_forms nhap_sau_ket_qua_forms open_workspace phong_wharton_hang_loat rename_workspace
reset_data reset_student_entry run_pipeline save_as_template set_student_class set_student_reserve_group
submit_wharton tao_bo_bieu_mau_api tra_loi_moi update_workspace_config xoa_tai_khoan xu_ly_khieu_nai
""".split()

QUYEN = {}
for _ten in _CONG_KHAI:
    QUYEN[_ten] = CONG_KHAI
for _ten in _GIAO_VIEN:
    QUYEN.setdefault(_ten, GIAO_VIEN)
for _ten in _QUAN_TRI:
    QUYEN.setdefault(_ten, QUAN_TRI)
del _ten

_TL = threading.local()


def kiem_quyen(api, ten: str):
    """None nếu được làm; ngược lại phản hồi lỗi đầy đủ `{ok: False, data: None, errors: [...]}`."""
    muc = QUYEN.get(ten)
    if muc == CONG_KHAI:
        return None
    if not api._co_tai_khoan_nho():
        return None
    phien = api._dang_nhap.cham_hoat_dong(api.db_path)       # làm mới giờ nghỉ
    if phien is None:
        return _fail(err("gt3_can_dang_nhap"))
    if muc is None or (muc == QUAN_TRI and phien["vai"] != QUAN_TRI):
        return _fail(err("gt3_khong_du_quyen", hanh_dong=ten))
    return None


def _boc(ten, ham):
    @functools.wraps(ham)
    def cong(self, *args, **kwargs):
        sau = getattr(_TL, "sau", 0)
        if sau == 0:
            loi = kiem_quyen(self, ten)
            if loi is not None:
                return loi
        _TL.sau = sau + 1
        try:
            return ham(self, *args, **kwargs)
        finally:
            _TL.sau = sau
    cong._gt3_cong = True
    cong._gt3_goc = ham
    cong.__signature__ = inspect.signature(ham)
    if "__wrapped__" not in getattr(ham, "__dict__", {}):
        # `__wrapped__` là dấu của lớp bọc hàm ĐỌC (api._xep_hang_doc); hàm ghi không được mang dấu đó.
        del cong.__wrapped__
    return cong


def ap_dung_cong(lop):
    """Bọc mọi hàm công khai của `lop` (trừ mức `cong_khai`). Gọi một lần, ở cuối api.py."""
    for ten in dir(lop):
        if ten.startswith("_") or QUYEN.get(ten) == CONG_KHAI:
            continue
        ham = next((c.__dict__[ten] for c in lop.__mro__ if ten in c.__dict__), None)
        if isinstance(ham, types.FunctionType) and not getattr(ham, "_gt3_cong", False):
            setattr(lop, ten, _boc(ten, ham))
