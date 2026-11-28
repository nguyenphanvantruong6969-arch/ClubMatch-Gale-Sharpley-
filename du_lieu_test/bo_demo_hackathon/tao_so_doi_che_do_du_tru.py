# -*- coding: utf-8 -*-
"""Sinh `SO_NHAP_DEMO_DOI_CHE_DO.xlsx`: sổ demo đổi chế độ qua lại + nhóm ưu tiên. DỮ LIỆU MÔ PHỎNG.

    python du_lieu_test/bo_demo_hackathon/tao_so_doi_che_do_du_tru.py [--ra DUONG_DAN.xlsx]

Lấy nguyên `du_lieu_test/tao_so_nhap_doi_che_do.py` (150 em, 2 buổi × 7 CLB, hợp lệ cho Chỉ xếp thứ tự /
Chia 100 điểm / Huy chương và bật/tắt chia theo loại CLB), thêm cột Lớp (6 lớp × 25 em), suất ưu tiên ở 6 CLB (hai nhóm
`chinh_sach`, `khoi_10`) và gán nhóm cho ~35% học sinh (seed cố định). Nạp khi workspace đang ở chế độ
Huy chương để mọi cột vào máy; sau đó đổi chế độ ở Cài đặt và chạy lại, không cần nạp lại.
Nhóm ưu tiên có tác dụng ở Chỉ xếp và Chia 100 (RB-DA); chế độ chia theo loại / Huy chương không dùng nó.
"""
import argparse
import datetime
import os
import random
import sys

DAY = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(DAY))
sys.path.insert(0, GOC)
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import openpyxl  # noqa: E402

import so_nhap  # noqa: E402
import tao_so_nhap_doi_che_do as dc  # noqa: E402

SEED_NHOM = 7
LOP = ["10A1", "10A2", "10A3", "11A1", "11A2", "12A1"]   # 25 em mỗi lớp
DU_TRU = {"Bóng rổ": (6, "chinh_sach"), "Cờ vua": (5, "khoi_10"), "Robot": (4, "chinh_sach"),
          "Bóng đá": (6, "khoi_10"), "Nhiếp ảnh": (5, "chinh_sach"), "Tin học": (4, "khoi_10")}


def ghi(ra):
    clubs, students = dc.dung_so()
    for c in clubs:
        if c["name"][len("CLB "):] in DU_TRU:
            c["reserve_capacity"], c["reserve_group"] = DU_TRU[c["name"][len("CLB "):]]
    rd = random.Random(SEED_NHOM)
    for s in students:
        x = rd.random()
        s["reserve_group"] = "chinh_sach" if x < 0.15 else ("khoi_10" if x < 0.35 else "")
    lop = [LOP[i % len(LOP)] for i in range(len(students))]
    rd.shuffle(lop)
    for s, l in zip(students, lop):
        s["class_id"] = l
    so_nhap.ghi_so_nhap(ra, clubs, students, luon_co_cot_w=True, che_do_fa=True, co_lop=True)
    wb = openpyxl.load_workbook(ra)
    moc = datetime.datetime(2026, 11, 28)          # dấu thời gian cố định: chạy lại ra cùng tệp
    wb.properties.created = wb.properties.modified = moc
    wb.save(ra)
    return ra


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ra", default=os.path.join(DAY, "SO_NHAP_DEMO_DOI_CHE_DO.xlsx"))
    print(ghi(ap.parse_args().ra))
