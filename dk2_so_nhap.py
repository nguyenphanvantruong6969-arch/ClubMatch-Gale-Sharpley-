"""DK2: dữ liệu xuất của bản mẫu cổng đăng ký (JSON `dinhDang` 1) -> Sổ nhập CLB (.xlsx).

Sổ được ghi CHỈ qua `so_nhap.ghi_so_nhap` (chế độ huy chương FA-DAA), nên phần mềm xếp đọc được như
mọi sổ khác. Không đổi hợp đồng cột: Phòng -> "Địa điểm", sức chứa phòng -> "Sức chứa phòng",
Lớp -> cột "Lớp" (khối suy từ tên lớp). Link bài thi, giáo viên, mô tả không vào sổ.
Dữ liệu của bản mẫu là MÔ PHỎNG.

Dùng: python dk2_so_nhap.py vao.json SO_NHAP_CLB.xlsx
"""
import argparse
import json
import sys

import so_nhap

DINH_DANG = 1
HUY_CHUONG = {"Vàng": 60, "Bạc": 30, "Đồng": 10}


class LoiBanMau(ValueError):
    """Dữ liệu bản mẫu sai; `loi` là danh sách câu tiếng Việt. Không ghi tệp nào."""

    def __init__(self, loi):
        self.loi = list(loi)
        super().__init__("\n".join(self.loi))


def _nguyen_duong(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v > 0


def _diem(v):
    """Điểm 0–10 (số, hoặc chuỗi "8,5") -> float; None/"" -> None; sai -> ValueError."""
    if v is None or (isinstance(v, str) and not v.strip()):
        return None
    if isinstance(v, bool):
        raise ValueError(v)
    so = v if isinstance(v, (int, float)) else so_nhap.doc_diem(v)
    if so is None or not 0 <= so <= 10:
        raise ValueError(v)
    return float(so)


def _doc_clb(ds, loi):
    clubs, buoi_cua = [], {}
    for i, c in enumerate(ds, start=1):
        if not isinstance(c, dict):
            loi.append(f"CLB thứ {i}: không phải một bản ghi.")
            continue
        ma, ten = str(c.get("ma") or "").strip(), str(c.get("ten") or "").strip()
        noi = f"CLB {ten or ma or i}"
        if not ma or not ten:
            loi.append(f"{noi}: thiếu mã hoặc tên.")
            continue
        if ma in buoi_cua:
            loi.append(f"{noi}: mã {ma} bị trùng.")
            continue
        try:
            loai = so_nhap.chuan_hoa_loai(c.get("loai"))
        except ValueError:
            loai = None
        if loai is None:
            loi.append(f"{noi}: loại phải là Tự do, Giới hạn hoặc Tuyển chọn.")
            continue
        phong, suc_chua = c.get("phong"), c.get("sucChuaPhong")
        if suc_chua is not None and not _nguyen_duong(suc_chua):
            loi.append(f"{noi}: sức chứa phòng phải là số nguyên dương.")
            continue
        chi_tieu = c.get("chiTieu")
        if loai == so_nhap.TU_DO:
            # Thuật toán bỏ qua chỉ tiêu của CLB Tự do (fa_daa: capacity = số học sinh); sổ vẫn cần một số.
            chi_tieu = chi_tieu if _nguyen_duong(chi_tieu) else (suc_chua or 1)
        elif not _nguyen_duong(chi_tieu):
            loi.append(f"{noi}: chỉ tiêu phải là số nguyên dương.")
            continue
        ra = {"club_id": ma, "name": ten, "buoi": so_nhap.ma_buoi(c.get("buoi")), "capacity": chi_tieu,
              "reserve_capacity": 0, "reserve_group": "", "loai": loai}
        if loai == so_nhap.TUYEN_CHON:
            # Cùng luật với phần mềm (`so_nhap.kiem_thuoc_tinh`): điểm sàn là số NGUYÊN 0–10.
            san = c.get("diemSan")
            if isinstance(san, float) and san.is_integer():
                san = int(san)
            if san is None or not isinstance(san, int) or so_nhap.kiem_thuoc_tinh(None, san, None, None):
                loi.append(f"{noi}: CLB Tuyển chọn cần điểm sàn là số nguyên từ 0 đến 10.")
                continue
            ra["diem_san"] = san
        if suc_chua is not None:
            ra["suc_chua_phong"] = suc_chua
        if phong:
            ra["dia_diem"] = str(phong)
        buoi_cua[ma] = ra["buoi"]
        clubs.append(ra)
    return clubs, buoi_cua


def _doc_hs(ds, clubs, buoi_cua, thu_tu_buoi, loi, bo):
    loai_cua = {c["club_id"]: c["loai"] for c in clubs}
    students, da_co = [], set()
    for i, h in enumerate(ds, start=1):
        if not isinstance(h, dict):
            loi.append(f"Học sinh thứ {i}: không phải một bản ghi.")
            continue
        ma = str(h.get("ma") or "").strip()
        noi = f"Học sinh {ma or i}"
        if not ma or ma in da_co:
            loi.append(f"{noi}: thiếu mã hoặc mã bị trùng.")
            continue
        da_co.add(ma)
        nv, dem, sai = [], {}, False
        for x in h.get("nv") or []:
            cid = str((x or {}).get("clb") or "")
            if cid not in loai_cua:
                loi.append(f"{noi}: CLB {cid or '(trống)'} không có trong danh sách CLB.")
                sai = True
                continue
            if any(v["club_id"] == cid for v in nv):
                loi.append(f"{noi}: CLB {cid} có hai lần trong nguyện vọng.")
                sai = True
                continue
            b = buoi_cua[cid]
            d = dem.setdefault(b, {"nv": 0, "thi": 0, "hc": set()})
            d["nv"] += 1
            v = {"club_id": cid, "thi": bool(x.get("thi")), "diem": ""}
            if v["thi"]:
                d["thi"] += 1
                try:
                    diem = _diem(x.get("diem"))
                except ValueError:
                    loi.append(f"{noi}: điểm {x.get('diem')!r} ở CLB {cid} phải từ 0 đến 10.")
                    sai = True
                    continue
                v["diem"] = "" if diem is None else diem
            hc = x.get("huyChuong")
            if hc:
                if hc not in HUY_CHUONG:
                    loi.append(f"{noi}: huy chương {hc!r} không hợp lệ (Vàng, Bạc, Đồng).")
                    sai = True
                elif loai_cua[cid] == so_nhap.TU_DO:
                    loi.append(f"{noi}: CLB Tự do {cid} không nhận huy chương.")
                    sai = True
                elif hc in d["hc"]:
                    loi.append(f"{noi}: huy chương {hc} dùng hai lần trong một buổi.")
                    sai = True
                else:
                    d["hc"].add(hc)
                    v["diem_w"] = HUY_CHUONG[hc]
            if loai_cua[cid] == so_nhap.TUYEN_CHON and v["diem"] == "":
                # Bản mẫu: không thi / không điểm thì không được xét CLB Tuyển chọn đó (D35). Bỏ NV này cho cùng
                # kết quả (DA từ chối chắc chắn, không ảnh hưởng ai) và tránh fa_clb_tuyen_chon_chua_co_diem.
                bo.append((ma, cid))
                continue
            nv.append(v)
        for d in dem.values():
            if d["nv"] > so_nhap.TRAN_NV_MOI_BUOI or d["thi"] > so_nhap.TRAN_THI_MOI_BUOI:
                loi.append(f"{noi}: quá {so_nhap.TRAN_NV_MOI_BUOI} nguyện vọng hoặc "
                           f"{so_nhap.TRAN_THI_MOI_BUOI} bài thi trong một buổi.")
                sai = True
        if sai:
            continue
        # Một dãy NV1…NVk: buổi theo thứ tự của bản mẫu, trong buổi giữ thứ tự em xếp (sắp ổn định).
        nv.sort(key=lambda v: thu_tu_buoi.get(buoi_cua[v["club_id"]], len(thu_tu_buoi)))
        students.append({"student_id": ma, "name": str(h.get("hoTen") or ""), "reserve_group": "",
                         "class_id": str(h.get("lop") or ""), "nv": nv})
    return students


def tu_ban_mau(du_lieu, bo=None):
    """JSON của bản mẫu -> (clubs, students) đúng dạng `so_nhap.ghi_so_nhap`. Sai -> LoiBanMau.

    `bo` (list, tuỳ chọn) nhận các cặp (mã HS, mã CLB) NV Tuyển chọn bị bỏ vì không thi / không điểm."""
    if not isinstance(du_lieu, dict) or du_lieu.get("dinhDang") != DINH_DANG:
        raise LoiBanMau([f"Không phải dữ liệu xuất của bản mẫu (cần dinhDang = {DINH_DANG})."])
    if not isinstance(du_lieu.get("clb"), list) or not du_lieu["clb"]:
        raise LoiBanMau(["Không có CLB nào."])
    loi = []
    clubs, buoi_cua = _doc_clb(du_lieu["clb"], loi)
    thu_tu_buoi = {}
    for b in [so_nhap.ma_buoi(x) for x in du_lieu.get("buoi") or []] + [c["buoi"] for c in clubs]:
        thu_tu_buoi.setdefault(b, len(thu_tu_buoi))
    students = _doc_hs(du_lieu.get("hocSinh") or [], clubs, buoi_cua, thu_tu_buoi, loi, [] if bo is None else bo)
    if loi:
        raise LoiBanMau(loi)
    return clubs, students


def ghi_tu_ban_mau(du_lieu, duong_dan) -> dict:
    """Ghi Sổ nhập (.xlsx) từ JSON bản mẫu. Lỗi -> LoiBanMau, không ghi tệp. Trả số CLB, học sinh."""
    bo = []
    clubs, students = tu_ban_mau(du_lieu, bo)
    so_nhap.ghi_so_nhap(duong_dan, clubs, students, co_nhom=False, co_lop=True,
                        che_do_fa=True, luon_co_cot_w=True)
    return {"so_clb": len(clubs), "so_hs": len(students), "so_nv_bo": len(bo)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Đổi dữ liệu xuất của bản mẫu cổng đăng ký thành Sổ nhập CLB.")
    p.add_argument("vao", help="tệp .json chép từ nút 'Chép dữ liệu xuất'")
    p.add_argument("ra", help="tệp .xlsx sẽ ghi, ví dụ SO_NHAP_CLB.xlsx")
    a = p.parse_args(argv)
    try:
        with open(a.vao, encoding="utf-8-sig") as f:
            du_lieu = json.load(f)
        ket_qua = ghi_tu_ban_mau(du_lieu, a.ra)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Không đọc được {a.vao}: {e}", file=sys.stderr)
        return 1
    except LoiBanMau as e:
        print("Chưa ghi sổ. Sửa các lỗi sau:", file=sys.stderr)
        for dong in e.loi:
            print(" - " + dong, file=sys.stderr)
        return 1
    print(f"Đã ghi {a.ra}: {ket_qua['so_clb']} CLB, {ket_qua['so_hs']} học sinh.")
    if ket_qua["so_nv_bo"]:
        print(f"Bỏ {ket_qua['so_nv_bo']} nguyện vọng Tuyển chọn không thi hoặc không có điểm (không được xét).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
