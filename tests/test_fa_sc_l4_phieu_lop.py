"""FA-SC L4 (TH): phiếu xác nhận theo lớp — mỗi lớp một tệp, mỗi em một khối, cho giáo viên chủ nhiệm.

Dữ liệu MÔ PHỎNG (đợt giả của du_lieu_test/su_co/chung.py). Tuỳ chọn `phieu_lop` mặc định TẮT: tắt thì không có thư mục
và đầu ra như cũ. Mỗi khối: nguyện vọng đã lưu từng ngày, ba huy chương, bài thi nhận được và có tính hay không (bài không
tính ghi rõ lý do). Không điểm, không số bốc thăm, không dữ liệu lớp khác (bất biến 2: chỉ là báo cáo).
"""
import copy
import os
import re
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
THU_MUC = "PHIEU_XAC_NHAN_LOP"
BUOI = "thu_2"


@pytest.fixture
def dot():
    return c.sinh_dot(SO_HS, 42)


def _chuyen(thu_muc, dot, them_thi=(), co_ds=True, **kw):
    de, loai = c.de_fa()
    so_clb, tep_dk, tep_thi = c.ghi_tep(dot, str(thu_muc), de, loai, phieu_thi_them=list(them_thi))
    if co_ds:
        kw["danh_sach_truong"] = c.ghi_danh_sach(os.path.join(str(thu_muc), "ds.csv"), c.danh_sach_that(dot))
    return cv.chuyen_fa_daa(os.path.join(str(thu_muc), "nap"), de, so_clb, dang_ky_xlsx=tep_dk, quiz_xlsx=[tep_thi], **kw)


def _doc(thu_muc, lop):
    wb = openpyxl.load_workbook(os.path.join(str(thu_muc), "nap", THU_MUC, "%s.xlsx" % lop), data_only=True)
    return [[o.value for o in r] for w in wb.worksheets for r in w.iter_rows()]


def _chu(hang):
    return " ".join(str(v) for r in hang for v in r if v is not None)


def _lop_cua(dot):
    return {h["sid"]: l for h, (_, l, _) in zip(dot["hs"], c.danh_sach_that(dot))}


def _so_sanh_tep(pa, pb):
    wa, wb_ = openpyxl.load_workbook(pa), openpyxl.load_workbook(pb)
    assert wa.sheetnames == wb_.sheetnames
    for s in wa.sheetnames:
        assert [[o.value for o in r] for r in wa[s].iter_rows()] == [[o.value for o in r] for r in wb_[s].iter_rows()]


def test_tat_mac_dinh_khong_co_thu_muc_va_khong_co_khoa(tmp_path, dot):
    kq = _chuyen(tmp_path, dot)
    assert "phieu_lop" not in kq
    assert not os.path.exists(os.path.join(str(tmp_path), "nap", THU_MUC))


def test_bat_khong_doi_cac_tep_khac(tmp_path, dot):
    a = _chuyen(tmp_path / "tat", dot)
    b = _chuyen(tmp_path / "bat", dot, phieu_lop=True)
    assert a["canh_bao"] == b["canh_bao"] and a["n_bai_thi"] == b["n_bai_thi"]
    for ten in (cv.TEN_SO, "BANG_DIEM.xlsx"):
        _so_sanh_tep(*(os.path.join(str(p), "nap", ten) for p in (tmp_path / "tat", tmp_path / "bat")))


def test_mot_tep_moi_lop_moi_khoi_moi_em(tmp_path, dot):
    kq = _chuyen(tmp_path, dot, phieu_lop=True)
    lop_cua = _lop_cua(dot)
    tep = {f[:-5] for f in os.listdir(os.path.join(str(tmp_path), "nap", THU_MUC))}
    assert tep == set(lop_cua.values())
    assert set(kq["phieu_lop"]) == tep
    for lop in tep:
        chu = _chu(_doc(tmp_path, lop))
        for sid, l in lop_cua.items():
            assert (sid in chu) == (l == lop), (lop, sid)
        assert len(kq["phieu_lop"][lop]) == sum(1 for l in lop_cua.values() if l == lop)


def test_khoi_co_nguyen_vong_huy_chuong_va_bai_thi(tmp_path, dot):
    de, loai = c.de_fa()
    h = dot["hs"][0]
    kq = _chuyen(tmp_path, dot, phieu_lop=True)
    chu = _chu(_doc(tmp_path, _lop_cua(dot)[h["sid"]]))
    ten = {x["club_id"]: x["name"] for x in de["cau_lac_bo"]}
    for ds in h["nv"].values():
        for x in ds:
            assert ten[x] in chu
    assert "Vàng" in chu
    assert "Tính" in chu
    khoi = next(k for k in kq["phieu_lop"][_lop_cua(dot)[h["sid"]]] if k["student_id"] == h["sid"])
    assert "Vàng" in khoi["huy_chuong"].values() and set(khoi["huy_chuong"].values()) <= {"Vàng", "Bạc", "Đồng"}


def test_bai_thi_khong_tinh_ghi_ly_do(tmp_path, dot):
    de, loai = c.de_fa()
    h = next(e for e in dot["hs"] if any(loai[x] == so_nhap.TUYEN_CHON for x in e["nv"][BUOI]))
    x = next(x for x in h["nv"][BUOI] if loai[x] == so_nhap.TUYEN_CHON)
    loi = copy.deepcopy(dot)
    e = c.em(loi, h["sid"])
    e["nv"][BUOI] = [y for y in e["nv"][BUOI] if y != x]          # có bài thi CLB x nhưng em không xếp CLB x
    kq = _chuyen(tmp_path, loi, phieu_lop=True)
    lop = _lop_cua(dot)[h["sid"]]
    khoi = next(k for k in kq["phieu_lop"][lop] if k["student_id"] == h["sid"])
    sai = [b for b in khoi["bai_thi"] if b["club_id"] == x]
    assert sai and not sai[0]["tinh"] and "không xếp" in sai[0]["ly_do"]
    chu = _chu(_doc(tmp_path, lop))
    assert "Không tính" in chu and "không xếp" in chu


def test_em_xep_clb_tuyen_chon_chua_co_bai_thi_ghi_ro(tmp_path, dot):
    de, loai = c.de_fa()
    h, x = next((e, y) for e in dot["hs"] for y in e["thi"])
    loi = copy.deepcopy(dot)
    c.em(loi, h["sid"])["thi"] = {}
    kq = _chuyen(tmp_path, loi, phieu_lop=True)
    khoi = next(k for k in kq["phieu_lop"][_lop_cua(dot)[h["sid"]]] if k["student_id"] == h["sid"])
    thieu = [b for b in khoi["bai_thi"] if b["club_id"] == x]
    assert thieu and not thieu[0]["tinh"] and "chưa" in thieu[0]["ly_do"]


def test_bai_lan_hai_khong_tinh_ghi_ly_do(tmp_path, dot):
    import shutil
    de, loai = c.de_fa()
    so_clb, tep_dk, tep_thi = c.ghi_tep(dot, str(tmp_path), de, loai)
    tep_hai = os.path.join(str(tmp_path), "bai_thi_lan_hai.xlsx")
    shutil.copy(tep_thi, tep_hai)                                  # mọi em có bài lần hai ở tệp thứ hai
    kq = cv.chuyen_fa_daa(os.path.join(str(tmp_path), "nap"), de, so_clb, dang_ky_xlsx=tep_dk,
                          quiz_xlsx=[tep_thi, tep_hai], phieu_lop=True)
    h = next(e for e in dot["hs"] if e["thi"])
    x = next(iter(h["thi"]))
    khoi = next(k for lop in kq["phieu_lop"].values() for k in lop if k["student_id"] == h["sid"])
    hai = [b for b in khoi["bai_thi"] if b["club_id"] == x and not b["tinh"]]
    assert hai and "lần đầu" in hai[0]["ly_do"]
    assert any(b["club_id"] == x and b["tinh"] for b in khoi["bai_thi"])


def test_rieng_tu_khong_diem_khong_boc_tham_khong_lop_khac(tmp_path, dot):
    kq = _chuyen(tmp_path, dot, phieu_lop=True)
    lop_cua = _lop_cua(dot)
    for lop in kq["phieu_lop"]:
        hang = _doc(tmp_path, lop)
        tieu = _chu(hang).lower()
        for cam in ("điểm", "diem", "stb", "bốc thăm", "boc tham", "score", "@"):
            assert cam not in tieu, (lop, cam)
        assert all(v is None or isinstance(v, str) for r in hang for v in r)   # không số nào (điểm, thứ tự bốc thăm)
        for sid, l in lop_cua.items():
            if l != lop:
                assert not re.search(r"\b%s\b" % sid, _chu(hang))


def test_khong_co_danh_sach_truong_em_chua_co_lop_vao_mot_tep_rieng(tmp_path, dot):
    kq = _chuyen(tmp_path, dot, co_ds=False, phieu_lop=True)
    assert list(kq["phieu_lop"]) == ["Chưa có lớp"] or len(kq["phieu_lop"]) == 1
    assert sum(len(v) for v in kq["phieu_lop"].values()) == SO_HS
