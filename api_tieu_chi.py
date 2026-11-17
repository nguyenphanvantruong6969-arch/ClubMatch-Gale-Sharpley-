"""GT2 — API tiêu chí xếp (chỉ ĐỌC): mô tả luật đã lưu bằng lời thường + giá trị cho phép.

Lưu thay đổi vẫn đi qua `update_workspace_config` (không có đường lưu mới). Dùng được cả khi chạy
với một CSDL riêng, không cần bật chế độ workspace.
"""

import tieu_chi
from api_workspace import CauHinhHong, loi_cau_hinh
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import luat_xep_cua


class TieuChiMixin:
    def get_tieu_chi(self):
        """Luật xếp đã lưu của workspace đang mở, mô tả bằng lời thường (hai ngôn ngữ).

        data: luat (năm khoá luật xếp), mo_ta (vi), mo_ta_en, tang (tiêu đề hai tầng),
        lua_chon (giá trị cho phép), ghi_chu (câu cố định: không dùng thứ hạng nguyện vọng...).
        Cấu hình đọc không được thì báo lỗi, không lặng lẽ lùi về luật mặc định."""
        try:
            luat_tho = self._cfg_ws(nghiem=True)["rules"]
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        luat = luat_xep_cua(luat_tho)
        return _ok({
            "luat": luat,
            "mo_ta": tieu_chi.mo_ta_tieu_chi(luat_tho, "vi"),
            "mo_ta_en": tieu_chi.mo_ta_tieu_chi(luat_tho, "en"),
            "tang": tieu_chi.tieu_de_tang(luat_tho),
            "lua_chon": tieu_chi.cac_lua_chon_hop_le(),
            "ghi_chu": dict(tieu_chi.GHI_CHU),
        })
