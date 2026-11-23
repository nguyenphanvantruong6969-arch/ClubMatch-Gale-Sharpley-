"""ST-B: build mutated import files (SIMULATED) from the shared Sổ."""
import io
import shutil

import openpyxl

from conftest import SO_150


def _sua(fn):
    wb = openpyxl.load_workbook(SO_150)
    fn(wb)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def goc():
    return open(SO_150, "rb").read()


def _xoa_sheet_clb(wb):
    del wb["1. CLB"]


def _xoa_sheet_hs(wb):
    del wb["2. Học sinh"]


def _chi_tieu(v):
    def f(wb):
        wb["1. CLB"]["C2"] = v
    return f


def _trung_ma(wb):
    ws = wb["2. Học sinh"]
    ws["A4"] = ws["A3"].value


def _hoa_thuong(wb):
    ws = wb["2. Học sinh"]
    ws["A3"] = ws["A3"].value.lower()
    ws["D3"] = ws["D3"].value.upper()


def _ten_clb_trung(wb):
    ws = wb["1. CLB"]
    ws["A3"] = ws["A2"].value


def _o_dai(wb):
    wb["2. Học sinh"]["B3"] = "A" * 40000


def _cong_thuc(wb):
    ws = wb["2. Học sinh"]
    ws["B3"] = "=1+1"
    ws["B4"] = "=cmd|' /C calc'!A0"
    ws["B5"] = "@SUM(1,1)"


def _xss(wb):
    """Appends a club and a student whose NAMES carry markup; ids stay plain."""
    c = wb["1. CLB"]
    c.append(["<b onmouseover=\"window.__xss=1\">CLB XSS</b>", "Thứ 3", 10, None, None, "XSS_1", "Giới hạn", None, None, None])
    h = wb["2. Học sinh"]
    h.append(["XSS01", "<img src=x onerror=\"window.__xss=1\">", None, "<b onmouseover=\"window.__xss=1\">CLB XSS</b>", 5, 60,
              "CLB Bóng rổ", 5, 30])


def _diem_dau_phay(wb):
    wb["2. Học sinh"]["E3"] = "9,5"


def _diem_am(wb):
    wb["2. Học sinh"]["E3"] = -3
    wb["2. Học sinh"]["E4"] = 1e9


def _ngay(wb):
    import datetime
    wb["2. Học sinh"]["E3"] = datetime.datetime(2026, 1, 2)


def _gop_o(wb):
    wb["2. Học sinh"].merge_cells("D3:F4")


def _mot_dong_tieu_de(wb):
    wb["2. Học sinh"].delete_rows(2)


def _rong_hoc_sinh(wb):
    ws = wb["2. Học sinh"]
    ws.delete_rows(3, ws.max_row)


def _rong_clb(wb):
    ws = wb["1. CLB"]
    ws.delete_rows(2, ws.max_row)


def _nhieu_dong(wb):
    ws = wb["2. Học sinh"]
    for i in range(3000):
        ws.append(["Z%05d" % i, "Hs %d" % i, None, "CLB Bóng rổ", 5, None])


def _clb_la(wb):
    wb["2. Học sinh"]["D3"] = "CLB Không Tồn Tại"


def _nfd(wb):
    import unicodedata
    ws = wb["2. Học sinh"]
    ws["D3"] = unicodedata.normalize("NFD", ws["D3"].value)
    ws["B4"] = " " + ws["B4"].value + "  "


def _huy_chuong_sai(wb):
    wb["2. Học sinh"]["F3"] = 77
    wb["2. Học sinh"]["I3"] = 77


def _loai_sai(wb):
    wb["1. CLB"]["G2"] = "Xyz"


CAC_TEP = {
    "rong_0_byte": (lambda: b"", "so.xlsx"),
    "van_ban_doi_duoi_xlsx": (lambda: b"hello world not a zip", "so.xlsx"),
    "xlsx_cat_cut": (lambda: goc()[:len(goc()) // 2], "so.xlsx"),
    "xlsx_doi_duoi_xls": (goc, "so.xls"),
    "duoi_pdf": (goc, "so.pdf"),
    "thieu_sheet_clb": (lambda: _sua(_xoa_sheet_clb), "so.xlsx"),
    "thieu_sheet_hoc_sinh": (lambda: _sua(_xoa_sheet_hs), "so.xlsx"),
    "sheet_clb_rong": (lambda: _sua(_rong_clb), "so.xlsx"),
    "sheet_hoc_sinh_rong": (lambda: _sua(_rong_hoc_sinh), "so.xlsx"),
    "chi_tieu_0": (lambda: _sua(_chi_tieu(0)), "so.xlsx"),
    "chi_tieu_am": (lambda: _sua(_chi_tieu(-5)), "so.xlsx"),
    "chi_tieu_1e9": (lambda: _sua(_chi_tieu(10 ** 9)), "so.xlsx"),
    "chi_tieu_chu": (lambda: _sua(_chi_tieu("abc")), "so.xlsx"),
    "trung_ma_hs": (lambda: _sua(_trung_ma), "so.xlsx"),
    "ma_hoa_thuong": (lambda: _sua(_hoa_thuong), "so.xlsx"),
    "ten_clb_trung": (lambda: _sua(_ten_clb_trung), "so.xlsx"),
    "o_text_40k": (lambda: _sua(_o_dai), "so.xlsx"),
    "cong_thuc": (lambda: _sua(_cong_thuc), "so.xlsx"),
    "xss": (lambda: _sua(_xss), "so.xlsx"),
    "diem_dau_phay": (lambda: _sua(_diem_dau_phay), "so.xlsx"),
    "diem_am_va_1e9": (lambda: _sua(_diem_am), "so.xlsx"),
    "diem_la_ngay": (lambda: _sua(_ngay), "so.xlsx"),
    "o_gop": (lambda: _sua(_gop_o), "so.xlsx"),
    "mot_dong_tieu_de": (lambda: _sua(_mot_dong_tieu_de), "so.xlsx"),
    "3000_dong_them": (lambda: _sua(_nhieu_dong), "so.xlsx"),
    "clb_khong_ton_tai": (lambda: _sua(_clb_la), "so.xlsx"),
    "nfd_khoang_trang": (lambda: _sua(_nfd), "so.xlsx"),
    "huy_chuong_77": (lambda: _sua(_huy_chuong_sai), "so.xlsx"),
    "loai_sai": (lambda: _sua(_loai_sai), "so.xlsx"),
    "csv_utf16": ("a,b\r\n1,2\r\n".encode("utf-16"), "du_lieu.csv"),
    "csv_cp1258": (__import__("unicodedata").normalize("NFD", "Mã HS,Họ tên\r\nHS1,Nguyễn Văn A\r\n").encode("cp1258", "replace"), "du_lieu.csv"),
    "csv_rong": (b"", "du_lieu.csv"),
    "csv_bom_chi_tieu_de": ("﻿club_id,name,capacity\n".encode("utf-8"), "du_lieu.csv"),
    "zip_hong": (b"PK\x03\x04" + b"\x00" * 50, "ws.zip"),
}


def so_nhan_ban(lan):
    """The shared Sổ with the 150 students copied `lan` times (new ids, full preferences, tests, medals)."""
    def f(wb):
        h = wb["2. Học sinh"]
        goc_hang = [[c.value for c in r] for r in h.iter_rows(min_row=3, max_row=152)]
        for k in range(1, lan):
            for r in goc_hang:
                n = list(r)
                n[0] = "%s_%d" % (r[0], k)
                h.append(n)
        c = wb["1. CLB"]
        for r in range(2, c.max_row + 1):
            if isinstance(c.cell(r, 3).value, (int, float)):
                c.cell(r, 3).value = int(c.cell(r, 3).value) * lan
    return _sua(f)
