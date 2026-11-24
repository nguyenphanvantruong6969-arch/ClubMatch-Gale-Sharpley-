# -*- coding: utf-8 -*-
"""DC1 — kiểm độc lập đầu vào ⇄ kết quả (phạm vi B: chỉ kiểm bảo toàn).

Bộ kiểm thử đột biến: lấy một bộ xuất HỢP LỆ từ `SO_NHAP_TEST.xlsx` (seed 3), sửa MỘT chỗ,
và khẳng định đúng phép kiểm Kx báo FAIL. Dữ liệu là dữ liệu MÔ PHỎNG.
"""
import ast
import base64
import csv
import os
import shutil
import sys

import openpyxl
import pytest

from _wharton import tat_wharton

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC_SCRIPT = os.path.join(GOC, "du_lieu_test", "kiem_doc_lap")
DLT = os.path.join(GOC, "du_lieu_test")
sys.path.insert(0, THU_MUC_SCRIPT)
import kiem_doc_lap as kdl  # noqa: E402

SO_NHAP_TEST = os.path.join(DLT, "SO_NHAP_TEST.xlsx")


def xuat_bo(so_nhap, thu_muc, seed=3):
    """Nạp Sổ nhập, chạy, xuất CSV mặc định; trả về đường dẫn tệp kết quả chính."""
    from api import PipelineAPI
    os.makedirs(thu_muc, exist_ok=True)
    a = PipelineAPI(os.path.join(thu_muc, "app.db"))
    tat_wharton(a)
    with open(so_nhap, "rb") as f:
        kq = a.import_so_nhap(base64.b64encode(f.read()).decode())
    assert kq["ok"], kq
    assert a.run_pipeline(seed=seed)["ok"]
    chinh = os.path.join(thu_muc, "ket_qua_phan_bo.csv")
    assert a.export_csv(chinh)["ok"]
    return chinh


@pytest.fixture(scope="module")
def goc_xuat(tmp_path_factory):
    thu_muc = str(tmp_path_factory.mktemp("dc1_goc"))
    return xuat_bo(SO_NHAP_TEST, thu_muc)


@pytest.fixture
def bo(goc_xuat, tmp_path):
    """Bản sao riêng của bộ xuất để mỗi test được sửa thoải mái."""
    cho = tmp_path / "bo"
    thu_muc_goc = os.path.dirname(goc_xuat)
    cho.mkdir()
    for ten in os.listdir(thu_muc_goc):
        nguon = os.path.join(thu_muc_goc, ten)
        if ten.startswith("ket_qua_phan_bo") and ten.endswith(".csv"):
            shutil.copy(nguon, cho / ten)
        elif ten == "ket_qua_phan_bo_theo_club":
            shutil.copytree(nguon, cho / ten)
    return str(cho / "ket_qua_phan_bo.csv")


def doc(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def ghi(path, dong):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(dong)


def chay(capsys, so_nhap, ket_qua, ra=None):
    argv = ["--so-nhap", so_nhap, "--ket-qua", ket_qua]
    if ra:
        argv += ["--ra", ra]
    ma = kdl.main(argv)
    return ma, capsys.readouterr().out


def trang_thai(out, ma_kiem):
    for dong in out.splitlines():
        if dong.startswith(ma_kiem + " "):
            return dong.split()[1]
    raise AssertionError(f"không thấy {ma_kiem} trong:\n{out}")


def doc_so_nhap_clb():
    wb = openpyxl.load_workbook(SO_NHAP_TEST, data_only=True)
    return {r[5]: r for r in wb["1. CLB"].iter_rows(min_row=2, values_only=True) if r[0]}


# ---------------------------------------------------------------- hợp lệ ----

def test_bo_hop_le_pass_het(capsys, bo, tmp_path):
    ma, out = chay(capsys, SO_NHAP_TEST, bo, str(tmp_path / "ra.csv"))
    assert ma == 0, out
    for k in ("K0", "K1", "K2", "K3", "K4", "K5", "K6"):
        assert trang_thai(out, k) == "PASS", out


# --------------------------------------------------------- đột biến K1..K6 ----

def test_k1_thieu_dong(capsys, bo):
    d = doc(bo)
    del d[5]
    ghi(bo, d)
    ma, out = chay(capsys, SO_NHAP_TEST, bo)
    assert ma == 1 and trang_thai(out, "K1") == "FAIL", out


def test_k1_trung_dong(capsys, bo):
    d = doc(bo)
    d.append(list(d[7]))
    ghi(bo, d)
    ma, out = chay(capsys, SO_NHAP_TEST, bo)
    assert ma == 1 and trang_thai(out, "K1") == "FAIL", out


def test_k2_vuot_chi_tieu(capsys, bo):
    clb = doc_so_nhap_clb()
    d = doc(bo)
    dem = {}
    for r in d[1:]:
        if r[3]:
            dem[r[3]] = dem.get(r[3], 0) + 1
    # CLB đã đầy chỉ tiêu (hoặc gần nhất) -> nhét thêm một em từ CLB khác vào.
    day = max(dem, key=lambda c: dem[c] / clb[c][2])
    thieu = clb[day][2] - dem[day]
    chuyen = [r for r in d[1:] if r[3] and r[3] != day][: thieu + 1]
    for r in chuyen:
        r[3], r[4] = day, clb[day][0]
    ghi(bo, d)
    ma, out = chay(capsys, SO_NHAP_TEST, bo)
    assert ma == 1 and trang_thai(out, "K2") == "FAIL", out


def test_k3_vuot_suat_du_tru(capsys, bo):
    clb = doc_so_nhap_clb()
    d = doc(bo)
    co_suat = [c for c, r in clb.items() if r[3]]
    c = co_suat[0]
    quota = clb[c][3]
    hien = sum(1 for r in d[1:] if r[3] == c and r[6] == "Dự trữ")
    can = quota - hien + 1
    thuong = [r for r in d[1:] if r[3] == c and r[6] == "Thường"][:can]
    assert len(thuong) == can, "dữ liệu không đủ em Thường để đột biến"
    for r in thuong:
        r[6] = "Dự trữ"
    ghi(bo, d)
    ma, out = chay(capsys, SO_NHAP_TEST, bo)
    assert ma == 1 and trang_thai(out, "K3") == "FAIL", out


def test_k4_clb_ngoai_nguyen_vong(capsys, bo):
    d = doc(bo)
    wb = openpyxl.load_workbook(SO_NHAP_TEST, data_only=True)
    ten2ma = {r[0]: r[5] for r in wb["1. CLB"].iter_rows(min_row=2, values_only=True) if r[0]}
    ma2ten = {v: k for k, v in ten2ma.items()}
    nv = {}
    for r in wb["2. Học sinh"].iter_rows(min_row=2, values_only=True):
        if r[0]:
            nv[r[0]] = {ten2ma.get(x) for x in r[3::2] if x}
    for r in d[1:]:
        if r[3]:
            ngoai = next(c for c in ma2ten if c not in nv[r[0]])
            r[3], r[4] = ngoai, ma2ten[ngoai]
            break
    ghi(bo, d)
    ma, out = chay(capsys, SO_NHAP_TEST, bo)
    assert ma == 1 and trang_thai(out, "K4") == "FAIL", out


def test_k5_sai_thu_hang(capsys, bo):
    d = doc(bo)
    for r in d[1:]:
        if r[3] and r[5] == "1":
            r[5] = "3"
            break
    ghi(bo, d)
    ma, out = chay(capsys, SO_NHAP_TEST, bo)
    assert ma == 1 and trang_thai(out, "K5") == "FAIL", out


def test_k6_tep_theo_clb_thieu_dong(capsys, bo):
    thu_muc = os.path.splitext(bo)[0] + "_theo_club"
    tep = os.path.join(thu_muc, "clb_tinhoc.csv")
    d = doc(tep)
    del d[1]
    ghi(tep, d)
    ma, out = chay(capsys, SO_NHAP_TEST, bo)
    assert ma == 1 and trang_thai(out, "K6") == "FAIL", out


def test_k0_clb_khong_doi_chieu_duoc(capsys, bo):
    d = doc(bo)
    for r in d[1:]:
        if r[3]:
            r[3], r[4] = "clb_la_hoac", "CLB Không Có Trong Sổ"
            break
    ghi(bo, d)
    ma, out = chay(capsys, SO_NHAP_TEST, bo)
    assert ma == 1 and trang_thai(out, "K0") == "FAIL", out


def test_nhieu_buoi_thoat_2(capsys, bo):
    d = doc(bo)
    d = [r[:3] + ["Thứ 2"] + r[3:] for r in d]
    ghi(bo, d)
    ma, out = chay(capsys, SO_NHAP_TEST, bo)
    assert ma == 2
    assert "nhiều buổi" in (out + capsys.readouterr().err)


def test_thieu_tep_thoat_2(capsys, tmp_path):
    ma = kdl.main(["--so-nhap", SO_NHAP_TEST, "--ket-qua", str(tmp_path / "khong_co.csv")])
    assert ma == 2


# ------------------------------------------------------------- cô lập ----

def test_script_chi_dung_thu_vien_chuan_va_openpyxl():
    mo = os.path.join(THU_MUC_SCRIPT, "kiem_doc_lap.py")
    cay = ast.parse(open(mo, encoding="utf-8").read())
    cho_phep = set(sys.stdlib_module_names) | {"openpyxl"}
    for nut in ast.walk(cay):
        if isinstance(nut, ast.Import):
            for a in nut.names:
                assert a.name.split(".")[0] in cho_phep, a.name
        elif isinstance(nut, ast.ImportFrom):
            assert nut.level == 0, "không import tương đối"
            assert nut.module.split(".")[0] in cho_phep, nut.module
        elif isinstance(nut, ast.Attribute) and nut.attr == "path":
            assert not (isinstance(nut.value, ast.Name) and nut.value.id == "sys"), "không sửa sys.path"


# ----------------------------------------------- L2: dương tính giả (D6) ----

def loc_mot_buoi(nguon, dich, buoi="Thứ 2"):
    """Từ Sổ nhập nhiều buổi dựng Sổ nhập MỘT buổi: giữ CLB của `buoi`, xoá cột Buổi, bỏ nguyện vọng
    tới CLB đã bỏ (dồn trái các nguyện vọng còn lại). Hỗ trợ cả hai kiểu tiêu đề."""
    wb = openpyxl.load_workbook(nguon)
    ws1, ws2 = wb["1. CLB"], wb["2. Học sinh"]
    giu = [list(r) for r in ws1.iter_rows(min_row=2, values_only=True) if r[0] and r[1] == buoi]
    ten_giu = {r[0] for r in giu}
    ws1.delete_rows(2, ws1.max_row)
    for i, r in enumerate(giu, start=2):
        r[1] = None
        for j, v in enumerate(r, start=1):
            ws1.cell(i, j, v)
    hai_dong = str(ws2.cell(1, 4).value or "").startswith("Nguyện vọng")
    dau, rong = (3, 3) if hai_dong else (2, 2)   # dòng dữ liệu đầu; bề rộng một nhóm nguyện vọng
    du = [[c.value for c in row] for row in ws2.iter_rows(min_row=dau) if row[0].value]
    ncot = ws2.max_column
    ws2.delete_rows(dau, ws2.max_row)
    for i, r in enumerate(du, start=dau):
        cac_nhom = [r[c:c + rong] for c in range(3, ncot, rong)]
        con = [g for g in cac_nhom if g and g[0] in ten_giu]
        phang = [v for g in con for v in g]
        moi = r[:3] + phang + [None] * (ncot - 3 - len(phang))
        for j, v in enumerate(moi, start=1):
            ws2.cell(i, j, v)
    wb.save(dich)
    return dich


@pytest.fixture(scope="module", params=["TEST", "DQT_120HS", "MAU_3BUOI"])
def bo_hop_le(request, tmp_path_factory):
    thu_muc = str(tmp_path_factory.mktemp("dc1_" + request.param))
    if request.param == "TEST":
        so = SO_NHAP_TEST
    else:
        nguon = {"DQT_120HS": "SO_NHAP_DQT_120HS_HOP_LE.xlsx",
                 "MAU_3BUOI": "SO_NHAP_MAU_120HS_3BUOI.xlsx"}[request.param]
        so = loc_mot_buoi(os.path.join(DLT, nguon), os.path.join(thu_muc, "so_nhap.xlsx"))
    return so, xuat_bo(so, os.path.join(thu_muc, "xuat"))


def test_ba_bo_hop_le_pass_het(capsys, bo_hop_le, tmp_path):
    so, chinh = bo_hop_le
    ma, out = chay(capsys, so, chinh, str(tmp_path / "ra.csv"))
    assert ma == 0, out
    assert "7 PASS, 0 FAIL" in out


def test_csv_dau_vao_mot_dong_moi_hoc_sinh(capsys, bo_hop_le, tmp_path):
    so, chinh = bo_hop_le
    ra = str(tmp_path / "ra.csv")
    assert chay(capsys, so, chinh, ra)[0] == 0
    _, hs = kdl.doc_so_nhap(so)
    d = doc(ra)
    assert d[0][:3] == ["student_id", "ho_ten", "nhom"] and d[0][-4:] == [
        "club_id_nhan", "ten_clb_nhan", "dien", "hang_nhan"]
    assert [r[0] for r in d[1:]] == [h["id"] for h in hs]
    xuat = {r[0]: r[3] for r in doc(chinh)[1:]}
    i = d[0].index("club_id_nhan")
    assert all(r[i] == xuat[r[0]] for r in d[1:])
