"""FA-SC L3 (TH): báo cáo theo CLB — mỗi CLB một tệp, cho giáo viên CLB.

Dữ liệu MÔ PHỎNG (đợt giả của du_lieu_test/su_co/chung.py). Tuỳ chọn `bao_cao_clb` mặc định TẮT: tắt thì không có thư mục
và đầu ra như cũ. Mỗi tệp chỉ có việc của CLB đó: email phiếu thi bị bỏ, và mã em xếp CLB mà chưa có bài thi.
Không điểm, không số bốc thăm, không dữ liệu CLB khác (bất biến 2: chỉ là báo cáo).
"""
import copy
import os
import sys

import openpyxl
import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (GOC, os.path.join(GOC, "mau_forms_thi_clb"), os.path.join(GOC, "du_lieu_test", "su_co")):
    sys.path.insert(0, _p)

import chung as c  # noqa: E402
import chuyen_forms_sang_phan_mem as cv  # noqa: E402
import so_nhap  # noqa: E402

SO_HS = 24
THU_MUC = "BAO_CAO_CLB"
BUOI = "thu_2"


@pytest.fixture
def dot():
    return c.sinh_dot(SO_HS, 42)


def _chuyen(thu_muc, dot, them_thi=(), **kw):
    de, loai = c.de_fa()
    so_clb, tep_dk, tep_thi = c.ghi_tep(dot, str(thu_muc), de, loai, phieu_thi_them=list(them_thi))
    return cv.chuyen_fa_daa(os.path.join(str(thu_muc), "nap"), de, so_clb, dang_ky_xlsx=tep_dk, quiz_xlsx=[tep_thi], **kw)


def _doc(thu_muc, clb):
    duong = os.path.join(str(thu_muc), "nap", THU_MUC, "%s.xlsx" % clb)
    wb = openpyxl.load_workbook(duong, data_only=True)
    return {w.title: [[o.value for o in r] for r in w.iter_rows()] for w in wb.worksheets}


def _em_va_clb(dot, loai):
    for h in dot["hs"]:
        for x in h["nv"][BUOI]:
            if loai[x] == so_nhap.TUYEN_CHON and x in h["thi"]:
                return h, x
    raise ValueError("không có em phù hợp")


def _loi(dot, loai):
    """Đợt có hai ca: một em bài thi gửi từ email lạ (gửi cho CLB x) và một em xếp CLB x nhưng chưa có bài."""
    h, x = _em_va_clb(dot, loai)
    loi = copy.deepcopy(dot)
    e = c.em(loi, h["sid"])
    bai, e["thi"] = e["thi"], {}
    return loi, h, x, "ca.nhan@ngoai.example", bai


def test_tat_mac_dinh_khong_co_thu_muc_va_khong_co_khoa(tmp_path, dot):
    kq = _chuyen(tmp_path, dot)
    assert "bao_cao_clb" not in kq
    assert not os.path.exists(os.path.join(str(tmp_path), "nap", THU_MUC))


def test_bat_khong_doi_cac_tep_khac(tmp_path, dot):
    loai = c.de_fa()[1]
    loi, h, x, la, bai = _loi(dot, loai)
    a = _chuyen(tmp_path / "tat", loi, them_thi=[(la, bai)])
    b = _chuyen(tmp_path / "bat", loi, them_thi=[(la, bai)], bao_cao_clb=True)
    assert a["canh_bao"] == b["canh_bao"] and a["n_bai_thi"] == b["n_bai_thi"]
    for ten in ("SO_NHAP_HOC_SINH_FA.xlsx", "BANG_DIEM.xlsx"):
        pa, pb = (os.path.join(str(p), "nap", ten) for p in (tmp_path / "tat", tmp_path / "bat"))
        if os.path.exists(pa):
            wa, wb_ = openpyxl.load_workbook(pa), openpyxl.load_workbook(pb)
            assert wa.sheetnames == wb_.sheetnames
            for s in wa.sheetnames:
                assert [[o.value for o in r] for r in wa[s].iter_rows()] == [[o.value for o in r] for r in wb_[s].iter_rows()]


def test_mot_tep_cho_moi_clb_co_thi(tmp_path, dot):
    de, loai = c.de_fa()
    kq = _chuyen(tmp_path, dot, bao_cao_clb=True)
    co_thi = {x["club_id"] for x in de["cau_lac_bo"] if x.get("de_thi")}
    tep = {f[:-5] for f in os.listdir(os.path.join(str(tmp_path), "nap", THU_MUC))}
    assert tep == co_thi and co_thi
    assert set(kq["bao_cao_clb"]) == co_thi


def test_phieu_bi_bo_va_em_chua_thi_nam_dung_tep(tmp_path, dot):
    loai = c.de_fa()[1]
    loi, h, x, la, bai = _loi(dot, loai)
    kq = _chuyen(tmp_path, loi, them_thi=[(la, bai)], bao_cao_clb=True)
    tep = _doc(tmp_path, x)
    chu = " ".join(str(v) for hang in tep["Phiếu thi bị bỏ"] for v in hang)
    assert la in chu
    assert h["sid"] in " ".join(str(v) for hang in tep["Chưa có bài thi"] for v in hang)
    assert kq["bao_cao_clb"][x]["phieu_bo"] == [la]
    assert h["sid"] in kq["bao_cao_clb"][x]["chua_thi"]
    # CLB khác không bị lẫn
    for y in kq["bao_cao_clb"]:
        if y != x and y not in bai:
            assert la not in kq["bao_cao_clb"][y]["phieu_bo"]


def test_rieng_tu_khong_diem_khong_boc_tham_khong_clb_khac(tmp_path, dot):
    loai = c.de_fa()[1]
    loi, h, x, la, bai = _loi(dot, loai)
    kq = _chuyen(tmp_path, loi, them_thi=[(la, bai)], bao_cao_clb=True)
    for y in kq["bao_cao_clb"]:
        tep = _doc(tmp_path, y)
        tieu = " ".join(str(v) for hang in tep.values() for v in hang).lower()
        for cam in ("điểm", "diem", "stb", "bốc thăm", "boc tham", "score"):
            assert cam not in tieu, (y, cam)
        # chỉ em xếp đúng CLB này mới có mặt ở "Chưa có bài thi"
        nguoi = {hs["sid"] for hs in loi["hs"] if y in [z for v in hs["nv"].values() for z in v]}
        for hang in tep["Chưa có bài thi"][1:]:
            if hang[0] and hang[0] in {hs["sid"] for hs in loi["hs"]}:
                assert hang[0] in nguoi, (y, hang)


def test_khong_co_ca_nao_van_co_tep_ghi_ro(tmp_path, dot):
    kq = _chuyen(tmp_path, dot, bao_cao_clb=True)
    y = next(iter(kq["bao_cao_clb"]))
    tep = _doc(tmp_path, y)
    if not kq["bao_cao_clb"][y]["phieu_bo"]:
        assert any("Không có" in str(v) for hang in tep["Phiếu thi bị bỏ"] for v in hang)
