# -*- coding: utf-8 -*-
"""Sinh `SO_NHAP_DOI_CHE_DO_150HS.xlsx`: MỘT sổ nhập hợp lệ cùng lúc cho mọi chế độ của trang Cài đặt
(Chỉ xếp thứ tự / Chia 100 điểm / Huy chương, và bật/tắt chia theo loại CLB), để thử đổi chế độ qua
lại liên tục sau khi nạp mà không phải nạp lại.

    python du_lieu_test/tao_so_nhap_doi_che_do.py [--ra DUONG_DAN.xlsx] [--seed 20261122]

DỮ LIỆU MÔ PHỎNG: tên, nguyện vọng, điểm thi và huy chương do máy bịa theo `random.Random(seed)`.
Không phải học sinh hay khảo sát có thật.

Vì sao một sổ hợp lệ cho cả hai luật điểm (cột "Điểm quyết tâm" = cột "Huy chương", cùng `diem_w`):
  - Huy chương: mỗi buổi tối đa 60/30/10, mỗi giá trị một lần, không đặt ở CLB Tự do.
  - Chia 100: mỗi buổi, quỹ 1 (CLB có điểm thi) và quỹ 2 (CLB còn lại) đều đúng 100; ô trống = 0;
    quỹ chỉ có MỘT CLB mà trống thì phần mềm tự điền 100 (trong bộ nhớ, không ghi vào sổ).
  => 60+30+10 = 100 đặt trọn trong MỘT quỹ; quỹ kia rỗng hoặc chỉ có một CLB để trống.
Mỗi buổi 7 CLB: 1 Tự do, 3 Giới hạn (A, B, C), 3 Tuyển chọn (có điểm sàn). Mỗi em, mỗi buổi, một kiểu:
  K1 không thi:      xếp A, B, C (+ Tự do cuối); huy chương 60/30/10 trên A, B, C.
  K2 thi một CLB:    xếp A, B, C, T (+ Tự do cuối); huy chương trên A, B, C; T trống (quỹ 1 tự điền).
  K3 thi ba CLB:     xếp T1, T2, T3 (+ Tự do cuối); huy chương trên ba CLB thi; Tự do trống (tự điền).
Điểm thi chỉ ở CLB Tuyển chọn (ai xếp CLB Tuyển chọn đều có điểm).
"""
import argparse
import datetime
import os
import random
import sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GOC)

import openpyxl  # noqa: E402

import so_nhap  # noqa: E402

SEED_MAC_DINH = 20261122
N_HOC_SINH = 150
MAC_DINH_RA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DOI_CHE_DO_%dHS.xlsx" % N_HOC_SINH)
BUOI = ["thu_3", "thu_6"]
# (tên, loại, chỉ tiêu, điểm sàn)
CLB_MOI_BUOI = {
    "thu_3": [("Đọc sách", so_nhap.TU_DO, N_HOC_SINH, None),
              ("Bóng rổ", so_nhap.GIOI_HAN, 30, None),
              ("Cờ vua", so_nhap.GIOI_HAN, 25, None),
              ("Âm nhạc", so_nhap.GIOI_HAN, 25, None),
              ("Robot", so_nhap.TUYEN_CHON, 15, 5),
              ("Toán chuyên đề", so_nhap.TUYEN_CHON, 15, 6),
              ("Tranh biện", so_nhap.TUYEN_CHON, 12, 5)],
    "thu_6": [("Trồng cây", so_nhap.TU_DO, N_HOC_SINH, None),
              ("Bóng đá", so_nhap.GIOI_HAN, 30, None),
              ("Hội hoạ", so_nhap.GIOI_HAN, 25, None),
              ("Nhiếp ảnh", so_nhap.GIOI_HAN, 25, None),
              ("Tin học", so_nhap.TUYEN_CHON, 15, 5),
              ("Tiếng Anh", so_nhap.TUYEN_CHON, 15, 6),
              ("Khoa học", so_nhap.TUYEN_CHON, 12, 5)],
}
HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ"]
DEM = ["Văn", "Thị", "Minh", "Gia", "Ngọc", "Thanh", "Quốc", "Bảo"]
TEN = ["An", "Bình", "Chi", "Dũng", "Hà", "Khoa", "Linh", "Nam", "Phúc", "Quân", "Thảo", "Vy"]
GHI_CHU = [
    "",
    "DỮ LIỆU MÔ PHỎNG (du_lieu_test/tao_so_nhap_doi_che_do.py, seed cố định). Không phải học sinh thật.",
    "Sổ này hợp lệ cùng lúc cho Chỉ xếp thứ tự, Chia 100 điểm và Huy chương (60/30/10 = 100 trong một quỹ),",
    "và cho bật/tắt chia theo loại CLB: đổi chế độ ở Cài đặt rồi chạy lại, không cần nạp lại.",
]


def dung_so(seed: int = SEED_MAC_DINH):
    """(clubs, students) cho `so_nhap.ghi_so_nhap`, tất định theo `seed`."""
    rd = random.Random(seed)
    clubs, theo_buoi = [], {}
    for b in BUOI:
        theo_buoi[b] = []
        for k, (ten, loai, cho, san) in enumerate(CLB_MOI_BUOI[b], 1):
            c = {"club_id": "%s_%d" % (b.upper(), k), "name": "CLB %s" % ten, "capacity": cho,
                 "reserve_capacity": 0, "reserve_group": "", "buoi": b, "loai": loai,
                 "diem_san": san, "so_toi_thieu": None, "suc_chua_phong": None}
            clubs.append(c)
            theo_buoi[b].append(c)
    students = []
    for i in range(1, N_HOC_SINH + 1):
        nv = []
        for b in BUOI:
            tu_do = theo_buoi[b][0]
            gioi_han = [c for c in theo_buoi[b] if c["loai"] == so_nhap.GIOI_HAN]
            tuyen = [c for c in theo_buoi[b] if c["loai"] == so_nhap.TUYEN_CHON]
            kieu = rd.choices(["K1", "K2", "K3"], weights=[4, 4, 2])[0]
            if kieu == "K3":
                co_huy = rd.sample(tuyen, 3)
                chon = list(co_huy)
            else:
                co_huy = rd.sample(gioi_han, 3)
                chon = co_huy + ([rd.choice(tuyen)] if kieu == "K2" else [])
                rd.shuffle(chon)
            if rd.random() < 0.85:
                chon.append(tu_do)                                   # Tự do xếp cuối (đa số em)
            huy = dict(zip((c["club_id"] for c in co_huy), rd.sample([60, 30, 10], 3)))
            for c in chon:
                x = {"club_id": c["club_id"], "thi": False, "diem": ""}
                if c["loai"] == so_nhap.TUYEN_CHON:
                    x["thi"], x["diem"] = True, str(rd.randint(3, 10))
                if c["club_id"] in huy:
                    x["diem_w"] = huy[c["club_id"]]
                nv.append(x)
        ten = "%s %s %s" % (rd.choice(HO), rd.choice(DEM), rd.choice(TEN))
        students.append({"student_id": "DC%03d" % i, "name": ten, "reserve_group": "", "nv": nv})
    return clubs, students


def ghi(ra: str, seed: int = SEED_MAC_DINH) -> str:
    clubs, students = dung_so(seed)
    so_nhap.ghi_so_nhap(ra, clubs, students, luon_co_cot_w=True, che_do_fa=True)
    wb = openpyxl.load_workbook(ra)
    hd = wb[so_nhap.SHEET_HD]
    for dong in GHI_CHU:
        hd.cell(row=hd.max_row + 1, column=1, value=dong or None)
    moc = datetime.datetime(2026, 11, 22)          # dấu thời gian cố định: chạy lại ra cùng tệp
    wb.properties.created = wb.properties.modified = moc
    wb.save(ra)
    return ra


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ra", default=MAC_DINH_RA)
    ap.add_argument("--seed", type=int, default=SEED_MAC_DINH)
    a = ap.parse_args()
    print(ghi(a.ra, a.seed))
