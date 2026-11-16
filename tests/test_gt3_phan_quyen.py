"""GT3-L2: cổng phân quyền trung tâm (`phan_quyen.py`). Dữ liệu MÔ PHỎNG, mật khẩu giả.

Chưa có tài khoản thì mọi hàm chạy y như trước; có tài khoản thì giáo viên chỉ xem / xuất / nhập điểm,
quản trị làm được hết, hàm lạ bị từ chối.
"""

import inspect
import os
import sqlite3

import pytest

import browser_host
import phan_quyen as pq
from api import PipelineAPI

MK = "matkhau-gia-1"
RESOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ma_loi(r):
    return [e["code"] for e in r["errors"]]


def hang(api, bang):
    con = sqlite3.connect(api.db_path)
    try:
        return con.execute(f"SELECT COUNT(*) FROM {bang}").fetchone()[0]
    finally:
        con.close()


@pytest.fixture
def co_tk(api):
    """Có quản trị + giáo viên; trả về hàm đổi vai."""
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]

    def vao(ten):
        api.dang_xuat()
        if ten:
            assert api.dang_nhap(ten, MK)["ok"]
    vao("quantri")
    return vao


# ------------------------------------------------------------- bảng đầy đủ
def cac_ham_cong_khai():
    return sorted(n for n in dir(PipelineAPI) if not n.startswith("_") and callable(getattr(PipelineAPI, n)))


def test_moi_ham_cong_khai_co_trong_bang_quyen():
    thieu = [n for n in cac_ham_cong_khai() if n not in pq.QUYEN]
    assert not thieu, f"hàm công khai chưa phân quyền (I1 ở nhánh tích hợp): {thieu}"


def test_bang_quyen_khong_co_ten_thua():
    co = set(cac_ham_cong_khai())
    thua = [n for n in pq.QUYEN if n not in co]
    assert not thua, f"tên trong QUYEN không còn là hàm của PipelineAPI: {thua}"


def test_muc_quyen_hop_le_va_hai_nhom_khong_chong_nhau():
    assert set(pq.QUYEN.values()) == {pq.CONG_KHAI, pq.GIAO_VIEN, pq.QUAN_TRI}
    assert {n for n, m in pq.QUYEN.items() if m == pq.CONG_KHAI} == {
        "dang_nhap", "dang_xuat", "get_phien_dang_nhap", "tao_tai_khoan", "doi_mat_khau"}


def test_ham_ghi_la_quan_tri_ham_doc_la_giao_vien():
    for n in ("run_pipeline", "reset_data", "delete_club", "import_so_nhap", "update_workspace_config",
              "mo_khoa_wharton", "xoa_tai_khoan", "liet_ke_tai_khoan", "delete_workspace"):
        assert pq.QUYEN[n] == pq.QUAN_TRI, n
    for n in ("get_match_results", "export_ket_qua", "get_dashboard_status", "list_clubs",
              "submit_club_scores", "luu_diem_danh"):
        assert pq.QUYEN[n] == pq.GIAO_VIEN, n
    for n in cac_ham_cong_khai():
        if n.startswith(("get_", "list_")) and n not in ("get_phien_dang_nhap", "get_nhat_ky_thao_tac"):
            assert pq.QUYEN[n] != pq.QUAN_TRI, n


# ------------------------------------------------------------ chưa có tài khoản
def test_chua_co_tai_khoan_nam_ham_ghi_chay_nhu_cu(api):
    assert api.create_or_update_club("A", "CLB A", 5, 0, "")["ok"]
    assert api.create_student_if_missing("s1", "Hoc sinh 1")["ok"]
    assert api.submit_preferences("s1", ["A"])["ok"]
    assert api.set_student_class("s1", "10A1")["ok"]
    assert api.delete_student("s1")["ok"]
    assert api.delete_club("A")["ok"]


def test_bao_ham_giu_ten_chu_ky_va_ngoai_le(api):
    assert PipelineAPI.run_pipeline._gt3_cong
    goc = PipelineAPI.run_pipeline._gt3_goc
    assert inspect.signature(PipelineAPI.run_pipeline) == inspect.signature(goc)
    assert PipelineAPI.run_pipeline.__name__ == "run_pipeline"
    # ngoại lệ do chính hàm ném vẫn đi qua nguyên vẹn khi chưa có tài khoản
    with pytest.raises(TypeError):
        api.create_or_update_club()


def test_ham_cong_khai_chi_bi_bao_de_ghi_nhat_ky(api):
    assert not getattr(PipelineAPI.get_phien_dang_nhap, "_gt3_cong", False)       # không ghi, không kiểm
    for n in ("dang_nhap", "dang_xuat", "tao_tai_khoan", "doi_mat_khau"):
        assert getattr(getattr(PipelineAPI, n), "_gt3_cong", False), n


# ---------------------------------------------------------------- có tài khoản
def test_chua_dang_nhap_bi_chan_moi_ham_tru_dang_nhap(api, co_tk):
    co_tk(None)
    r = api.get_dashboard_status()
    assert not r["ok"] and r["data"] is None and ma_loi(r) == ["gt3_can_dang_nhap"]
    r = api.create_or_update_club("A", "CLB A", 5, 0, "")
    assert ma_loi(r) == ["gt3_can_dang_nhap"] and hang(api, "clubs") == 0
    assert api.get_phien_dang_nhap()["ok"]
    assert api.dang_nhap("gv1", MK)["ok"]


def test_giao_vien_ghi_bi_tu_choi_va_khong_ghi_gi(api, co_tk):
    co_tk("quantri")
    assert api.create_or_update_club("A", "CLB A", 5, 0, "")["ok"]
    assert api.create_student_if_missing("s1", "Hoc sinh 1")["ok"]
    truoc = (hang(api, "clubs"), hang(api, "students"), hang(api, "run_history"))
    co_tk("gv1")
    for goi in (lambda: api.create_or_update_club("B", "CLB B", 5, 0, ""),
                lambda: api.delete_club("A"),
                lambda: api.delete_student("s1"),
                lambda: api.run_pipeline(),
                lambda: api.reset_data(),
                lambda: api.xoa_tai_khoan("quantri"),
                lambda: api.liet_ke_tai_khoan()):
        r = goi()
        assert not r["ok"] and r["data"] is None and ma_loi(r) == ["gt3_khong_du_quyen"], r
    assert (hang(api, "clubs"), hang(api, "students"), hang(api, "run_history")) == truoc
    r = api.delete_club("A")
    assert r["errors"][0]["params"] == {"hanh_dong": "delete_club"}


def test_giao_vien_xem_va_xuat_duoc(api, co_tk):
    co_tk("quantri")
    assert api.create_or_update_club("A", "CLB A", 5, 0, "")["ok"]
    co_tk("gv1")
    assert api.get_dashboard_status()["ok"]
    assert api.list_clubs()["ok"]
    assert api.get_run_history()["ok"]


def test_quan_tri_lam_duoc_ca_ghi_va_doc(api, co_tk):
    assert api.create_or_update_club("A", "CLB A", 5, 0, "")["ok"]
    assert api.create_student_if_missing("s1", "Hoc sinh 1")["ok"]
    assert api.delete_student("s1")["ok"]
    assert api.get_dashboard_status()["ok"]
    assert api.liet_ke_tai_khoan()["ok"]


def test_ham_la_chua_phan_quyen_bi_tu_choi_ke_ca_quan_tri(api, co_tk, monkeypatch):
    def ham_la_gia(self):
        return {"ok": True, "data": "da chay", "errors": []}
    monkeypatch.setattr(PipelineAPI, "ham_la_gia", ham_la_gia, raising=False)
    pq.ap_dung_cong(PipelineAPI)
    r = api.ham_la_gia()
    assert ma_loi(r) == ["gt3_khong_du_quyen"]
    co_tk(None)
    assert ma_loi(api.ham_la_gia()) == ["gt3_can_dang_nhap"]


def test_goi_long_ben_trong_khong_kiem_lai(api, co_tk, monkeypatch):
    """Hàm của giáo viên gọi hàm của quản trị bên trong: chỉ kiểm ở lời gọi ngoài cùng."""
    def ham_gv(self):
        return self.get_dashboard_status()
    monkeypatch.setattr(PipelineAPI, "ham_gv_gia", ham_gv, raising=False)
    monkeypatch.setitem(pq.QUYEN, "ham_gv_gia", pq.GIAO_VIEN)

    def ham_cha(self):
        return self.delete_club("khong-co")      # mức quản trị
    monkeypatch.setattr(PipelineAPI, "ham_cha_gia", ham_cha, raising=False)
    monkeypatch.setitem(pq.QUYEN, "ham_cha_gia", pq.GIAO_VIEN)
    pq.ap_dung_cong(PipelineAPI)
    co_tk("gv1")
    assert api.ham_gv_gia()["ok"]
    r = api.ham_cha_gia()
    assert ma_loi(r) != ["gt3_khong_du_quyen"]          # không bị chặn giữa chừng
    assert api.delete_club("A")["errors"][0]["code"] == "gt3_khong_du_quyen"   # ngoài cùng vẫn chặn


def test_lam_moi_gio_nghi_moi_lan_goi(api, co_tk):
    class DongHo:
        t = 1000.0

        def __call__(self):
            return self.t
    dh = DongHo()
    api._dong_ho = dh
    co_tk("gv1")
    dh.t += 10 * 60
    assert api.get_dashboard_status()["ok"]              # làm mới giờ nghỉ
    dh.t += 10 * 60                                       # tổng 20 phút nhưng chỉ nghỉ 10 phút kể từ lần gọi
    assert api.get_dashboard_status()["ok"]
    dh.t += 16 * 60
    assert ma_loi(api.get_dashboard_status()) == ["gt3_can_dang_nhap"]


def test_dang_xuat_xong_bi_chan_lai(api, co_tk):
    assert api.get_dashboard_status()["ok"]
    api.dang_xuat()
    assert ma_loi(api.get_dashboard_status()) == ["gt3_can_dang_nhap"]


def test_xoa_het_tai_khoan_thi_ve_nhu_cu(api, co_tk):
    assert api.get_dashboard_status()["ok"]
    con = sqlite3.connect(api.db_path)
    con.execute("DELETE FROM tai_khoan")
    con.commit()
    con.close()
    api.dang_xuat()
    assert api.get_dashboard_status()["ok"]


# ----------------------------------------------------------- máy chủ trình duyệt
def _post(base, token, ten, args=None):
    import json
    import urllib.request
    req = urllib.request.Request(
        f"{base}/__api__/{ten}", data=json.dumps({"args": args or []}).encode(),
        headers={"Content-Type": "application/json", "X-Kiosk-Token": token}, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def test_browser_host_di_qua_cung_mot_cong(api, co_tk):
    url = browser_host.serve(api, RESOURCE_DIR, "index.html", open_browser=False)
    base, token = url.split("/index.html?t=")
    co_tk("gv1")
    r = _post(base, token, "create_or_update_club", ["A", "CLB A", 5, 0, ""])
    assert ma_loi(r) == ["gt3_khong_du_quyen"] and hang(api, "clubs") == 0
    assert _post(base, token, "get_dashboard_status")["ok"]
    co_tk(None)
    assert ma_loi(_post(base, token, "get_dashboard_status")) == ["gt3_can_dang_nhap"]
    co_tk("quantri")
    assert _post(base, token, "create_or_update_club", ["A", "CLB A", 5, 0, ""])["ok"]
    assert hang(api, "clubs") == 1


# ------------------------------------------------- đọc bảng tài khoản bị hỏng (đóng khi lỗi)
def _lam_hong_doc(monkeypatch):
    def hong(self):
        raise sqlite3.OperationalError("database is locked")
    monkeypatch.setattr(PipelineAPI, "_co_tai_khoan", hong)


def test_api_moi_tren_csdl_co_tai_khoan_doc_hong_van_chan(api, co_tk, monkeypatch):
    co_tk(None)
    api2 = PipelineAPI(api.db_path)             # tiến trình mới trên CSDL đã có tài khoản
    _lam_hong_doc(monkeypatch)
    r = api2.reset_data()
    assert not r["ok"] and ma_loi(r) == ["gt3_can_dang_nhap"]
    assert api2.create_or_update_club("A", "CLB A", 5, 0, "")["errors"][0]["code"] == "gt3_can_dang_nhap"
    assert hang(api2, "clubs") == 0


def test_doc_hong_lan_dau_khong_co_nho_coi_nhu_da_co_tai_khoan(api, monkeypatch):
    api._co_tk_nho.clear()                      # chưa từng đọc được
    _lam_hong_doc(monkeypatch)
    assert ma_loi(api.get_dashboard_status()) == ["gt3_can_dang_nhap"]


def test_doc_hong_sau_khi_da_doc_duoc_dung_ket_qua_cu(api, co_tk, monkeypatch):
    assert api.get_dashboard_status()["ok"]       # quản trị đã đăng nhập, bộ nhớ đệm = có tài khoản
    _lam_hong_doc(monkeypatch)
    assert api.get_dashboard_status()["ok"]       # vẫn là phiên quản trị hợp lệ
    api.dang_xuat()
    assert ma_loi(api.get_dashboard_status()) == ["gt3_can_dang_nhap"]


def test_chua_co_tai_khoan_doc_duoc_thi_bo_nho_la_false_va_hong_van_chay_nhu_cu(api, monkeypatch):
    assert api.get_dashboard_status()["ok"]
    assert api._co_tk_nho[api.db_path] is False
    _lam_hong_doc(monkeypatch)
    assert api.get_dashboard_status()["ok"]       # đã biết CSDL này chưa có tài khoản


def test_bo_nho_theo_tung_csdl(api, co_tk, tmp_path, monkeypatch):
    """Đổi sang CSDL khác (workspace) chưa từng đọc được thì không mượn kết quả của CSDL trước."""
    assert api.get_dashboard_status()["ok"]
    api.db_path = str(tmp_path / "khac.db")
    _lam_hong_doc(monkeypatch)
    assert api._co_tai_khoan_nho() is True


def test_thieu_bang_tai_khoan_la_chua_co_tai_khoan(api, monkeypatch):
    def thieu(self):
        raise sqlite3.OperationalError("no such table: tai_khoan")
    monkeypatch.setattr(PipelineAPI, "_co_tai_khoan", thieu)
    assert api._co_tai_khoan_nho() is False
    assert api.get_dashboard_status()["ok"]


def test_cong_khong_cong_them_thoi_gian_cho_khi_csdl_bi_khoa(api, co_tk):
    """CSDL đang bị khoá ghi: bước hỏi "có tài khoản không" của cổng dùng giá trị nhớ, không chờ hết thời gian chờ khoá."""
    import sqlite3
    import time

    assert api.get_dashboard_status()["ok"]
    giu = sqlite3.connect(api.db_path)
    giu.execute("BEGIN EXCLUSIVE")
    try:
        t0 = time.monotonic()
        for _ in range(20):
            assert api._co_tai_khoan_nho() is True
        assert time.monotonic() - t0 < 1.0          # lần đầu chờ tối đa 50 ms, 19 lần sau không chờ
    finally:
        giu.rollback()
        giu.close()
