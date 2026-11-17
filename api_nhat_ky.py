"""GT3-L3: xem và xuất nhật ký thao tác (chỉ quản trị). Ghi dòng nhật ký nằm ở `phan_quyen.py` (một chỗ duy nhất)."""

import nhat_ky as nk
from api_chung import _ghi_csv
from api_workspace import LoiDuongXuat
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok


class NhatKyMixin:
    def get_nhat_ky_thao_tac(self, page=1, page_size=50, nguoi=None, hanh_dong=None, chi_tu_choi=False, ngay=None):
        """Một trang nhật ký, MỚI NHẤT TRƯỚC: `{dong: [...], tong, page, page_size, so_trang, hanh_dong_co}`.
        `chi_tu_choi`: chỉ dòng có kết quả khác `ok`; `ngay`: `YYYY-MM-DD` (sai dạng: `gt4_ngay_sai`);
        `hanh_dong_co`: các tên hành động có trong nhật ký (cho ô chọn lọc)."""
        try:
            with self._ket_noi_doc() as cur:
                dong, tong, page, page_size = nk.doc_trang(cur, page, page_size, nguoi, hanh_dong, chi_tu_choi, ngay)
                co = nk.hanh_dong_co(cur)
            return _ok({"dong": dong, "tong": tong, "page": page, "page_size": page_size,
                        "so_trang": max(1, -(-tong // page_size)), "hanh_dong_co": co})
        except ValueError:
            return _fail(err("gt4_ngay_sai"))
        except Exception as e:
            return _fail(err("gt3_loi_nhat_ky", detail=str(e)))

    def export_nhat_ky_thao_tac_csv(self, path: str = "", nguoi=None, hanh_dong=None, chi_tu_choi=False, ngay=None):
        """`nhat_ky_thao_tac.csv` (UTF-8 có BOM, chặn công thức), cũ nhất trước, dạng THÔ (tên hành động và mã kết
        quả nguyên văn, không nhãn tiếng Việt). Trả `{path, n_rows}`."""
        try:
            with self._ket_noi_doc() as cur:
                dong = nk.doc_het(cur, nguoi, hanh_dong, chi_tu_choi, ngay)
            duong = self._duong_xuat(path, "nhat_ky_thao_tac.csv")
            _ghi_csv(duong, list(nk.COT), dong)
            return _ok({"path": duong, "n_rows": len(dong)})
        except ValueError:
            return _fail(err("gt4_ngay_sai"))
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            return _fail(err("gt3_loi_nhat_ky", detail=str(e)))
