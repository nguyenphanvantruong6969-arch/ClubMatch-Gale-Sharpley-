# -*- coding: utf-8 -*-
"""Từ SO_NHAP_300HS_DOI_CHE_DO.xlsx sinh hai sổ CỐ Ý SAI để chụp thông báo lỗi — DỮ LIỆU MÔ PHỎNG.
  SO_NHAP_300HS_LOI_CLB.xlsx : lỗi ở sheet CLB (thiếu chỉ tiêu, suất ưu tiên > chỉ tiêu) — chặn nhập.
  SO_NHAP_300HS_LOI_HS.xlsx  : sheet CLB đúng; lỗi/thiếu ở sheet học sinh (trùng mã, thiếu mã, CLB không có,
                               điểm sai dạng) — chặn nhập.
  SO_NHAP_300HS_THIEU_XUNG_DOT.xlsx : nhập được; một em không khai nguyện vọng (thiếu dữ liệu) và một em
                               đặt hai huy chương Vàng cùng buổi (tiêu chí xung đột).
    python docs/bao_cao_300hs/sinh_so_co_loi.py
"""
import os
import openpyxl
D = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.join(D, "SO_NHAP_300HS_DOI_CHE_DO.xlsx")

# Mỗi lỗi: (mô tả, hàm sửa sheet)
LOI_CLB = [
    ("CLB Bóng rổ (Thứ 3) bỏ trống Chỉ tiêu", lambda c: setattr(c.cell(3, 3), "value", None)),
    ("CLB Cờ vua: Suất ưu tiên 80 > Chỉ tiêu 50, không ghi nhóm", lambda c: c.cell(4, 4, 80)),
]
LOI_HS = [
    ("DC003 đổi mã thành DC001 (trùng mã)", lambda h: h.cell(5, 1, "DC001")),
    ("DC004 bỏ trống mã học sinh", lambda h: setattr(h.cell(6, 1), "value", None)),
    ("DC005 NV1 ghi 'CLB Bơi lội' (không có trong danh sách)", lambda h: h.cell(7, 4, "CLB Bơi lội")),
    ("DC006 điểm thi NV1 ghi chữ 'chín'", lambda h: h.cell(8, 5, "chín")),
]
LOI_MEM = [
    ("DC007 không khai nguyện vọng nào (thiếu dữ liệu)",
     lambda h: [setattr(h.cell(9, c), "value", None) for c in range(4, h.max_column + 1)]),
    ("DC009 đặt huy chương Vàng (60) cho hai CLB cùng buổi", None),
]


def _hai_vang(h):
    """DC009 (hàng 11): đặt 60 vào hai ô huy chương của hai CLB cùng buổi Thứ 3 đầu tiên có ô huy chương."""
    o = [c for c in range(6, h.max_column + 1, 3) if h.cell(11, c).value not in (None, "")]
    h.cell(11, o[0], 60); h.cell(11, o[1], 60)


LOI_MEM[-1] = (LOI_MEM[-1][0], _hai_vang)


def ghi(ten, sheet, loi):
    wb = openpyxl.load_workbook(GOC)
    for _, f in loi:
        f(wb[sheet])
    ra = os.path.join(D, ten)
    wb.save(ra)
    return ra


if __name__ == "__main__":
    print(ghi("SO_NHAP_300HS_LOI_CLB.xlsx", "1. CLB", LOI_CLB))
    print(ghi("SO_NHAP_300HS_LOI_HS.xlsx", "2. Học sinh", LOI_HS))
    print(ghi("SO_NHAP_300HS_THIEU_XUNG_DOT.xlsx", "2. Học sinh", LOI_MEM))
