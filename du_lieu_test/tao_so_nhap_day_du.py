# -*- coding: utf-8 -*-
"""Sinh `SO_NHAP_MAU_DAY_DU.xlsx`: MỘT sổ nhập mẫu điền ĐỦ mọi cột phần mềm đọc được.

    python du_lieu_test/tao_so_nhap_day_du.py [--ra DUONG_DAN.xlsx] [--seed 20261121]

DỮ LIỆU MÔ PHỎNG: tên, lớp, nguyện vọng, điểm thi, huy chương, giữ chỗ do máy bịa theo
`random.Random(seed)`; cùng seed ra cùng nội dung. Không phải học sinh hay khảo sát có thật.

Cấu trúc lấy từ NGUỒN DUY NHẤT `so_nhap.ghi_so_nhap` (không tự vẽ sổ), nên sổ này nạp được bằng
`import_so_nhap` như mọi sổ khác. Đủ cột:
  1. CLB      Tên CLB · Buổi · Chỉ tiêu · Suất ưu tiên · Nhóm ưu tiên · Mã CLB · Loại · Điểm sàn ·
              Tối thiểu · Sức chứa phòng · Giờ · Địa điểm
  2. Học sinh Mã HS · Họ tên · Lớp · Nhóm ưu tiên · (NV k · Điểm k · Huy chương k) …
  Giữ chỗ    Mã CLB · Mã học sinh
  Hướng dẫn  hướng dẫn chuẩn + bảng "Từ điển cột" (cột nào dùng ở chế độ nào).

Hợp lệ cho workspace bật "Xếp theo loại CLB và huy chương" (FA-DAA, chế độ đầy đủ nhất): 120 em,
ba buổi; mỗi buổi một CLB Tự do (có Sức chứa phòng), hai CLB Giới hạn (có Tối thiểu), một CLB
Tuyển chọn (có Điểm sàn + Tối thiểu, điểm thi chỉ ở CLB này); huy chương 60/30/10 mỗi giá trị tối
đa một lần mỗi buổi, không đặt ở CLB Tự do. Cột Suất ưu tiên / Nhóm ưu tiên để TRỐNG: chúng chỉ
dùng ở chế độ RB-DA thường; chế độ FA dùng sheet Giữ chỗ thay cho chúng.
"""
import argparse
import datetime
import os
import random
import sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GOC)

import openpyxl  # noqa: E402
from openpyxl.styles import Font, PatternFill  # noqa: E402

import so_nhap  # noqa: E402

SEED_MAC_DINH = 20261121
MAC_DINH_RA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_MAU_DAY_DU.xlsx")
N_HOC_SINH = 120
LOP = ["10A1", "10A2", "10A3", "10A4", "11A1", "11A2"]
BUOI = ["thu_2", "thu_4", "thu_6"]
GIO = {"thu_2": "14:00–15:30", "thu_4": "15:00–16:30", "thu_6": "14:30–16:00"}
# (tên, loại, chỉ tiêu, điểm sàn, tối thiểu, sức chứa phòng, địa điểm)
CLB_THEO_BUOI = {
    "thu_2": [("Bóng rổ", so_nhap.TU_DO, 120, None, None, 40, "Sân bóng rổ"),
              ("Cờ vua", so_nhap.GIOI_HAN, 20, None, 8, None, "Phòng 201"),
              ("Âm nhạc", so_nhap.GIOI_HAN, 20, None, 8, None, "Phòng nhạc"),
              ("Robotics", so_nhap.TUYEN_CHON, 15, 5, 6, None, "Phòng STEM")],
    "thu_4": [("Bóng đá", so_nhap.TU_DO, 120, None, None, 40, "Sân cỏ"),
              ("Hội hoạ", so_nhap.GIOI_HAN, 20, None, 8, None, "Phòng mỹ thuật"),
              ("Nhiếp ảnh", so_nhap.GIOI_HAN, 20, None, 8, None, "Phòng 305"),
              ("Tranh biện", so_nhap.TUYEN_CHON, 15, 6, 6, None, "Thư viện")],
    "thu_6": [("Cầu lông", so_nhap.TU_DO, 120, None, None, 40, "Nhà thi đấu"),
              ("Tình nguyện", so_nhap.GIOI_HAN, 20, None, 8, None, "Phòng Đoàn"),
              ("Kịch nói", so_nhap.GIOI_HAN, 20, None, 8, None, "Hội trường"),
              ("Tin học", so_nhap.TUYEN_CHON, 15, 5, 6, None, "Phòng máy 1")],
}
HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đặng", "Bùi", "Đỗ", "Ngô"]
DEM = ["Văn", "Thị", "Minh", "Đức", "Ngọc", "Gia", "Bảo", "Thu", "Quang", "Khánh"]
TEN = ["An", "Bình", "Châu", "Dũng", "Giang", "Hà", "Khoa", "Linh", "Mai", "Nam", "Phúc", "Quỳnh",
       "Sơn", "Trang", "Uyên", "Việt", "Yến", "Long", "Hải", "Thảo"]

# Từ điển cột: (trang, cột, bắt buộc?, chế độ dùng, giá trị hợp lệ / ghi chú)
TU_DIEN = [
    ("1. CLB", "Tên CLB", "Bắt buộc", "Mọi chế độ", "Tên hiển thị; không trùng trong cùng buổi."),
    ("1. CLB", "Buổi", "Bắt buộc nếu trường có nhiều buổi", "Mọi chế độ", "Chọn trong danh sách: Thứ 2 … Chủ nhật."),
    ("1. CLB", "Chỉ tiêu", "Bắt buộc", "Mọi chế độ", "Số nguyên > 0: số chỗ của CLB."),
    ("1. CLB", "Suất ưu tiên", "Tuỳ chọn", "Chỉ RB-DA thường", "Số chỗ dành cho Nhóm ưu tiên (≤ Chỉ tiêu). Chế độ FA bỏ qua: dùng sheet Giữ chỗ."),
    ("1. CLB", "Nhóm ưu tiên", "Tuỳ chọn", "Chỉ RB-DA thường", "Tên nhóm được hưởng Suất ưu tiên (vd. chinh_sach)."),
    ("1. CLB", "Mã CLB", "Tuỳ chọn", "Mọi chế độ", "Để trống thì phần mềm tự tạo; giữ nguyên khi nạp lại để không mất dữ liệu."),
    ("1. CLB", "Loại", "Bắt buộc ở chế độ FA", "Chỉ FA", "Tự do / Giới hạn / Tuyển chọn. Mỗi buổi cần ít nhất một CLB Tự do."),
    ("1. CLB", "Điểm sàn", "Bắt buộc với CLB Tuyển chọn", "Chỉ FA", "Số nguyên 0–10. Dưới điểm sàn hoặc chưa thi thì không được xét CLB đó."),
    ("1. CLB", "Tối thiểu", "Tuỳ chọn", "Chỉ FA", "CLB Giới hạn / Tuyển chọn: số thành viên ít nhất để CLB mở."),
    ("1. CLB", "Sức chứa phòng", "Tuỳ chọn", "Chỉ FA", "CLB Tự do: đông hơn số này thì chia nhóm theo số bốc thăm."),
    ("1. CLB", "Giờ", "Tuỳ chọn", "Mọi chế độ", "Chỉ để hiển thị và xuất (vd. 14:00–15:30)."),
    ("1. CLB", "Địa điểm", "Tuỳ chọn", "Mọi chế độ", "Chỉ để hiển thị và xuất."),
    ("2. Học sinh", "Mã HS", "Bắt buộc", "Mọi chế độ", "Duy nhất cho mỗi em."),
    ("2. Học sinh", "Họ tên", "Bắt buộc", "Mọi chế độ", ""),
    ("2. Học sinh", "Lớp", "Tuỳ chọn", "Mọi chế độ", "Dùng để lọc, sắp, xuất theo lớp và in phiếu cả lớp."),
    ("2. Học sinh", "Nhóm ưu tiên", "Tuỳ chọn", "Chỉ RB-DA thường", "Trùng tên với Nhóm ưu tiên của CLB thì em được xét Suất ưu tiên."),
    ("2. Học sinh", "NV k", "Ít nhất 1", "Mọi chế độ", "Chọn tên CLB trong danh sách thả xuống; NV1 là muốn nhất. Tối đa 10 NV mỗi buổi."),
    ("2. Học sinh", "Điểm k", "Tuỳ chọn", "Mọi chế độ", "Có điểm (hoặc chữ 'thi') = em đã thi CLB đó; trống = không thi. Tối đa 5 CLB thi mỗi buổi."),
    ("2. Học sinh", "Huy chương / Điểm quyết tâm k", "Tuỳ chọn", "FA: Huy chương · RB-DA bật điểm quyết tâm: Điểm quyết tâm", "FA: chỉ 60 / 30 / 10, mỗi giá trị tối đa một lần mỗi buổi, không đặt ở CLB Tự do."),
    ("Giữ chỗ", "Mã CLB, Mã học sinh", "Tuỳ chọn", "Chỉ FA", "Mỗi dòng một chỗ giữ trước; em phải có CLB đó trong nguyện vọng."),
]


def _ten(rd):
    return "%s %s %s" % (rd.choice(HO), rd.choice(DEM), rd.choice(TEN))


def dung_so(seed: int = SEED_MAC_DINH):
    """(clubs, students, giu_cho) cho `so_nhap.ghi_so_nhap`, tất định theo `seed`."""
    rd = random.Random(seed)
    clubs, theo_buoi = [], {}
    for b in BUOI:
        theo_buoi[b] = []
        for k, (ten, loai, cho, san, toi, phong, noi) in enumerate(CLB_THEO_BUOI[b], 1):
            c = {"club_id": "%s_%d" % (b, k), "name": "CLB " + ten, "capacity": cho,
                 "reserve_capacity": 0, "reserve_group": "", "buoi": b, "loai": loai,
                 "diem_san": san, "so_toi_thieu": toi, "suc_chua_phong": phong,
                 "gio": GIO[b], "dia_diem": noi}
            clubs.append(c)
            theo_buoi[b].append(c)
    students = []
    for i in range(1, N_HOC_SINH + 1):
        nv = []
        for b in BUOI:
            tu_do, khac = theo_buoi[b][0], theo_buoi[b][1:]
            chon = rd.sample(khac, rd.choice([2, 3])) + [tu_do]      # Tự do xếp cuối (luôn có chỗ)
            huy = rd.sample([60, 30, 10], len(chon) - 1)
            for k, c in enumerate(chon):
                x = {"club_id": c["club_id"], "thi": False, "diem": ""}
                if c["loai"] == so_nhap.TUYEN_CHON:
                    x["thi"], x["diem"] = True, str(rd.randint(3, 10))
                if c["loai"] != so_nhap.TU_DO:
                    x["diem_w"] = huy[k]
                nv.append(x)
        students.append({"student_id": "HS%03d" % i, "name": _ten(rd), "class_id": LOP[(i - 1) % len(LOP)],
                         "reserve_group": "", "nv": nv})
    # Giữ chỗ: 3 em, mỗi em ở một CLB Giới hạn mà em đã xếp trong nguyện vọng.
    giu = []
    for s in students:
        if len(giu) == 3:
            break
        for x in s["nv"]:
            c = next(c for c in clubs if c["club_id"] == x["club_id"])
            if c["loai"] == so_nhap.GIOI_HAN and all(g[0] != c["club_id"] for g in giu):
                giu.append((c["club_id"], s["student_id"]))
                break
    return clubs, students, giu


def _them_tu_dien(wb):
    ws = wb[so_nhap.SHEET_HD]
    r = ws.max_row + 2
    ws.cell(row=r, column=1, value="TỪ ĐIỂN CỘT (sổ mẫu đầy đủ)").font = Font(bold=True, size=12)
    r += 1
    tieu_de = ["Trang", "Cột", "Bắt buộc?", "Dùng ở chế độ", "Giá trị hợp lệ / ghi chú"]
    for j, t in enumerate(tieu_de, 1):
        o = ws.cell(row=r, column=j, value=t)
        o.font = Font(bold=True)
        o.fill = PatternFill("solid", fgColor="E8E2D0")
    for dong in TU_DIEN:
        r += 1
        for j, v in enumerate(dong, 1):
            ws.cell(row=r, column=j, value=v)
    r += 2
    for dong in [
        "Chế độ đầy đủ nhất: bật 'Xếp theo loại CLB và huy chương' khi tạo không gian làm việc (cần bật 'Dùng điểm quyết tâm').",
        "Không gian làm việc thường (RB-DA) vẫn nạp được sổ này: các cột chỉ-FA bị bỏ qua và phần mềm báo một cảnh báo.",
        "DỮ LIỆU MÔ PHỎNG: tên, lớp, nguyện vọng, điểm, huy chương do máy bịa (du_lieu_test/tao_so_nhap_day_du.py).",
    ]:
        ws.cell(row=r, column=1, value=dong)
        r += 1
    for cot, rong in zip("ABCDE", (14, 30, 30, 34, 90)):
        ws.column_dimensions[cot].width = max(ws.column_dimensions[cot].width or 0, rong)


def ghi(ra: str = MAC_DINH_RA, seed: int = SEED_MAC_DINH) -> str:
    clubs, students, giu = dung_so(seed)
    so_nhap.ghi_so_nhap(ra, clubs, students, luon_co_cot_w=True, co_lop=True, giu_cho=giu,
                        che_do_fa=True)
    wb = openpyxl.load_workbook(ra)
    _them_tu_dien(wb)
    moc = datetime.datetime(2026, 11, 21)          # dấu thời gian cố định: chạy lại ra cùng tệp
    wb.properties.created = wb.properties.modified = moc
    wb.save(ra)
    return ra


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ra", default=MAC_DINH_RA)
    ap.add_argument("--seed", type=int, default=SEED_MAC_DINH)
    a = ap.parse_args()
    print(ghi(a.ra, a.seed))
