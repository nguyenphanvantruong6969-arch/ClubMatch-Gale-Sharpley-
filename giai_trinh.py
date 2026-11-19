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
from fa_daa import GIA_TRI_HUY_CHUONG
from so_nhap import NHAN_BUOI

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
NO_CHOICES = "NO_CHOICES"          # em chưa đăng ký nguyện vọng nào ở buổi này


# UX1B-L7: chữ đời thường dùng chung cho màn hình và phiếu in (MỘT nơi giữ câu).
NHAN_HUY_CHUONG = dict(zip(GIA_TRI_HUY_CHUONG, ("Vàng", "Bạc", "Đồng")))
_NHAN_BUOI = {ma: nhan for nhan, ma in NHAN_BUOI}
_BUOI_MAC_DINH = "__mac_dinh__"
# Khớp khoá ưu tiên FA (`fa_daa.ly_do_ket_qua`): giữ chỗ, điểm thi (chỉ CLB có thi), huy chương cao hơn trước (Vàng 60 >
# Bạc 30 > Đồng 10 > chưa đặt 0), rồi bốc thăm.
CHU_THICH_HUY_CHUONG = ("Huy chương: khi các bạn bằng nhau ở các bước trước, bạn đặt huy chương cao hơn "
                        "(Vàng, rồi Bạc, rồi Đồng) được xét trước; chưa đặt huy chương thì xét sau; "
                        "vẫn bằng nhau thì bốc thăm.")


def _nhan_buoi(buoi):
    return "" if not buoi or buoi == _BUOI_MAC_DINH else _NHAN_BUOI.get(buoi, str(buoi))


nhan_buoi = _nhan_buoi          # tên công khai cho các nơi khác (phiếu, báo cáo tổng hợp): "thu_2" -> "Thứ 2"


def tom_tat_dong(ra_buoi: list, giong: str = fa_ly_do.GIONG_HOC_SINH) -> str:
    """Dòng tóm tắt dưới tên em: "Em có 2/3 buổi: CLB A (Thứ 4), CLB B (Thứ 6)." hay "Em chưa có CLB ở buổi nào".
    `giong` "giao_vien": cùng câu nhưng nói "Học sinh" (khung tra cứu của giáo viên / quản trị)."""
    if not ra_buoi:
        return ""
    em = "Học sinh" if giong == fa_ly_do.GIONG_GIAO_VIEN else "Em"
    co = [b for b in ra_buoi if b["ket_qua"]]
    if len(ra_buoi) == 1 and not _nhan_buoi(ra_buoi[0]["buoi"]):
        return ("%s được xếp vào %s." % (em, co[0].get("ten_clb") or co[0]["ket_qua"])) if co else \
            "%s chưa có CLB nào." % em
    if not co:
        return "%s chưa có CLB ở buổi nào." % em
    return "%s có %d/%d buổi: %s." % (em, len(co), len(ra_buoi), ", ".join(
        "%s (%s)" % (b.get("ten_clb") or b["ket_qua"], _nhan_buoi(b["buoi"]) or b["buoi"]) for b in co))


def cac_buoc_tiep(tinh_nang: dict | None, giong: str = fa_ly_do.GIONG_HOC_SINH) -> list:
    """"Em nên làm gì tiếp": chỉ nêu tính năng ĐANG BẬT của workspace, luôn kèm "hỏi giáo viên phụ trách".
    `giong` "giao_vien": cùng ý, ngôi thứ ba."""
    t = tinh_nang or {}
    gv = giong == fa_ly_do.GIONG_GIAO_VIEN
    ra = []
    if t.get("vong_2"):
        ra.append("Nhà trường có vòng 2 cho các học sinh chưa có CLB: học sinh theo dõi thông báo và đăng ký lại."
                  if gv else "Nhà trường có vòng 2 cho các em chưa có CLB: em theo dõi thông báo và đăng ký lại.")
    if t.get("moi_cho_trong"):
        ra.append("Nếu CLB còn chỗ trống, nhà trường có thể mời học sinh từ danh sách chờ."
                  if gv else "Nếu CLB còn chỗ trống, nhà trường có thể mời em từ danh sách chờ: em nhớ trả lời lời mời.")
    if t.get("khieu_nai"):
        so = t.get("so_ngay") or 3
        ra.append("Nếu học sinh thấy dữ liệu bị sai (điểm, nguyện vọng), có thể khiếu nại trong %s ngày." % so if gv else
                  "Nếu em thấy dữ liệu của em bị sai (điểm, nguyện vọng), em có thể khiếu nại trong %s ngày." % so)
    ra.append("Học sinh hỏi giáo viên phụ trách để biết thêm." if gv else "Em hỏi giáo viên phụ trách để biết thêm.")
    return ra


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
                            "chon_loc": bool(scores_b.get(cid)), "loai": c.get("loai")}
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
             "loai_clb": c.get("loai"), "diem_em": diem_clb.get(sid), "suc_chua": c["capacity"], "du_tru": c["reserve_capacity"],
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
                if x["ma"] == RESERVED:
                    # GT4-L4: chỗ dành riêng — số của người nhận cuối KHÔNG phải ngưỡng của em này, nên không đưa ra.
                    x["diem_chuan"], x["diem_chuan_loai"] = None, "giu_cho"
        ra.append(x)
    return ra


def _them_cau(x, giong=fa_ly_do.GIONG_HOC_SINH):
    if x.get("ma"):
        x["cau"] = fa_ly_do.cau_ly_do_rbda(
            {"ma": x["ma"], "rank_in_list": x["hang"], "cut_score": x.get("diem_chuan"),
             "diem_em": x.get("diem_em")}, x["ten_clb"], giong)
    else:
        x["cau"] = ""


def _cau_huy_chuong(r, cua_em, ten_clb):
    """MỘT câu thay cho câu chung của dòng lý do MEDAL: nêu huy chương CỦA EM và huy chương của người nhận cuối (con số
    của CLB, không tên ai). Rỗng nếu không có `cut_medal` (giữ câu chung)."""
    cut = r.get("cut_medal")
    if not cut:
        return ""
    own = NHAN_HUY_CHUONG.get(cua_em)
    khac = NHAN_HUY_CHUONG.get(cut, str(cut))
    if own:
        return "Em đặt huy chương %s; các bạn đặt %s ở %s được xét trước." % (own, khac, ten_clb)
    return "Em chưa đặt huy chương ở %s; các bạn đặt %s được xét trước." % (ten_clb, khac)


def _chuan_clb_fa(cid, b):
    """UX1B-R1: mức vào được của CLB có thi ở chế độ FA, MỘT quy tắc cho cột, thanh SVG và câu "Vì sao": lấy từ các dòng bị
    từ chối đã lưu của CLB (`fa_ly_do`: mọi dòng REJECTED của một CLB cùng so với MỘT người nhận cuối, người có khoá xấu
    nhất theo (giữ chỗ, điểm, huy chương, bốc thăm)). Có dòng RESERVED -> người nhận cuối giữ chỗ riêng, không có mức điểm
    ("giu_cho"); ngược lại `cut_score` ("diem"). Chưa ai bị từ chối: còn chỗ -> "con_cho", đầy vừa đủ -> không ghi.
    Chỉ là con số / mã của CLB, không tên hay điểm của người cụ thể. CLB không thi: (None, None)."""
    c = b["clubs"][cid]
    if not c["chon_loc"]:
        return None, None
    tu_choi = [r for dong in (b.get("fa_rows") or {}).values() for r in dong
               if r.get("club_id") == cid and r.get("outcome") == "REJECTED"]
    if tu_choi:
        if any(r.get("reason") == "RESERVED" for r in tu_choi):
            return None, "giu_cho"
        cat = [r["cut_score"] for r in tu_choi if r.get("cut_score") is not None]
        return (cat[0], "diem") if cat else (None, None)
    so_nhan = sum(1 for k in b["assign"].values() if k == cid)
    if c["capacity"] is None or so_nhan < c["capacity"]:
        return None, "con_cho"
    return None, None


def _lua_chon_fa(sid, buoi, b, huy=None):
    """FA bật: dùng LẠI dòng `fa_ly_do` đã lưu (b["fa_rows"][sid]) — không tính lại.
    `huy` = {club_id: 60|30|10} của CHÍNH em (UX1B-L7): thêm khoá `huy_chuong` ("Vàng"/"Bạc"/"Đồng"/None) vào mỗi dòng."""
    huy = huy or {}
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
             "loai_clb": c.get("loai"), "diem_em": (r or {}).get("diem_em"), "suc_chua": c["capacity"], "du_tru": c["reserve_capacity"],
             "da_nhan": n, "stb_em": b["stb"].get(sid), "duoc_xep": cid == ket,
             "diem_chuan": (r or {}).get("cut_score"), "diem_chuan_loai": None,
             "sau_nguoi_nhan_cuoi": None, "vi_tri_cho": (r or {}).get("waitlist_pos"),
             "huy_chuong": NHAN_HUY_CHUONG.get(huy.get(cid))}
        if r is not None:
            thay.add(cid)
            x["ma"] = r["reason"]            # ACCEPTED hoặc lý do đã lưu (SCORE, MEDAL, LOTTERY, ...)
            x["diem_chuan_loai"] = ("diem" if r.get("cut_score") is not None
                                    else "boc_tham" if r["reason"] == "LOTTERY" else None)
            x["cau"] = fa_ly_do.cau_ly_do(r, c["ten"])
            if r["reason"] == "MEDAL":
                cau_moi = _cau_huy_chuong(r, huy.get(cid, 0), c["ten"])
                if cau_moi:
                    x["cau"] = cau_moi
        else:
            x["ma"] = HIGHER_CHOICE_ACCEPTED if (hang_xep is not None and i > hang_xep) else None
            x["cau"] = (fa_ly_do.cau_ly_do_rbda({"ma": x["ma"]}, c["ten"]) if x["ma"] else "")
        chuan, loai = _chuan_clb_fa(cid, b)           # UX1B-R1: mức vào được của CLB, kể cả dòng ACCEPTED (không có cut_score)
        if loai:
            x["diem_chuan"], x["diem_chuan_loai"] = chuan, loai
        elif r is not None and r["reason"] == "MEDAL" and r.get("cut_medal"):
            x["diem_chuan"], x["diem_chuan_loai"] = NHAN_HUY_CHUONG.get(r["cut_medal"], str(r["cut_medal"])), "huy_chuong"
        ra.append(x)
    for cid, r in dong.items():                # CLB dự phòng / Tự do ngoài danh sách nguyện vọng
        if cid in thay or cid in ds:
            continue
        c = b["clubs"].get(cid) or {"ten": cid, "capacity": None, "reserve_capacity": 0,
                                    "chon_loc": False}
        ra.append({"hang": None, "club_id": cid, "ten_clb": c["ten"], "chon_loc": c["chon_loc"],
                   "loai_clb": c.get("loai"), "diem_em": None, "suc_chua": c["capacity"], "du_tru": c["reserve_capacity"],
                   "da_nhan": sum(1 for s, k in b["assign"].items() if k == cid),
                   "stb_em": b["stb"].get(sid), "duoc_xep": cid == ket, "diem_chuan": None,
                   "diem_chuan_loai": None, "sau_nguoi_nhan_cuoi": None, "vi_tri_cho": None,
                   "huy_chuong": NHAN_HUY_CHUONG.get(huy.get(cid)),
                   "ma": r["reason"], "cau": fa_ly_do.cau_ly_do(r, c["ten"])})
    return ra


def _diem_da_thi(sid, b, ds, fa):
    """UX1B-L7: điểm của MỌI CLB em đã thi trong buổi (kể cả CLB ngoài nguyện vọng), kèm mức vào được của CLB đó.
    Chỉ CLB em có điểm; mức vào được là con số của CLB (như cột "Mức vào được"), không tên hay điểm em khác."""
    theo = {x["club_id"]: x for x in ds}
    ket = b["assign"].get(sid)
    ra = []
    for cid, diem_clb in b["scores"].items():
        c = b["clubs"].get(cid)
        if sid not in diem_clb or c is None:
            continue
        x = theo.get(cid)
        if x is not None:
            chuan, loai = x["diem_chuan"], x["diem_chuan_loai"]
        elif not fa and cid in b.get("base_rank", {}):
            cuoi, n = _nguoi_nhan_cuoi(cid, b["assign"], b["base_rank"])
            if n >= c["capacity"] and cuoi is not None:
                chuan, loai = (diem_clb[cuoi], "diem") if cuoi in diem_clb else (None, "boc_tham")
            else:
                chuan, loai = None, "con_cho"
        elif fa:
            chuan, loai = _chuan_clb_fa(cid, b)
        else:
            chuan, loai = None, None
        ra.append({"club_id": cid, "ten_clb": c["ten"], "diem_em": diem_clb[sid], "diem_chuan": chuan,
                   "diem_chuan_loai": loai, "trong_nv": x is not None, "duoc_xep": cid == ket})
    thu_tu = {x["club_id"]: i for i, x in enumerate(ds)}
    ra.sort(key=lambda d: (thu_tu.get(d["club_id"], len(thu_tu)), d["ten_clb"]))
    return ra


def giai_trinh_mot_hoc_sinh(du_lieu_run: dict, student_id: str, giong: str = fa_ly_do.GIONG_HOC_SINH) -> dict:
    """Giải trình của MỘT học sinh. `du_lieu_run`:

        {"fa_bat": bool, "du_lieu_da_doi": bool, "run": {...}, "ds_buoi": [buoi...],
         "buoi": {buoi: {"clubs", "prefs", "scores", "stb", "assign", "base_rank", ... "fa_rows"}}}

    Trả {"student_id", "fa_bat", "du_lieu_da_doi", "run", "buoi": [{"buoi", "ket_qua", "ten_clb",
    "ma_tom_tat", "cau_tom_tat", "chu_thich", "cac_lua_chon": [...]}]}. Hàm thuần: không CSDL, không ghi.
    `giong`: giọng các câu RB-DA ("hoc_sinh" mặc định, hoặc "giao_vien" trung tính cho khung tra cứu; xem
    `fa_ly_do.cau_ly_do_rbda`). `chu_thich`: câu cố định khi buổi có hàng chỗ dành riêng, nếu không thì chuỗi rỗng.
    """
    fa = bool(du_lieu_run.get("fa_bat"))
    ra_buoi = []
    for buoi in du_lieu_run.get("ds_buoi", []):
        b = du_lieu_run["buoi"][buoi]
        if student_id not in b["assign"] and student_id not in b["prefs"]:
            continue
        huy = (du_lieu_run.get("huy_chuong") or {}).get(student_id) or {}   # CHỈ của chính em
        ds = _lua_chon_fa(student_id, buoi, b, huy) if fa else _lua_chon_rbda(student_id, buoi, b)
        if not fa:
            for x in ds:
                _them_cau(x, giong)
        ket = b["assign"].get(student_id)
        ma_tt = ACCEPTED if ket else (UNASSIGNED if ds else NO_CHOICES)
        ten = (b["clubs"].get(ket) or {}).get("ten") if ket else None
        ra_buoi.append({
            "buoi": buoi, "ket_qua": ket, "ten_clb": ten,
            "ma_tom_tat": ma_tt,
            "cau_tom_tat": (fa_ly_do.cau_ly_do_rbda({"ma": ma_tt}, "", giong) if not ket else ""),
            "chu_thich": (fa_ly_do.CAU_GIU_CHO if (not fa and any(x.get("ma") == RESERVED for x in ds)) else ""),
            "diem_da_thi": _diem_da_thi(student_id, b, ds, fa),
            "cac_lua_chon": ds})
    co_buoi_trong = any(not b["ket_qua"] for b in ra_buoi)
    return {"student_id": student_id, "fa_bat": fa,
            "du_lieu_da_doi": bool(du_lieu_run.get("du_lieu_da_doi")),
            "run": du_lieu_run.get("run") or {}, "buoi": ra_buoi,
            "tom_tat_dong": tom_tat_dong(ra_buoi, giong),
            "buoc_tiep": cac_buoc_tiep(du_lieu_run.get("tinh_nang"), giong) if co_buoi_trong else [],
            "chu_thich_huy_chuong": CHU_THICH_HUY_CHUONG if fa else ""}
