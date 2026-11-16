"""GT1-L1: giải trình kết quả cho MỘT học sinh — chỉ ĐỌC, không đổi đường chạy nào.

Hai nửa:
  * `dung_du_lieu_run(...)`: dựng lại, trong bộ nhớ, đúng lần chạy RB-DA thường (FA tắt) từ dữ liệu
    đã đọc — gọi lại `run_rbda_nhieu_buoi` với bộ số bốc thăm ĐÃ KHOÁ. Không ghi gì.
  * `giai_trinh_mot_hoc_sinh(du_lieu_run, student_id)`: hàm thuần, không CSDL; từ `du_lieu_run` ra
    cấu trúc giải trình của MỘT em (mọi buổi, mọi CLB em chọn). Câu chữ lấy từ `fa_ly_do`.

Riêng tư: kết quả chỉ chứa dữ liệu của chính em (mã, số bốc thăm của em). Điểm chuẩn là con số của CLB,
không gắn tên ai; số bốc thăm của người khác không bao giờ ra.

Dữ liệu trong test là dữ liệu MÔ PHỎNG.
"""

from __future__ import annotations

import fa_ly_do

# Mã kết cục (hằng số ở đây; câu chữ chỉ ở fa_ly_do.py)
ACCEPTED = "ACCEPTED"
HIGHER_CHOICE_ACCEPTED = "HIGHER_CHOICE_ACCEPTED"
FULL_SCORE = "FULL_SCORE"
FULL_LOTTERY = "FULL_LOTTERY"
FULL_GROUP = "FULL_GROUP"          # nhóm xếp cứng (tier_mode strict) quyết định
FULL_WHARTON = "FULL_WHARTON"      # điểm Wharton quyết định (A13, FA tắt)
RESERVED = "RESERVED"
NOT_TESTED = "NOT_TESTED"
UNASSIGNED = "UNASSIGNED"


def dung_du_lieu_run(students, clubs, tested_scores, applicants, preferences, reserve_fn,
                     tier_rank, bo_qua_du_tru, diem_wharton, stb_goc, seed, stb_buoi_da_khoa):
    """Chạy lại lần chạy RB-DA thường trong bộ nhớ, trả `(KetQuaTuan, du_lieu_theo_buoi)`.

    Gọi y hệt `api.run_pipeline` (che_do_boc_tham mặc định) nên cùng đầu vào cho cùng kết quả. KHÔNG
    ghi CSDL, KHÔNG vẽ lại số bốc thăm: `stb_goc` và `stb_buoi_da_khoa` là bộ đã khoá.
    """
    from rbda_priority_pipeline import (
        CHE_DO_BOC_THAM_MAC_DINH, cat_du_lieu_theo_buoi, nhom_theo_buoi, run_rbda_nhieu_buoi)

    ket = run_rbda_nhieu_buoi(
        students, clubs, tested_scores, applicants, preferences, stb_goc,
        is_reserve_eligible_fn=reserve_fn, che_do_boc_tham=CHE_DO_BOC_THAM_MAC_DINH, seed=seed,
        tier_rank=tier_rank, bo_qua_du_tru=bo_qua_du_tru, diem_wharton=diem_wharton,
        stb_buoi_da_khoa=stb_buoi_da_khoa)
    nhom = nhom_theo_buoi(clubs)
    theo_buoi = {}
    for buoi in ket.ds_buoi:
        clubs_b, scores_b, _, prefs_b = cat_du_lieu_theo_buoi(
            buoi, nhom[buoi], clubs, tested_scores, applicants, preferences)
        kq = ket.per_buoi[buoi]
        theo_buoi[buoi] = {
            "clubs": {cid: {"ten": c.get("ten") or c.get("name") or cid,
                            "capacity": c["capacity"],
                            "reserve_capacity": 0 if bo_qua_du_tru else c["reserve_capacity"],
                            "chon_loc": bool(scores_b.get(cid))}
                      for cid, c in clubs_b.items()},
            "prefs": prefs_b,
            "scores": scores_b,
            "stb": ket.stb_theo_buoi[buoi],
            "assign": dict(kq.assignment),
            "base_rank": kq.base_rank,
            "tier_rank": tier_rank,
            "diem_wharton": diem_wharton,
        }
    return ket, theo_buoi


# ---------------------------------------------------------------------------------------------
def _nguoi_nhan_cuoi(cid, assign, base_rank):
    """Người nhận CUỐI (hạng nền thấp nhất) của CLB, hoặc None nếu CLB chưa nhận ai."""
    giu = [s for s, c in assign.items() if c == cid]
    return (max(giu, key=lambda s: base_rank[cid].get(s, len(base_rank[cid]))) if giu else None), len(giu)


def _ma_tu_choi(sid, cid, b, cuoi):
    """(mã, sau_nguoi_nhan_cuoi) cho em `sid` bị từ chối ở CLB `cid` so với người nhận cuối `cuoi`."""
    rank = b["base_rank"][cid]
    r_em, r_cuoi = rank.get(sid), rank.get(cuoi)
    if r_em is not None and r_cuoi is not None and r_em < r_cuoi:
        return RESERVED, False                   # em xếp TRƯỚC người nhận cuối mà vẫn không vào = suất dự trữ
    tr = b.get("tier_rank")
    if tr is not None:
        cu = max(tr.values(), default=-1) + 1
        if tr.get(sid, cu) != tr.get(cuoi, cu):
            return FULL_GROUP, True
    diem = b["scores"].get(cid, {})
    if cuoi in diem and sid not in diem:
        return NOT_TESTED, True
    if cuoi in diem and sid in diem and diem[cuoi] != diem[sid]:
        return FULL_SCORE, True
    w = b.get("diem_wharton")
    if w is not None and w.get(cid, {}).get(sid, 0) != w.get(cid, {}).get(cuoi, 0):
        return FULL_WHARTON, True
    return FULL_LOTTERY, True


def _lua_chon_rbda(sid, buoi, b):
    ds = b["prefs"].get(sid, [])
    ket = b["assign"].get(sid)
    hang_xep = ds.index(ket) if ket in ds else None
    ra = []
    for i, cid in enumerate(ds):
        c = b["clubs"].get(cid)
        if c is None:
            continue
        cuoi, n = _nguoi_nhan_cuoi(cid, b["assign"], b["base_rank"])
        diem_clb = b["scores"].get(cid, {})
        x = {"hang": i + 1, "club_id": cid, "ten_clb": c["ten"], "chon_loc": c["chon_loc"],
             "diem_em": diem_clb.get(sid), "suc_chua": c["capacity"], "du_tru": c["reserve_capacity"],
             "da_nhan": n, "stb_em": b["stb"].get(sid), "duoc_xep": cid == ket,
             "diem_chuan": None, "diem_chuan_loai": None, "sau_nguoi_nhan_cuoi": None}
        if n >= c["capacity"] and cuoi is not None:
            if cuoi in diem_clb:
                x["diem_chuan"], x["diem_chuan_loai"] = diem_clb[cuoi], "diem"
            else:
                x["diem_chuan_loai"] = "boc_tham"
        else:
            x["diem_chuan_loai"] = "con_cho"
        if cid == ket:
            x["ma"] = ACCEPTED
        elif hang_xep is not None and i > hang_xep:
            x["ma"] = HIGHER_CHOICE_ACCEPTED
        else:
            if cuoi is None:      # bất khả: CLB trống mà em bị từ chối (dữ liệu hỏng) — không bịa lý do
                x["ma"] = None
            else:
                x["ma"], x["sau_nguoi_nhan_cuoi"] = _ma_tu_choi(sid, cid, b, cuoi)
        ra.append(x)
    return ra


def _them_cau(x):
    if x.get("ma"):
        x["cau"] = fa_ly_do.cau_ly_do_rbda(
            {"ma": x["ma"], "rank_in_list": x["hang"], "cut_score": x.get("diem_chuan"),
             "diem_em": x.get("diem_em")}, x["ten_clb"])
    else:
        x["cau"] = ""


def _lua_chon_fa(sid, buoi, b):
    """FA bật: dùng LẠI dòng `fa_ly_do` đã lưu (b["fa_rows"][sid]) — không tính lại."""
    ket = b["assign"].get(sid)
    dong = {r["club_id"]: r for r in b.get("fa_rows", {}).get(sid, [])}
    ds = b["prefs"].get(sid, [])
    hang_xep = ds.index(ket) if ket in ds else None
    ra, thay = [], set()
    for i, cid in enumerate(ds):
        c = b["clubs"].get(cid)
        if c is None:
            continue
        r = dong.get(cid)
        n = sum(1 for s, k in b["assign"].items() if k == cid)
        x = {"hang": i + 1, "club_id": cid, "ten_clb": c["ten"], "chon_loc": c["chon_loc"],
             "diem_em": (r or {}).get("diem_em"), "suc_chua": c["capacity"], "du_tru": c["reserve_capacity"],
             "da_nhan": n, "stb_em": b["stb"].get(sid), "duoc_xep": cid == ket,
             "diem_chuan": (r or {}).get("cut_score"), "diem_chuan_loai": None,
             "sau_nguoi_nhan_cuoi": None, "vi_tri_cho": (r or {}).get("waitlist_pos")}
        if r is not None:
            thay.add(cid)
            x["ma"] = r["reason"]            # ACCEPTED hoặc lý do đã lưu (SCORE, MEDAL, LOTTERY, ...)
            x["diem_chuan_loai"] = ("diem" if r.get("cut_score") is not None
                                    else "boc_tham" if r["reason"] == "LOTTERY" else None)
            x["cau"] = fa_ly_do.cau_ly_do(r, c["ten"])
        else:
            x["ma"] = HIGHER_CHOICE_ACCEPTED if (hang_xep is not None and i > hang_xep) else None
            x["cau"] = (fa_ly_do.cau_ly_do_rbda({"ma": x["ma"]}, c["ten"]) if x["ma"] else "")
        ra.append(x)
    for cid, r in dong.items():                # CLB dự phòng / Tự do ngoài danh sách nguyện vọng
        if cid in thay or cid in ds:
            continue
        c = b["clubs"].get(cid) or {"ten": cid, "capacity": None, "reserve_capacity": 0,
                                    "chon_loc": False}
        ra.append({"hang": None, "club_id": cid, "ten_clb": c["ten"], "chon_loc": c["chon_loc"],
                   "diem_em": None, "suc_chua": c["capacity"], "du_tru": c["reserve_capacity"],
                   "da_nhan": sum(1 for s, k in b["assign"].items() if k == cid),
                   "stb_em": b["stb"].get(sid), "duoc_xep": cid == ket, "diem_chuan": None,
                   "diem_chuan_loai": None, "sau_nguoi_nhan_cuoi": None, "vi_tri_cho": None,
                   "ma": r["reason"], "cau": fa_ly_do.cau_ly_do(r, c["ten"])})
    return ra


def giai_trinh_mot_hoc_sinh(du_lieu_run: dict, student_id: str) -> dict:
    """Giải trình của MỘT học sinh. `du_lieu_run`:

        {"fa_bat": bool, "du_lieu_da_doi": bool, "run": {...}, "ds_buoi": [buoi...],
         "buoi": {buoi: {"clubs", "prefs", "scores", "stb", "assign", "base_rank", ... "fa_rows"}}}

    Trả {"student_id", "fa_bat", "du_lieu_da_doi", "run", "buoi": [{"buoi", "ket_qua", "ten_clb",
    "ma_tom_tat", "cau_tom_tat", "cac_lua_chon": [...]}]}. Hàm thuần: không CSDL, không ghi.
    """
    fa = bool(du_lieu_run.get("fa_bat"))
    ra_buoi = []
    for buoi in du_lieu_run.get("ds_buoi", []):
        b = du_lieu_run["buoi"][buoi]
        if student_id not in b["assign"] and student_id not in b["prefs"]:
            continue
        ds = _lua_chon_fa(student_id, buoi, b) if fa else _lua_chon_rbda(student_id, buoi, b)
        if not fa:
            for x in ds:
                _them_cau(x)
        ket = b["assign"].get(student_id)
        ten = (b["clubs"].get(ket) or {}).get("ten") if ket else None
        ra_buoi.append({
            "buoi": buoi, "ket_qua": ket, "ten_clb": ten,
            "ma_tom_tat": ACCEPTED if ket else UNASSIGNED,
            "cau_tom_tat": (fa_ly_do.cau_ly_do_rbda({"ma": UNASSIGNED}, "") if not ket else ""),
            "cac_lua_chon": ds})
    return {"student_id": student_id, "fa_bat": fa,
            "du_lieu_da_doi": bool(du_lieu_run.get("du_lieu_da_doi")),
            "run": du_lieu_run.get("run") or {}, "buoi": ra_buoi}
