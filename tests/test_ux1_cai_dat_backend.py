"""UX1A-L2b: backend cho trang Cài đặt — kiểm dữ liệu sẵn sàng cho Huy chương và đặt loại CLB.
Dữ liệu MÔ PHỎNG (du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx)."""

import base64
import os

import pytest

from test_fa_gap1_diem_danh import api_ws  # noqa: F401 (fixture)

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_120 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx")


@pytest.fixture
def api_120(api):
    with open(SO_120, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    return api


def test_san_sang_liet_ke_9_clb_thieu_loai_va_3_buoi_thieu_tu_do(api_120):
    kq = api_120.get_san_sang_huy_chuong()
    assert kq["ok"]
    d = kq["data"]
    assert d["san_sang"] is False
    assert len(d["thieu_loai"]) == 9
    assert d["buoi_thieu_tu_do"] == ["thu_2", "thu_4", "thu_6"]
    assert {c["club_id"] for c in d["clubs"]} == set(d["thieu_loai"])


def test_dat_loai_tung_clb_den_khi_san_sang(api_120):
    d = api_120.get_san_sang_huy_chuong()["data"]
    cids = [c["club_id"] for c in d["clubs"]]
    # mỗi buổi: CLB đầu = Tự do, các CLB còn lại = Giới hạn
    thay = set()
    for c in d["clubs"]:
        loai = "TU_DO" if c["buoi"] not in thay else "GIOI_HAN"
        thay.add(c["buoi"])
        assert api_120.dat_loai_clb(c["club_id"], loai)["ok"]
    d2 = api_120.get_san_sang_huy_chuong()["data"]
    assert d2["thieu_loai"] == [] and d2["buoi_thieu_tu_do"] == []
    # UX1A-L2b fix2: loại CLB đã đủ NHƯNG sổ này nạp ở chế độ thường nên các ô huy chương là điểm quyết tâm 0-100
    # -> chưa sẵn sàng; nói đúng số em, không tự đổi dữ liệu.
    assert d2["huy_chuong_sai"] > 100 and d2["huy_chuong_sai_vd"] and d2["san_sang"] is False
    assert len(cids) == 9


def test_so_huy_chuong_hop_le_o_che_do_huy_chuong_thi_san_sang(api_ws):  # noqa: F811
    assert api_ws.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    with open(os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx"), "rb") as f:
        assert api_ws.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    d = api_ws.get_san_sang_huy_chuong()["data"]
    assert d["huy_chuong_sai"] == 0 and d["san_sang"] is True
    assert api_ws.run_pipeline(42)["ok"]                         # và lần chạy thật cũng qua: "Sẵn sàng" không nói dối



def test_tuyen_chon_can_diem_san(api_120):
    cid = api_120.get_san_sang_huy_chuong()["data"]["clubs"][0]["club_id"]
    assert api_120.dat_loai_clb(cid, "TUYEN_CHON")["ok"]
    assert cid in api_120.get_san_sang_huy_chuong()["data"]["thieu_diem_san"]
    assert api_120.dat_loai_clb(cid, "TUYEN_CHON", 5)["ok"]
    assert cid not in api_120.get_san_sang_huy_chuong()["data"]["thieu_diem_san"]


def test_loai_sai_va_clb_la_bi_tu_choi_khong_ghi(api_120):
    cid = api_120.get_san_sang_huy_chuong()["data"]["clubs"][0]["club_id"]
    assert api_120.dat_loai_clb(cid, "BAY_BA")["ok"] is False
    assert api_120.dat_loai_clb("khong_co_clb", "TU_DO")["ok"] is False
    assert api_120.dat_loai_clb(cid, "TUYEN_CHON", 99)["ok"] is False
    assert len(api_120.get_san_sang_huy_chuong()["data"]["thieu_loai"]) == 9


def test_dat_loai_khong_dong_toi_ket_qua_da_xep(api_120):
    assert api_120.run_pipeline(42)["ok"]
    truoc = api_120.get_run_history()["data"]
    cid = api_120.get_san_sang_huy_chuong()["data"]["clubs"][0]["club_id"]
    assert api_120.dat_loai_clb(cid, "TU_DO")["ok"]
    assert api_120.get_run_history()["data"] == truoc          # run_history giữ nguyên (invariant 4)


def test_phan_quyen_va_nhat_ky(api):
    import phan_quyen
    assert phan_quyen.QUYEN["dat_loai_clb"] == phan_quyen.QUAN_TRI
    assert phan_quyen.QUYEN["get_san_sang_huy_chuong"] == phan_quyen.GIAO_VIEN


def test_doi_cach_chon_ghi_mot_dong_nhat_ky_thao_tac(api_ws):  # noqa: F811
    MK = "matkhau-gia-1"
    assert api_ws.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]

    def so_dong():
        kq = api_ws.get_nhat_ky_thao_tac(1, 50, None, "update_workspace_config")
        assert kq["ok"], kq
        d = kq["data"]
        return len(d["dong"] if isinstance(d, dict) and "dong" in d else d)
    n0 = so_dong()
    assert api_ws.update_workspace_config({"rules": {"wharton": True, "fa_daa": False}})["ok"]
    assert so_dong() == n0 + 1
