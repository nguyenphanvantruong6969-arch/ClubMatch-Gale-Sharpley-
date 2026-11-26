"""DK4-L0d: hoàn nguyên khi "Chốt và xếp" hỏng không bao giờ làm mất dòng nào của bảng nhật ký chỉ-thêm (bất biến 4)."""
import sqlite3

import test_dk3_api as _t3
from test_dk3_api import ma, ok
from test_dk4_chot_va_xep import _bang, _dang_ky_va_cham

cd = _t3.cd
NHAT_KY = ("run_history", "wharton_nhat_ky", "fa_dieu_chinh")


def _hong_sau_khi_ghi_dong(api, monkeypatch):
    """Mô phỏng bước xếp đã COMMIT một dòng run_history rồi mới hỏng (trường hợp xấu nhất)."""
    goc = api.run_pipeline

    def hong(**k):
        goc(**k)
        raise RuntimeError("hong sau khi da ghi")
    monkeypatch.setattr(api, "run_pipeline", hong)


def test_hong_sau_nhap_khong_mat_dong_run_history_da_co(cd, monkeypatch):
    api, qt = cd
    _dang_ky_va_cham(api, qt)
    ok(api.dk_chot_va_xep(qt, 7))                              # lần chạy thật đầu tiên -> có dòng run_history
    truoc = {t: _bang(api, t) for t in NHAT_KY}
    assert truoc["run_history"]
    _hong_sau_khi_ghi_dong(api, monkeypatch)
    assert ma(api.dk_chot_va_xep(qt, 7)) == "dk_chot_loi_he_thong"
    for t in NHAT_KY:
        sau = _bang(api, t)
        assert all(d in sau for d in truoc[t]), t              # không dòng nào đã có bị mất


def test_dong_run_history_cua_lan_hong_cung_con_lai(cd, monkeypatch):
    api, qt = cd
    _dang_ky_va_cham(api, qt)
    n0 = len(_bang(api, "run_history"))
    _hong_sau_khi_ghi_dong(api, monkeypatch)
    assert ma(api.dk_chot_va_xep(qt, 7)) == "dk_chot_loi_he_thong"
    assert len(_bang(api, "run_history")) == n0 + 1            # mỗi lần chạy thêm một dòng, kể cả lần hỏng
    c = sqlite3.connect(api.db_path)
    try:
        assert c.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        c.close()
