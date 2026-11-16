"""GT3-L1: tài khoản và đăng nhập (hai vai `quan_tri` / `giao_vien`).

Một phần của PipelineAPI (xem api.py). Bảng `tai_khoan` rỗng thì mọi thứ chạy y như trước:
không màn đăng nhập, không ghi thêm gì. Phiên đăng nhập nằm TRONG BỘ NHỚ của tiến trình
(kiosk chỉ có một tiến trình), gắn với đường dẫn CSDL đang mở — đổi workspace là phiên cũ hết hiệu lực.

Mật khẩu / băm / muối KHÔNG BAO GIỜ được trả ra, ghi nhật ký hay đưa vào tham số lỗi.
Gạch dưới đầu tên = pywebview không phơi ra giao diện (xem test_do_api).
"""

import sqlite3
import time

import tai_khoan as tk
from rbda_priority_pipeline import connect_db
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok

# Tên cố định, dùng để làm một lần băm "giả" khi tên không tồn tại (cùng thời gian phản hồi).
# Chờ khoá tối đa khi cổng L2 làm mới "có tài khoản không" (đã có giá trị cũ để dùng).
_CHO_KHOA_CONG_MS = 50
# Làm mới thất bại vì khoá thì 5 giây sau mới thử lại: CSDL bận lâu không bị cộng thêm chờ ở MỖI lời gọi.
_LUI_LAI_CONG_GIAY = 5.0
_MAT_KHAU_GIA = "khong-ton-tai-0"


class TaiKhoanMixin:
    def _khoi_tao_tai_khoan(self) -> None:
        # Đồng hồ tiêm được: test thay `api._dong_ho` bằng đồng hồ giả.
        self._dong_ho = time.monotonic
        self._dang_nhap = tk.TrangThaiDangNhap(lambda: self._dong_ho())
        self._co_tk_lui = {}           # {đường dẫn CSDL: mốc monotonic trước đó không làm mới lại}
        self._co_tk_nho = {}           # {đường dẫn CSDL: có tài khoản?} — lần đọc thành công gần nhất (cổng L2)

    # ------------------------------------------------------------- nội bộ
    def _co_tai_khoan(self) -> bool:
        with self._ket_noi_doc() as cur:
            return tk.dem_tai_khoan(cur) > 0

    def _co_tai_khoan_nho(self) -> bool:
        """Cho cổng phân quyền (L2): như `_co_tai_khoan` nhưng không bao giờ ném lỗi.

        Chưa có bảng `tai_khoan` = chưa có tài khoản. Đọc hỏng (CSDL tạm bận...) thì dùng lần đọc thành công gần nhất
        CỦA CSDL ĐANG MỞ; CSDL này chưa từng đọc được thì coi như ĐÃ CÓ tài khoản (đóng khi lỗi, không để lọt cổng).
        """
        db = self.db_path
        try:
            if db in self._co_tk_nho and getattr(self._giao_dich, "conn", None) is None:
                # Đã có giá trị đọc được của CSDL này: làm mới với thời gian chờ khoá NGẮN (CSDL đang bận thì
                # dùng giá trị cũ, cổng không cộng thêm thời gian chờ vào lời gọi).
                if time.monotonic() < self._co_tk_lui.get(db, 0.0):
                    return self._co_tk_nho[db]
                try:
                    conn = connect_db(db, cho_khoa_ms=_CHO_KHOA_CONG_MS)
                    try:
                        co = tk.dem_tai_khoan(conn.cursor()) > 0
                    finally:
                        conn.close()
                except sqlite3.OperationalError as e:
                    if "no such table" not in str(e):
                        self._co_tk_lui[db] = time.monotonic() + _LUI_LAI_CONG_GIAY
                        return self._co_tk_nho[db]
                    co = False
            else:
                co = self._co_tai_khoan()
        except sqlite3.OperationalError as e:
            if "no such table" not in str(e):
                return self._co_tk_nho.get(db, True)
            co = False
        except Exception:
            return self._co_tk_nho.get(db, True)
        self._co_tk_nho[db] = co
        return co

    def _hoat_dong(self) -> bool:
        """Dùng cho cổng phân quyền (L2): có thể làm thao tác không, và làm mới giờ nghỉ.

        True khi chưa có tài khoản nào (phần mềm chạy như cũ) hoặc phiên còn hạn; False khi cần đăng nhập.
        """
        if not self._co_tai_khoan():
            return True
        return self._dang_nhap.cham_hoat_dong(self.db_path) is not None

    def _phien_can_co(self, can_quan_tri: bool):
        """`(phien, None)` nếu đủ điều kiện, ngược lại `(None, err)`. Làm mới giờ nghỉ khi hợp lệ."""
        phien = self._dang_nhap.cham_hoat_dong(self.db_path)
        if phien is None:
            return None, err("gt3_can_dang_nhap")
        if can_quan_tri and phien["vai"] != tk.VAI_QUAN_TRI:
            return None, err("gt3_khong_du_quyen")
        return phien, None

    def _bao_lock(self, ten: str):
        giay = self._dang_nhap.giay_con_khoa(ten)
        return err("gt3_tam_khoa", giay=giay) if giay > 0 else None

    def _ghi_sai(self, ten: str):
        """Ghi một lần sai; trả lỗi `gt3_tam_khoa` nếu vừa đủ 5 lần, ngược lại None."""
        giay = self._dang_nhap.ghi_sai(ten)
        return err("gt3_tam_khoa", giay=giay) if giay > 0 else None

    # --------------------------------------------------------------- đọc
    def get_phien_dang_nhap(self):
        """Trạng thái đăng nhập cho giao diện. KHÔNG làm mới giờ nghỉ (giao diện hỏi định kỳ)."""
        try:
            co = self._co_tai_khoan()
            phien = self._dang_nhap.phien_hien_tai(self.db_path) if co else None
            d = {"co_tai_khoan": co, "dang_nhap": phien is not None, "ten": None, "vai": None}
            if phien is not None:
                d["ten"], d["vai"] = phien["ten"], phien["vai"]
            return _ok(d)
        except Exception as e:
            return _fail(err("gt3_loi_tai_khoan", detail=str(e)))

    def liet_ke_tai_khoan(self):
        """Danh sách tài khoản (tên, vai, ngày tạo) — chỉ quản trị."""
        try:
            _, loi = self._phien_can_co(True)
            if loi:
                return _fail(loi)
            with self._ket_noi_doc() as cur:
                return _ok(tk.liet_ke(cur))
        except Exception as e:
            return _fail(err("gt3_loi_tai_khoan", detail=str(e)))

    # --------------------------------------------------------------- ghi
    def tao_tai_khoan(self, ten, mat_khau, vai):
        """Tạo tài khoản. Tài khoản ĐẦU TIÊN phải là quản trị và không cần đăng nhập
        (người tạo được đăng nhập luôn); các tài khoản sau cần phiên quản trị."""
        try:
            ten_sach = tk.chuan_hoa_ten(ten)
            if ten_sach is None:
                return _fail(err("gt3_ten_khong_hop_le", toi_da=tk.TEN_TOI_DA))
            if vai not in tk.CAC_VAI:
                return _fail(err("gt3_vai_khong_hop_le"))
            if not tk.mat_khau_hop_le(mat_khau):
                return _fail(err("gt3_mat_khau_ngan", toi_thieu=tk.MAT_KHAU_TOI_THIEU))
            with self._ket_noi_ghi() as cur:
                dau_tien = tk.dem_tai_khoan(cur) == 0
                if dau_tien:
                    if vai != tk.VAI_QUAN_TRI:
                        return _fail(err("gt3_tai_khoan_dau_phai_quan_tri"))
                else:
                    _, loi = self._phien_can_co(True)
                    if loi:
                        return _fail(loi)
                if tk.tim_ten(cur, ten_sach) is not None:
                    return _fail(err("gt3_ten_da_co"))
                try:
                    tk.them(cur, ten_sach, mat_khau, vai)
                except sqlite3.IntegrityError:
                    return _fail(err("gt3_ten_da_co"))
            self._co_tk_nho[self.db_path] = True          # có tài khoản rồi (xoá không bao giờ về 0: giữ quản trị cuối)
            self._co_tk_lui.pop(self.db_path, None)
            if dau_tien:
                self._dang_nhap.bat_dau(ten_sach, vai, self.db_path)
            return _ok({"ten": ten_sach, "vai": vai})
        except Exception as e:
            return _fail(err("gt3_loi_tai_khoan", detail=str(e)))

    def dang_nhap(self, ten, mat_khau):
        try:
            ten_sach = tk.chuan_hoa_ten(ten)
            if not self._co_tai_khoan():
                return _fail(err("gt3_chua_co_tai_khoan"))
            if ten_sach is None or not isinstance(mat_khau, str):
                return _fail(err("gt3_sai_thong_tin"))
            loi = self._bao_lock(ten_sach)
            if loi:
                return _fail(loi)
            with self._ket_noi_doc() as cur:
                dong = tk.lay(cur, ten_sach)
            if dong is None:
                tk.bam_mat_khau(_MAT_KHAU_GIA)          # cùng thời gian phản hồi, không lộ tên có tồn tại
                dung = False
            else:
                dung = tk.kiem_tra_mat_khau(mat_khau, dong[2], dong[3])
            if not dung:
                return _fail(self._ghi_sai(ten_sach) or err("gt3_sai_thong_tin"))
            self._dang_nhap.xoa_dem(ten_sach)
            self._dang_nhap.bat_dau(dong[0], dong[1], self.db_path)
            return _ok({"ten": dong[0], "vai": dong[1]})
        except Exception as e:
            return _fail(err("gt3_loi_tai_khoan", detail=str(e)))

    def dang_xuat(self):
        self._dang_nhap.ket_thuc()
        return _ok(None)

    def doi_mat_khau(self, cu, moi):
        """Người đang đăng nhập tự đổi mật khẩu của mình."""
        try:
            phien, loi = self._phien_can_co(False)
            if loi:
                return _fail(loi)
            ten = phien["ten"]
            loi = self._bao_lock(ten)
            if loi:
                return _fail(loi)
            if not tk.mat_khau_hop_le(moi):
                return _fail(err("gt3_mat_khau_ngan", toi_thieu=tk.MAT_KHAU_TOI_THIEU))
            with self._ket_noi_ghi() as cur:
                dong = tk.lay(cur, ten)
                if dong is None or not isinstance(cu, str) or not tk.kiem_tra_mat_khau(cu, dong[2], dong[3]):
                    return _fail(self._ghi_sai(ten) or err("gt3_sai_thong_tin"))
                tk.dat_mat_khau(cur, dong[0], moi)
            self._dang_nhap.xoa_dem(ten)
            return _ok(None)
        except Exception as e:
            return _fail(err("gt3_loi_tai_khoan", detail=str(e)))

    def xoa_tai_khoan(self, ten):
        """Xoá một tài khoản (quản trị). Không bao giờ xoá quản trị cuối cùng."""
        try:
            phien, loi = self._phien_can_co(True)
            if loi:
                return _fail(loi)
            ten_sach = tk.chuan_hoa_ten(ten)
            with self._ket_noi_ghi() as cur:
                dong = tk.lay(cur, ten_sach) if ten_sach else None
                if dong is None:
                    return _fail(err("gt3_khong_thay_tai_khoan"))
                if dong[1] == tk.VAI_QUAN_TRI and tk.dem_quan_tri(cur) <= 1:
                    return _fail(err("gt3_khong_xoa_quan_tri_cuoi"))
                tk.xoa(cur, dong[0])
            if dong[0] == phien["ten"]:
                self._dang_nhap.ket_thuc()
            return _ok(None)
        except Exception as e:
            return _fail(err("gt3_loi_tai_khoan", detail=str(e)))
