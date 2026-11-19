"""XP1-L1 — lõi PDF: phông Việt nhúng, bảng tự ngắt trang, "Trang x/y", không ghi đè."""
import os

import pytest

pytest.importorskip("reportlab")
import xuat_pdf  # noqa: E402

try:  # chỉ để đọc lại chữ; thiếu thì các ca đọc chữ tự bỏ qua, ca mức byte vẫn chạy
    import pypdf
except ImportError:
    pypdf = None

can_pypdf = pytest.mark.skipif(pypdf is None, reason="cần pypdf để đọc lại chữ trong PDF")


def _n_trang(duong):
    """Số trang đọc thẳng từ byte (không cần pypdf): nút gốc cây trang `/Count n`."""
    with open(duong, "rb") as f:
        b = f.read()
    import re
    return max(int(m) for m in re.findall(rb"/Count (\d+)", b))


def _tep(thu_muc):
    # conftest tạo thêm thư mục "TaiXuong_gia" trong tmp_path; chỉ xét tệp.
    return sorted(t for t in os.listdir(thu_muc) if os.path.isfile(os.path.join(thu_muc, t)))


def _doc(duong):
    return pypdf.PdfReader(duong)


def _chu(duong):
    return "\n".join(p.extract_text() for p in _doc(duong).pages)


def _trang_ba(ten):
    kv = xuat_pdf.dong_khoa_gia_tri
    return [
        xuat_pdf.tieu_de("Danh sách Nguyễn Văn Ánh"),
        kv("Lớp", "10A1"),
        xuat_pdf.bang(["Họ tên", "Lớp"], [["Nguyễn Văn Ánh", "10A1"], ["Lê Đức Cường", "10A2"]]),
        xuat_pdf.ngat_trang(),
        xuat_pdf.tieu_de("Trang hai Lê Đức Cường"),
        xuat_pdf.ngat_trang(),
        xuat_pdf.tieu_de("Trang ba"),
    ]


def test_ba_trang_dem_theo_byte(tmp_path):
    ra = str(tmp_path / "a.pdf")
    xuat_pdf.dung_pdf(ra, _trang_ba("x"))
    assert _n_trang(ra) == 3


@can_pypdf
def test_ba_trang_va_chu_viet_doc_lai_duoc(tmp_path):
    ra = str(tmp_path / "a.pdf")
    xuat_pdf.dung_pdf(ra, _trang_ba("x"))
    assert len(_doc(ra).pages) == 3
    chu = _chu(ra)
    assert "Nguyễn Văn Ánh" in chu and "Lê Đức Cường" in chu


def test_phong_duoc_nhung(tmp_path):
    ra = str(tmp_path / "a.pdf")
    xuat_pdf.dung_pdf(ra, _trang_ba("x"))
    with open(ra, "rb") as f:
        b = f.read()
    assert b"BeVietnamPro" in b and b"/FontFile2" in b


@can_pypdf
def test_chan_trang_trang_x_tren_y(tmp_path):
    ra = str(tmp_path / "a.pdf")
    xuat_pdf.dung_pdf(ra, _trang_ba("x"))
    p = _doc(ra).pages
    assert "Trang 1/3" in p[0].extract_text() and "Trang 3/3" in p[2].extract_text()


@can_pypdf
def test_bang_dai_ngat_trang_va_lap_tieu_de_cot(tmp_path):
    ra = str(tmp_path / "a.pdf")
    hang = [[f"Em {i}", "10A1"] for i in range(150)]
    xuat_pdf.dung_pdf(ra, [xuat_pdf.bang(["Họ tên", "Lớp"], hang)])
    p = _doc(ra).pages
    assert len(p) >= 3
    assert all("Họ tên" in t.extract_text() for t in p)
    assert "Em 149" in p[-1].extract_text()


@can_pypdf
def test_o_bang_dai_tu_xuong_dong(tmp_path):
    ra = str(tmp_path / "a.pdf")
    dai = "Câu lạc bộ " + "rất dài " * 60
    xuat_pdf.dung_pdf(ra, [xuat_pdf.bang(["Tên"], [[dai]])])
    assert "rất dài" in _chu(ra)


@can_pypdf
def test_ky_tu_dac_biet_khong_vo_markup(tmp_path):
    ra = str(tmp_path / "a.pdf")
    xuat_pdf.dung_pdf(ra, [xuat_pdf.tieu_de("A <b>& B</b> <x>"),
                           xuat_pdf.bang(["c"], [["1 < 2 & 3 > 2"]])])
    chu = _chu(ra)
    assert "<b>& B</b>" in chu and "1 < 2 & 3 > 2" in chu


def test_khong_ghi_de_tep_co_san(tmp_path):
    ra = tmp_path / "a.pdf"
    ra.write_bytes(b"cu")
    thuc = xuat_pdf.dung_pdf(str(ra), [xuat_pdf.tieu_de("moi")])
    assert ra.read_bytes() == b"cu"
    assert thuc == str(tmp_path / "a (2).pdf") and os.path.exists(thuc)


def test_ghi_qua_tep_tam_roi_doi_ten_khong_de_lai_tep_tam(tmp_path):
    xuat_pdf.dung_pdf(str(tmp_path / "a.pdf"), [xuat_pdf.tieu_de("x")])
    assert _tep(tmp_path) == ["a.pdf"]


def test_loi_giua_chung_khong_de_lai_tep(tmp_path):
    with pytest.raises(Exception):
        xuat_pdf.dung_pdf(str(tmp_path / "a.pdf"), ["khong phai khoi"])
    assert _tep(tmp_path) == []


def test_thieu_phong_bao_loi_ro(tmp_path, monkeypatch):
    monkeypatch.setattr(xuat_pdf, "_THU_MUC_PHONG", str(tmp_path / "khong_co"))
    monkeypatch.setattr(xuat_pdf, "_da_dang_ky", False)
    with pytest.raises(xuat_pdf.ThieuThuVienPdf):
        xuat_pdf.dung_pdf(str(tmp_path / "a.pdf"), [xuat_pdf.tieu_de("x")])


def test_bang_dai_ngat_trang_theo_byte(tmp_path):
    ra = str(tmp_path / "a.pdf")
    hang = [[f"Em {i}", "10A1"] for i in range(150)]
    xuat_pdf.dung_pdf(ra, [xuat_pdf.bang(["Họ tên", "Lớp"], hang)])
    assert _n_trang(ra) >= 3


def test_ky_tu_dac_biet_khong_gay_loi_theo_byte(tmp_path):
    ra = str(tmp_path / "a.pdf")
    xuat_pdf.dung_pdf(ra, [xuat_pdf.tieu_de("A <b>& B</b> <x>"),
                           xuat_pdf.bang(["c"], [["1 < 2 & 3 > 2"]])])
    assert _n_trang(ra) == 1
