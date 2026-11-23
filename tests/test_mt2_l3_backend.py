"""MT2-L3 (backend): sẵn sàng / báo cáo sức khoẻ cho "Chia CLB theo loại" khi KHÔNG có huy chương, cột loại ở bảng CLB,
cảnh báo không chặn (F4), vòng bật → tắt → bật giữ `clubs.loai`, giáo viên không ghi được công tắc.
Dữ liệu là dữ liệu MÔ PHỎNG dựng trong test."""

import cau_hinh_ws as ch
import api as api_mod
from _fa import dung_fa_clb, dung_hs_fa, giu_cho

MK = "matkhau-gia-1"


def _bat(api, **luat):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False, "chia_loai": True, **luat}})


def _ma(res):
    return [w["code"] for w in res["data"]["warnings"]]


def test_suc_khoe_bao_thieu_clb_tu_do_va_thieu_loai_khi_bat(api):
    _bat(api)
    dung_fa_clb(api, G=(2, "GIOI_HAN"), X=(2,))
    dung_hs_fa(api, "a", nv={"a": ["G"]})
    rep = api.get_data_health_report()
    assert rep["ok"], rep
    assert {"fa_thieu_clb_tu_do", "fa_clb_thieu_loai"} <= set(_ma(rep))
    assert rep["data"]["n_high"] >= 2                      # lỗi chặn = "high" -> thanh "Việc tiếp theo" chỉ vào cảnh báo


def test_suc_khoe_im_lang_khi_tat_va_khi_du(api):
    _bat(api, chia_loai=False)
    dung_fa_clb(api, G=(2, "GIOI_HAN"))
    dung_hs_fa(api, "a", nv={"a": ["G"]})
    assert not [c for c in _ma(api.get_data_health_report()) if c.startswith("fa_")]
    _bat(api)
    dung_fa_clb(api, T=(2, "TU_DO"))
    assert not [c for c in _ma(api.get_data_health_report()) if c.startswith("fa_")]


def test_canh_bao_khong_chan_xuat_hien_o_suc_khoe_va_o_lan_chay(api):
    """F4: giữ chỗ cho em không xếp CLB đó là cảnh báo (MA_CANH_BAO), không chặn; hiện ở sức khoẻ (medium) và ở bước validate."""
    _bat(api)
    dung_fa_clb(api, T=(3, "TU_DO"), G=(2, "GIOI_HAN"))
    dung_hs_fa(api, "a", "b", nv={"a": ["G", "T"], "b": ["T"]})
    giu_cho(api, ("G", "b"))                                # b không xếp G
    rep = api.get_data_health_report()
    w = [x for x in rep["data"]["warnings"] if x["code"] == "fa_giu_cho_khong_xep_clb"]
    assert w and w[0]["severity"] == "medium"
    kq = api.run_pipeline(seed=3)
    assert kq["ok"], kq["errors"]
    buoc = [s for s in kq["data"]["steps"] if s["step"] == "validate"][-1]
    assert "fa_giu_cho_khong_xep_clb" in [e["code"] for e in buoc["detail"]]


def test_get_san_sang_loai_khong_xet_huy_chuong(api):
    _bat(api)
    dung_fa_clb(api, T=(2, "TU_DO"), S=(2, "TUYEN_CHON"))
    dung_hs_fa(api, "a", nv={"a": ["T"]})
    d = api.get_san_sang_loai()["data"]
    assert d["san_sang"] is False and d["thieu_diem_san"] == ["S"] and d["huy_chuong_sai"] == 0
    assert api.dat_loai_clb("S", "TUYEN_CHON", 5)["ok"]
    d = api.get_san_sang_loai()["data"]
    assert d["san_sang"] is True and d["thieu_diem_san"] == []


def test_bang_clb_co_cot_loai_khi_bat_va_khong_khi_tat(api):
    dung_fa_clb(api, T=(2, "TU_DO"))
    _bat(api, chia_loai=False)
    assert "loai" not in api.list_clubs_admin()["data"][0]
    _bat(api)
    assert api.list_clubs_admin()["data"][0]["loai"] == "TU_DO"


def test_bat_tat_bat_giu_nguyen_loai_da_dat(api):
    dung_fa_clb(api, T=(2, "TU_DO"), G=(2, "GIOI_HAN"), S=(2, "TUYEN_CHON", 6))
    truoc = {c["club_id"]: (c["loai"], c["diem_san"]) for c in api.get_san_sang_loai()["data"]["clubs"]}
    for bat in (True, False, True):
        ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False, "chia_loai": bat}})
        assert api.get_chia_loai()["data"]["hieu_luc"] is bat
    sau = {c["club_id"]: (c["loai"], c["diem_san"]) for c in api.get_san_sang_loai()["data"]["clubs"]}
    assert sau == truoc


def test_giao_vien_khong_ghi_duoc_cong_tac_va_loai(tmp_path):
    a = api_mod.PipelineAPI(str(tmp_path / "app.db"))
    dung_fa_clb(a, T=(2, "TU_DO"))
    assert a.tao_tai_khoan("quantri", MK, "quan_tri")["ok"] and a.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    assert a.dang_nhap("gv1", MK)["ok"]
    for kq in (a.update_workspace_config({"rules": {"chia_loai": True}}), a.dat_loai_clb("T", "GIOI_HAN")):
        assert [e["code"] for e in kq["errors"]] == ["gt3_khong_du_quyen"]
