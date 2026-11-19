"""XP1-L3 — danh sách thành viên dạng PDF: theo CLB và theo lớp. Dữ liệu MÔ PHỎNG.

Không điểm, không số bốc thăm; em chưa có chỗ ở mục riêng; nhiều buổi thì mỗi CLB mỗi buổi một tệp.
"""
import base64
import os
import re

import pytest
from _wharton import tat_wharton
from test_a14_lop_xuat import _dat_lop, _nap

pytest.importorskip("reportlab")

import xuat_pdf  # noqa: E402

try:  # chỉ để đọc lại chữ trong PDF; thiếu thì các ca đọc chữ tự bỏ qua
    import pypdf
except ImportError:
    pypdf = None

can_pypdf = pytest.mark.skipif(pypdf is None, reason="cần pypdf để đọc lại chữ trong PDF")
GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def api(api):
    tat_wharton(api)
    return api


def _chu(duong):
    return "\n".join(p.extract_text() for p in pypdf.PdfReader(duong).pages)


def _tep(thu_muc):
    return sorted(t for t in os.listdir(thu_muc) if t.endswith((".pdf", ".tmp")))


def _tep_cung_cap(tmp_path):
    return sorted(t for t in os.listdir(tmp_path) if t.endswith((".pdf", ".tmp")))


def _dem(api):
    with api._ket_noi_doc() as cur:
        return tuple(cur.execute("SELECT COUNT(*) FROM %s" % b).fetchone()[0]
                     for b in ("match_results", "run_history"))


def _so_dong_ket_qua(api):
    with api._ket_noi_doc() as cur:
        return cur.execute("SELECT COUNT(*) FROM match_results").fetchone()[0]


def _gan_loai(api, club_id, loai):
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET loai = ? WHERE club_id = ?", (loai, club_id))


# ------------------------------------------------------------------ theo CLB

def test_theo_clb_mot_tep_moi_clb_va_tep_chua_duoc_xep(api, tmp_path):
    _nap(api)
    r = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")
    assert r["ok"], r
    d = r["data"]
    assert _tep(d["thu_muc"]) == ["_chua_duoc_xep.pdf", "a.pdf", "b.pdf"]     # a chỉ 1 chỗ nên có em chưa có chỗ
    assert d["n_tep"] == 3 and d["n_trang"] >= 3
    assert d["n_dong"] == _so_dong_ket_qua(api)


@can_pypdf
def test_theo_clb_dong_la_em_duoc_xep_va_co_loai_clb(api, tmp_path):
    _nap(api)
    _gan_loai(api, "a", "GIOI_HAN")
    _gan_loai(api, "b", "TU_DO")
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")["data"]
    with api._ket_noi_doc() as cur:
        xep = {c: sorted(r[0] for r in cur.execute(
            "SELECT student_id FROM match_results WHERE club_id = ?", (c,))) for c in ("a", "b")}
        chua = sorted(r[0] for r in cur.execute(
            "SELECT student_id FROM match_results WHERE club_id IS NULL"))
    for c, nhan in (("a", "Giới hạn"), ("b", "Tự do")):
        chu = _chu(os.path.join(d["thu_muc"], c + ".pdf"))
        assert nhan in chu and "CLB " + c.upper() in chu
        assert sorted(re.findall(r"HS00\d", chu)) == xep[c]
    chu = _chu(os.path.join(d["thu_muc"], "_chua_duoc_xep.pdf"))
    assert sorted(re.findall(r"HS00\d", chu)) == chua and chua


@can_pypdf
def test_khong_diem_khong_so_boc_tham_khong_dien_trung_tuyen(api, tmp_path):
    _nap(api)
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")["data"]
    d2 = api.export_danh_sach_pdf(str(tmp_path / "ra2"), theo="lop")["data"]
    for thu_muc in (d["thu_muc"], d2["thu_muc"]):
        for ten in _tep(thu_muc):
            chu = _chu(os.path.join(thu_muc, ten)).lower()
            for cam in ("điểm", "bốc thăm", "stb", "nguyện vọng", "dự trữ", "trúng tuyển", "reserve"):
                assert cam not in chu, (ten, cam)


def test_nhieu_buoi_moi_clb_moi_buoi_mot_tep(api, tmp_path):
    _nap(api, buoi=True)
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")["data"]
    ten = _tep(d["thu_muc"])
    # mọi em chỉ chọn CLB A: CLB B không có ai được xếp nên không có tệp (như bộ CSV theo CLB)
    assert ten == ["_chua_duoc_xep.pdf", "a_thu_2_thu_2.pdf", "a_thu_3_thu_3.pdf"]
    assert d["n_dong"] == _so_dong_ket_qua(api)


@can_pypdf
def test_nhieu_buoi_tieu_de_ghi_ro_buoi(api, tmp_path):
    _nap(api, buoi=True)
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")["data"]
    chu = _chu(os.path.join(d["thu_muc"], "a_thu_2_thu_2.pdf"))
    assert "Thứ 2" in chu and "Thứ 3" not in chu


def test_ten_clb_co_gach_cheo_va_dau_thanh_ten_tep_an_toan(api, tmp_path):
    api.create_or_update_club("Â/B", "CLB Â/B", 5, 0, "")
    api.create_or_update_club("a\\b", "CLB lạ", 5, 0, "")
    assert api.import_preferences_csv("student_id,name,pref_1\nHS001,Em 1,Â/B\nHS002,Em 2,a\\b\n")["ok"]
    assert api.run_pipeline(seed=7)["ok"]
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")["data"]
    ten = _tep(d["thu_muc"])
    assert len(ten) == 2 and all("/" not in t and "\\" not in t for t in ten) and "Â_B.pdf" in ten


# ------------------------------------------------------------------ theo lớp

def test_theo_lop_mot_tep_moi_lop_va_chua_co_lop(api, tmp_path):
    _nap(api)
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="lop")["data"]
    assert _tep(d["thu_muc"]) == ["10A1.pdf", "10A10.pdf", "10A2.pdf", "_chua_co_lop.pdf"]
    assert d["n_tep"] == 4 and d["n_dong"] == _so_dong_ket_qua(api)


@can_pypdf
def test_theo_lop_moi_tep_chi_co_em_cua_lop_do_va_ghi_clb(api, tmp_path):
    _nap(api)
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="lop")["data"]
    chu = _chu(os.path.join(d["thu_muc"], "10A2.pdf"))
    assert sorted(re.findall(r"HS00\d", chu)) == ["HS001", "HS003"]
    with api._ket_noi_doc() as cur:
        ten = {r[0]: r[1] for r in cur.execute(
            "SELECT m.student_id, c.name FROM match_results m JOIN clubs c ON c.club_id = m.club_id")}
    assert ten["HS001"] in chu and ten["HS003"] in chu and "HS002" not in chu and "HS004" not in chu


@can_pypdf
def test_theo_lop_em_chua_co_cho_o_muc_rieng(api, tmp_path):
    _nap(api)
    with api._ket_noi_doc() as cur:
        chua = [r[0] for r in cur.execute("SELECT student_id FROM match_results WHERE club_id IS NULL")]
    assert chua
    _dat_lop(api, chua[0], "10A7")
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="lop")["data"]
    chu = _chu(os.path.join(d["thu_muc"], "10A7.pdf"))
    assert "Chưa có câu lạc bộ" in chu and chua[0] in chu


def test_theo_lop_nhieu_buoi_mot_tep_moi_lop(api, tmp_path):
    _nap(api, buoi=True)
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="lop")["data"]
    assert _tep(d["thu_muc"]) == ["10A1.pdf", "10A10.pdf", "10A2.pdf", "_chua_co_lop.pdf"]


def test_ten_lop_co_gach_cheo_thanh_ten_tep_an_toan(api, tmp_path):
    _nap(api)
    _dat_lop(api, "HS001", "10/Ánh")
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="lop")["data"]
    assert "10_Ánh.pdf" in _tep(d["thu_muc"])


# ------------------------------------------------------------------ chung

def test_chua_co_ket_qua_tu_choi_va_khong_tao_gi(api, tmp_path):
    r = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")
    assert not r["ok"] and r["errors"][0]["code"] == "xuat_chua_co_ket_qua"
    assert not (tmp_path / "ra").exists()


def test_kieu_xuat_la_bi_tu_choi(api, tmp_path):
    _nap(api)
    r = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="buoi")
    assert not r["ok"] and r["errors"][0]["code"] == "xp1_kieu_xuat_la"
    assert not (tmp_path / "ra").exists()


def test_khong_ghi_de_thu_muc_co_san(api, tmp_path):
    _nap(api)
    a = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")["data"]["thu_muc"]
    b = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")["data"]["thu_muc"]
    assert a != b and b.endswith("ra (2)") and _tep(a) == _tep(b)


def test_mac_dinh_vao_thu_muc_tai_ve(api, tmp_path):
    _nap(api)
    api.thu_muc_xuat = str(tmp_path / "tv")
    os.makedirs(api.thu_muc_xuat)
    d = api.export_danh_sach_pdf("", theo="lop")["data"]
    assert os.path.basename(d["thu_muc"]) == "danh_sach_theo_lop"
    d = api.export_danh_sach_pdf("", theo="clb")["data"]
    assert os.path.basename(d["thu_muc"]) == "danh_sach_theo_clb"


def test_khong_doi_du_lieu(api, tmp_path):
    _nap(api)
    truoc = _dem(api)
    assert api.export_danh_sach_pdf(str(tmp_path / "a"), theo="clb")["ok"]
    assert api.export_danh_sach_pdf(str(tmp_path / "b"), theo="lop")["ok"]
    assert _dem(api) == truoc


def test_thieu_thu_vien_pdf_bao_loi_va_khong_de_lai_thu_muc(api, tmp_path, monkeypatch):
    _nap(api)
    monkeypatch.setattr(xuat_pdf, "_THU_MUC_PHONG", str(tmp_path / "khong_co"))
    monkeypatch.setattr(xuat_pdf, "_da_dang_ky", False)
    r = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")
    assert not r["ok"] and r["errors"][0]["code"] == "xp1_thieu_thu_vien_pdf"
    assert not (tmp_path / "ra").exists()


def test_chi_quan_tri():
    import phan_quyen
    assert phan_quyen.QUYEN["export_danh_sach_pdf"] == phan_quyen.QUAN_TRI


def test_so_that_ba_buoi_dong_bang_ket_qua_va_khong_lo_so_lieu(api, tmp_path):
    """Sổ mẫu 3 buổi có điểm thi: số dòng trong các tệp = số dòng match_results."""
    with open(os.path.join(GOC, "du_lieu_test", "SO_NHAP_MAU_120HS_3BUOI.xlsx"), "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    assert api.run_pipeline(seed=3)["ok"]
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")["data"]
    assert d["n_dong"] == _so_dong_ket_qua(api) and d["n_tep"] == len(_tep(d["thu_muc"])) > 3
    d2 = api.export_danh_sach_pdf(str(tmp_path / "rb"), theo="lop")["data"]
    assert d2["n_dong"] == d["n_dong"]


# ------------------------------------------------------------------ vòng sửa 3: cột STT, đếm em, chữ hoa đầu tiêu đề

def test_cot_stt_du_rong_cho_chu_stt_va_so_ba_chu_so():
    """Luôn chạy (không cần pypdf): cột STT phải chứa tiêu đề "STT" và số tới 4 chữ số trên một dòng."""
    import danh_sach_pdf
    from reportlab.pdfbase import pdfmetrics
    xuat_pdf.san_sang()
    for so_cot in (4, 5, 8):
        b = danh_sach_pdf.bang_danh_sach(["STT"] + ["Cột %d" % i for i in range(so_cot - 1)],
                                         [[1] + ["x"] * (so_cot - 1)])
        can = max(pdfmetrics.stringWidth("STT", "BeVietnamPro-Bold", 9),
                  pdfmetrics.stringWidth("0000", "BeVietnamPro", 9)) + 12      # 12 = đệm trái + phải của ô
        assert b._colWidths[0] >= can, (so_cot, b._colWidths[0], can)


@can_pypdf
def test_stt_khong_bi_cat_chu_trong_tep_nhieu_buoi(api, tmp_path):
    _nap(api, buoi=True)
    for theo in ("lop", "clb"):
        d = api.export_danh_sach_pdf(str(tmp_path / theo), theo=theo)["data"]
        ten = "10A2.pdf" if theo == "lop" else "_chua_duoc_xep.pdf"
        dong = _chu(os.path.join(d["thu_muc"], ten)).split("\n")
        assert "STT" in dong and "S" not in dong and "T" not in dong, (theo, dong[:12])


@can_pypdf
def test_chua_duoc_xep_nhieu_buoi_dem_so_em_khong_dem_luot(api, tmp_path):
    _nap(api, buoi=True)
    with api._ket_noi_doc() as cur:
        luot = cur.execute("SELECT COUNT(*) FROM match_results WHERE club_id IS NULL").fetchone()[0]
        em = cur.execute("SELECT COUNT(DISTINCT student_id) FROM match_results WHERE club_id IS NULL").fetchone()[0]
    assert luot > em > 0                      # dữ liệu thử có em chưa có chỗ ở cả hai buổi
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")["data"]
    chu = _chu(os.path.join(d["thu_muc"], "_chua_duoc_xep.pdf"))
    assert "Số học sinh: %d\n" % em in chu + "\n" and "Số học sinh: %d\n" % luot not in chu + "\n"
    assert "Số lượt chưa có chỗ: %d" % luot in chu


@can_pypdf
def test_tieu_de_viet_hoa_chu_dau(api, tmp_path):
    _nap(api)
    d = api.export_danh_sach_pdf(str(tmp_path / "ra"), theo="clb")["data"]
    dong = _chu(os.path.join(d["thu_muc"], "_chua_duoc_xep.pdf")).split("\n")
    assert dong[0] == "Học sinh chưa có câu lạc bộ", dong[0]


def test_hoa_dau_giu_nguyen_phan_con_lai():
    import danh_sach_pdf
    assert danh_sach_pdf.hoa_dau("học sinh chưa có CLB") == "Học sinh chưa có CLB"
    assert danh_sach_pdf.hoa_dau("Đã đủ") == "Đã đủ" and danh_sach_pdf.hoa_dau("đã đủ") == "Đã đủ"
    assert danh_sach_pdf.hoa_dau("") == ""
