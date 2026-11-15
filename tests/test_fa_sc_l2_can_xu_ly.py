"""FA-SC L2 (TH): sheet "Cần xử lý" trong BANG_DIEM.xlsx, gom các cảnh báo rời thành một dòng việc cần làm.

Dữ liệu MÔ PHỎNG (đợt giả của du_lieu_test/su_co/chung.py). Tuỳ chọn `can_xu_ly` mặc định TẮT: tắt thì sổ như cũ.
Sheet chỉ là báo cáo: không số nào trong đó đi vào Sổ nhập hay khoá ưu tiên (bất biến 2).
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
TEN_SHEET = "Cần xử lý"
BUOI = "thu_2"


@pytest.fixture
def dot():
    """Đợt sạch, nhưng CLB Tự do luôn xếp CUỐI mỗi ngày (đợt mẫu đôi khi để Tự do đứng trước, sẽ có dòng riêng)."""
    d = c.sinh_dot(SO_HS, 42)
    loai = c.de_fa()[1]
    for h in d["hs"]:
        for b, xep in h["nv"].items():
            h["nv"][b] = [z for z in xep if loai[z] != so_nhap.TU_DO] + [z for z in xep if loai[z] == so_nhap.TU_DO]
    return d


def _chuyen(thu_muc, dot, them_thi=(), **kw):
    de, loai = c.de_fa()
    so_clb, tep_dk, tep_thi = c.ghi_tep(dot, str(thu_muc), de, loai, phieu_thi_them=list(them_thi))
    return cv.chuyen_fa_daa(os.path.join(str(thu_muc), "nap"), de, so_clb, dang_ky_xlsx=tep_dk, quiz_xlsx=[tep_thi], **kw)


def _sheet(thu_muc, ten):
    wb = openpyxl.load_workbook(os.path.join(str(thu_muc), "nap", "BANG_DIEM.xlsx"), data_only=True)
    return wb, ([[o.value for o in r] for r in wb[ten].iter_rows()] if ten in wb.sheetnames else None)


def _em_va_clb(dot, loai):
    """Em đầu tiên có CLB Tuyển chọn đã thi ở BUOI; trả (em, CLB đó)."""
    for h in dot["hs"]:
        for x in h["nv"][BUOI]:
            if loai[x] == so_nhap.TUYEN_CHON and x in h["thi"]:
                return h, x
    raise ValueError("không có em phù hợp")


def test_tat_mac_dinh_khong_co_sheet_va_khong_co_khoa(tmp_path, dot):
    kq = _chuyen(tmp_path, dot)
    assert "can_xu_ly" not in kq
    wb, _ = _sheet(tmp_path, TEN_SHEET)
    assert TEN_SHEET not in wb.sheetnames


def test_du_lieu_sach_bat_tuy_chon_khong_co_dong_nao(tmp_path, dot):
    kq = _chuyen(tmp_path, dot, can_xu_ly=True)
    assert kq["can_xu_ly"] == []
    _, hang = _sheet(tmp_path, TEN_SHEET)
    assert len(hang) == 2 and "Không có" in str(hang[1][0] or hang[1][1] or hang[1][2])   # tiêu đề + một dòng "không có"


def test_bat_tuy_chon_khong_doi_danh_sach_canh_bao_cu(tmp_path, dot):
    h, x = _em_va_clb(dot, c.de_fa()[1])
    loi = copy.deepcopy(dot)
    loi["hs"][0]["nv"][BUOI] = [y for y in loi["hs"][0]["nv"][BUOI] if y != x]       # tạo vài cảnh báo cũ
    a = _chuyen(tmp_path / "tat", loi)
    b = _chuyen(tmp_path / "bat", loi, can_xu_ly=True)
    assert a["canh_bao"] == b["canh_bao"]
    # phần còn lại của sổ (ba sheet đầu) y như nhau
    wa = openpyxl.load_workbook(os.path.join(str(tmp_path / "tat"), "nap", "BANG_DIEM.xlsx"))
    wb = openpyxl.load_workbook(os.path.join(str(tmp_path / "bat"), "nap", "BANG_DIEM.xlsx"))
    for ten in wa.sheetnames:
        assert [[o.value for o in r] for r in wa[ten].iter_rows()] == [[o.value for o in r] for r in wb[ten].iter_rows()]


def test_thi_nham_clb_hai_canh_bao_thanh_mot_dong(tmp_path, dot):
    de, loai = c.de_fa()
    h, x = _em_va_clb(dot, loai)
    loi = copy.deepcopy(dot)
    e = c.em(loi, h["sid"])
    y = next(k for k, v in loai.items() if v == so_nhap.TUYEN_CHON and k != x)
    # bỏ Y khỏi nguyện vọng của em (nếu có) rồi em thi nhầm Y thay vì X
    for b in e["nv"]:
        e["nv"][b] = [z for z in e["nv"][b] if z != y]
    e["thi"][y] = e["thi"].pop(x)
    kq = _chuyen(tmp_path, loi, can_xu_ly=True)
    cua_em = [r for r in kq["can_xu_ly"] if r[0] == h["sid"]]
    assert len(cua_em) == 1, cua_em
    ma, van_de, ai, viec = cua_em[0]
    assert x in van_de and y in van_de          # nêu cả CLB định thi và CLB làm nhầm
    assert ai and viec
    # hai cảnh báo cũ vẫn còn ở sheet "Cảnh báo"
    assert any("KHÔNG xếp" in w[2] for w in kq["canh_bao"] if w[1] == h["email"])
    assert any("NOT_ATTEMPTED" in w[2] for w in kq["canh_bao"] if w[1] == h["sid"] or w[1] == h["email"])
    _, hang = _sheet(tmp_path, TEN_SHEET)
    assert hang[0][:4] == ["Mã HS", "Họ tên", "Vấn đề", "Ai xử lý"] or "Ai" in str(hang[0])
    assert sum(1 for r in hang[1:] if r[0] == h["sid"]) == 1


def test_phieu_thi_email_ngoai_danh_sach_mot_dong_co_email(tmp_path, dot):
    loai = c.de_fa()[1]
    h, x = _em_va_clb(dot, loai)
    loi = copy.deepcopy(dot)
    e = c.em(loi, h["sid"])
    bai, e["thi"] = e["thi"], {}
    la = "ca.nhan@ngoai.example"
    kq = _chuyen(tmp_path, loi, them_thi=[(la, bai)], can_xu_ly=True)
    cua_la = [r for r in kq["can_xu_ly"] if la in " ".join(str(v) for v in r)]
    assert len(cua_la) == 1, cua_la
    # em thật không có bài: có dòng "chưa có bài thi" của em, và nó nằm ở dòng của em
    assert any(r[0] == h["sid"] and x in r[1] for r in kq["can_xu_ly"])


def test_tu_do_dung_truoc_clb_tuyen_chon_da_thi_mot_dong(tmp_path, dot):
    loai = c.de_fa()[1]
    h, x = _em_va_clb(dot, loai)
    loi = copy.deepcopy(dot)
    e = c.em(loi, h["sid"])
    tu_do = next(z for z in e["nv"][BUOI] if loai[z] == so_nhap.TU_DO)
    e["nv"][BUOI] = [tu_do] + [z for z in e["nv"][BUOI] if z != tu_do]
    kq = _chuyen(tmp_path, loi, can_xu_ly=True)
    cua_em = [r for r in kq["can_xu_ly"] if r[0] == h["sid"] and tu_do in r[1]]
    assert len(cua_em) == 1, kq["can_xu_ly"]


def test_giu_cho_khong_dung_dong_gui_giao_vien_clb():
    de, loai = c.de_fa()
    clb = next(k for k, v in loai.items() if v == so_nhap.TUYEN_CHON)
    hs = [{"student_id": "A1", "email": "a1@x", "name": "An", "nguyen_vong": {BUOI: []}, "bai_thi": []}]
    ra = cv.lap_can_xu_ly(de, hs, {clb: {"loai": so_nhap.TUYEN_CHON}}, [(clb, "A1"), (clb, "KHONG_CO")])
    assert len(ra) == 2
    assert all(clb in r[1] and "giáo viên" in r[2].lower() for r in ra)


def test_giu_cho_da_xep_clb_do_khong_co_dong():
    de, loai = c.de_fa()
    clb = next(k for k, v in loai.items() if v == so_nhap.TUYEN_CHON)
    buoi = next(cl["buoi"] for cl in de["cau_lac_bo"] if cl["club_id"] == clb)
    hs = [{"student_id": "A1", "email": "a1@x", "name": "An", "nguyen_vong": {buoi: [clb]}, "bai_thi": []}]
    assert not [r for r in cv.lap_can_xu_ly(de, hs, {clb: {"loai": so_nhap.TUYEN_CHON}}, [(clb, "A1")])
                if "giữ chỗ" in r[1].lower()]


def test_danh_sach_truong_mot_email_hai_ma_bao_mot_dong(tmp_path, dot):
    import csv
    duong = str(tmp_path / "ds.csv")
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "class_id", "email"])
        for i, h in enumerate(dot["hs"], 1):
            w.writerow([h["sid"], "10A1", h["email"]])
        w.writerow(["HS999", "10A2", dot["hs"][0]["email"]])                 # cùng email trên hai mã
    kq = _chuyen(tmp_path / "x", dot, danh_sach_truong=duong)
    dong = [x[2] for x in kq["canh_bao"] if "hai mã" in x[2] or "nhiều mã" in x[2]]
    assert len(dong) == 1 and dot["hs"][0]["email"] in dong[0] and "HS999" in dong[0]
