"""GT2 — tiêu chí xếp bằng lời thường, và danh sách giá trị cho phép (module THUẦN, không đụng CSDL).

Chỉ MÔ TẢ luật xếp đã có (`LUAT_XEP_MAC_DINH`: priority, tier_mode, score_scope, tiers, wharton,
fa_daa) theo đúng luật HIỆU LỰC (`luat_xep_hieu_luc`). Không thêm tiêu chí nào, không đọc thứ hạng
nguyện vọng, kết quả kỳ trước hay hoàn cảnh cá nhân (bất biến 2): đây là báo cáo, không phải đầu
vào của `compute_club_priority`.

    mo_ta_tieu_chi(rules, lang)  -> danh sách dòng {nhom, thu_tu, ma, chu} (+ dòng "khong_dung")
    cac_lua_chon_hop_le()        -> giá trị được chọn cho từng khoá (nguồn duy nhất cho giao diện)
    KHOA_NGOAI_LUAT_XEP          -> các khoá luật của workspace KHÔNG phải luật xếp
"""

from __future__ import annotations

import cau_hinh_ws
from rbda_priority_pipeline import (
    luat_xep_cua,
    luat_xep_hieu_luc,
    nhom_xep_cung,
)

# Khoá luật của workspace mà thuật toán KHÔNG đọc để xếp (trần nhập liệu, cờ FA sau xếp).
KHOA_NGOAI_LUAT_XEP = frozenset({
    "max_choices", "max_tests", "fa_diem_danh", "fa_khieu_nai", "fa_khieu_nai_so_ngay",
    "fa_vong_2", "fa_phan_hoi", "fa_duong", "fa_vong_doi_cho",
})

GHI_CHU = {
    "vi": "Phần mềm không dùng thứ hạng nguyện vọng, kết quả kỳ trước hay hoàn cảnh cá nhân "
          "để xếp.",
    "en": "The software does not use preference rank, previous results or personal "
          "circumstances to allocate.",
}

_NHAN_LUA_CHON = {
    "priority": {
        "score": {"vi": "Chỉ theo điểm bài thi", "en": "Exam score only"},
        "score+tier": {"vi": "Điểm bài thi và nhóm ưu tiên", "en": "Exam score and priority group"},
        "tier": {"vi": "Chỉ theo nhóm ưu tiên", "en": "Priority group only"},
    },
    "tier_mode": {
        "reserve": {"vi": "Giữ suất riêng cho nhóm", "en": "Reserve seats for the group"},
        "strict": {"vi": "Nhóm đứng trước điểm", "en": "Group ranks before score"},
    },
    "score_scope": {
        "per_slot": {"vi": "Điểm theo từng CLB", "en": "Score per club"},
        "per_person": {"vi": "Một điểm cho cả người", "en": "One score per person"},
    },
}

_TIEU_DE_KHOA = {
    "priority": {"vi": "Xếp theo", "en": "Rank by"},
    "tier_mode": {"vi": "Cách dùng nhóm ưu tiên", "en": "How priority groups are used"},
    "score_scope": {"vi": "Phạm vi điểm", "en": "Score scope"},
    "tiers": {"vi": "Danh sách nhóm ưu tiên (nhóm đầu được ưu tiên nhất)",
              "en": "Priority groups (first group has the highest priority)"},
    "wharton": {"vi": "Xét điểm quyết tâm", "en": "Use commitment points"},
    "fa_daa": {"vi": "Chế độ huy chương (FA)", "en": "Medal mode (FA)"},
    "chia_loai": {"vi": "Chia CLB theo loại", "en": "Split clubs by type"},
}

_TIEU_DE_TANG = {
    "tang_1": {"vi": "Học sinh đã có điểm thi của CLB", "en": "Students with an exam score for the club"},
    "tang_2": {"vi": "Học sinh chưa có điểm thi của CLB", "en": "Students without an exam score for the club"},
    "tang_2_tat_ca": {"vi": "Mọi học sinh", "en": "All students"},
}

# Một dòng tiêu chí: mã -> chữ (hai ngôn ngữ). `{ds}` là danh sách nhóm.
_CHU = {
    "diem_clb": {"vi": "Điểm bài thi của CLB (cao trước)", "en": "Exam score for the club (higher first)"},
    "diem_ca_nhan": {"vi": "Điểm của cả người (cao trước)", "en": "Personal score (higher first)"},
    "nhom_cung": {
        "vi": "Nhóm ưu tiên ({ds}): nhóm đứng trước được xếp trước mọi nhóm sau, bất kể điểm",
        "en": "Priority group ({ds}): an earlier group ranks before all later groups, whatever the score"},
    "du_tru": {"vi": "Nhóm ưu tiên – giữ suất riêng", "en": "Priority group - reserved seats"},
    "quyet_tam": {"vi": "Điểm quyết tâm (cao trước)", "en": "Commitment points (higher first)"},
    "boc_tham": {"vi": "Số bốc thăm (nhỏ trước)", "en": "Lottery number (lower first)"},
}

_KHONG_DUNG = {
    "tiers": {
        "vi": "Danh sách nhóm chưa được dùng: nhóm đang là suất giữ riêng nên không xếp trước điểm.",
        "en": "The group list is not used: groups are reserved seats, not ranked before score."},
    "tier_mode": {
        "vi": "Cách dùng nhóm không có tác dụng: khi chỉ xét nhóm, nhóm luôn đứng trước.",
        "en": "Not used: when ranking by group only, the group always comes first."},
    "score_scope": {
        "vi": "Phạm vi điểm không có tác dụng vì không xét điểm bài thi.",
        "en": "Score scope is not used because exam scores are not considered."},
    "priority": {
        "vi": "Đã chọn điểm và nhóm nhưng nhóm đang là suất giữ riêng: kết quả giống chỉ xét điểm.",
        "en": "Score and group is selected but groups are reserved seats: same as exam score only."},
    "wharton": {
        "vi": "Điểm quyết tâm chưa được dùng: chỉ dùng được khi xét điểm bài thi theo từng CLB.",
        "en": "Commitment points are not used: they need exam scores per club."},
    "fa_daa": {
        "vi": "Chế độ huy chương chưa được dùng: cần bật điểm quyết tâm.",
        "en": "Medal mode is not used: commitment points must be on."},
}


def _lang(lang: str) -> str:
    return "en" if lang == "en" else "vi"


def _ten_nhom(tiers) -> str:
    ten = [str(t) for t in (tiers or []) if str(t).strip()]
    return ", ".join(ten)


def _chu(ma: str, lang: str, tiers=None) -> str:
    mau = _CHU[ma][lang]
    if ma == "nhom_cung":
        ds = _ten_nhom(tiers)
        if not ds:
            ds = "chưa khai báo nhóm nào" if lang == "vi" else "no group declared"
        return mau.format(ds=ds)
    return mau


def cac_lua_chon_hop_le() -> dict:
    """Giá trị cho phép của MỖI khoá luật xếp. Khoá = đúng `LUAT_XEP_MAC_DINH` (test canh)."""
    return {
        "priority": {"kieu": "chon", "gia_tri": list(cau_hinh_ws.UU_TIEN),
                     "nhan": _NHAN_LUA_CHON["priority"], "tieu_de": _TIEU_DE_KHOA["priority"]},
        "tier_mode": {"kieu": "chon", "gia_tri": list(cau_hinh_ws.CHE_DO_NHOM),
                      "nhan": _NHAN_LUA_CHON["tier_mode"], "tieu_de": _TIEU_DE_KHOA["tier_mode"]},
        "score_scope": {"kieu": "chon", "gia_tri": list(cau_hinh_ws.PHAM_VI_DIEM),
                        "nhan": _NHAN_LUA_CHON["score_scope"], "tieu_de": _TIEU_DE_KHOA["score_scope"]},
        "tiers": {"kieu": "danh_sach", "gia_tri": [], "nhan": {},
                  "tieu_de": _TIEU_DE_KHOA["tiers"]},
        "wharton": {"kieu": "bool", "gia_tri": [True, False], "nhan": {},
                    "tieu_de": _TIEU_DE_KHOA["wharton"]},
        "fa_daa": {"kieu": "bool", "gia_tri": [True, False], "nhan": {},
                   "tieu_de": _TIEU_DE_KHOA["fa_daa"]},
        "chia_loai": {"kieu": "bool", "gia_tri": [True, False], "nhan": {},
                      "tieu_de": _TIEU_DE_KHOA["chia_loai"]},
    }


def _wharton_dung(luat_tho: dict) -> bool:
    """Giống `dung_wharton` nhưng không ném: tổ hợp sai = không dùng (đã báo ở "khong_dung")."""
    return bool(luat_tho["wharton"] is True
                and luat_tho["priority"] in ("score", "score+tier")
                and luat_tho["score_scope"] == "per_slot")


def tieu_de_tang(rules) -> dict:
    """Tiêu đề hai tầng (song ngữ). Chỉ xét nhóm thì chỉ còn một tầng "Mọi học sinh"."""
    co_diem = luat_xep_hieu_luc(rules)["priority"] != "tier"
    return {"tang_1": _TIEU_DE_TANG["tang_1"],
            "tang_2": _TIEU_DE_TANG["tang_2" if co_diem else "tang_2_tat_ca"]}


def mo_ta_tieu_chi(rules, lang: str = "vi") -> list:
    """Thứ tự tiêu chí HIỆU LỰC của luật `rules`, bằng lời thường.

    Trả danh sách dòng:
      {"nhom": "tang_1" | "tang_2", "thu_tu": 1.., "ma": <mã tiêu chí>, "chu": <câu>}
      {"nhom": "khong_dung", "khoa": <khoá luật>, "chu": <vì sao vô tác dụng>}
    Tầng 1 (đã có điểm thi của CLB) luôn đứng trước tầng 2; không có điểm bài thi (chỉ xét nhóm)
    thì tầng 1 rỗng. Không sửa `rules`; thiếu khoá thì lấy mặc định như `luat_xep_cua`.
    """
    lang = _lang(lang)
    tho = luat_xep_cua(rules)
    luat = luat_xep_hieu_luc(rules)
    cung = nhom_xep_cung(luat)
    co_diem = luat["priority"] != "tier"
    quyet_tam = _wharton_dung(tho)
    ma_diem = "diem_ca_nhan" if luat["score_scope"] == "per_person" else "diem_clb"

    t1: list[str] = []
    if co_diem:
        if cung:
            t1.append("nhom_cung")
        t1.append(ma_diem)
        if not cung:
            t1.append("du_tru")
        if quyet_tam:
            t1.append("quyet_tam")
        t1.append("boc_tham")
    t2: list[str] = []
    if cung:
        t2.append("nhom_cung")
    else:
        t2.append("du_tru")
    if quyet_tam and co_diem:
        t2.append("quyet_tam")
    t2.append("boc_tham")

    ra = []
    for nhom, danh_sach in (("tang_1", t1), ("tang_2", t2)):
        for i, ma in enumerate(danh_sach, 1):
            ra.append({"nhom": nhom, "thu_tu": i, "ma": ma,
                       "chu": _chu(ma, lang, luat["tiers"] if cung else tho["tiers"])})

    # Khoá có giá trị nhưng VÔ TÁC DỤNG (cùng cách `luat_xep_hieu_luc` bỏ chúng đi).
    ko = []
    if tho["tiers"] and not cung:
        ko.append("tiers")
    if tho["priority"] == "tier":
        ko += ["tier_mode", "score_scope"]
    if tho["priority"] == "score+tier" and not cung:
        ko.append("priority")
    if tho["wharton"] is True and not quyet_tam:
        ko.append("wharton")
    if tho["fa_daa"] is True and not quyet_tam:
        ko.append("fa_daa")
    for khoa in ko:
        ra.append({"nhom": "khong_dung", "khoa": khoa, "chu": _KHONG_DUNG[khoa][lang]})
    return ra


# ----------------------------------------------------------------------------------------------
# GT2-L3 — so sánh hai lần chạy (thuần: không đọc CSDL, không bốc thăm, không ghi gì)
# ----------------------------------------------------------------------------------------------
def _pct(tu: int, mau: int):
    return round(100.0 * tu / mau, 1) if mau else None


def _thong_ke(rows) -> dict:
    """Số liệu của một tập dòng (student_id, buoi, club_id, rank). Phần trăm tính trên MỌI suất."""
    n = len(rows)
    da_xep = [r for r in rows if r[2] is not None]
    hang = [r[3] for r in da_xep if isinstance(r[3], int) and not isinstance(r[3], bool)]
    return {
        "n": n, "da_xep": len(da_xep), "chua_xep": n - len(da_xep),
        "pct_da_xep": _pct(len(da_xep), n),
        "pct_nv1": _pct(sum(1 for h in hang if h == 1), n),
        "pct_top3": _pct(sum(1 for h in hang if h <= 3), n),
        "hang_tb": round(sum(hang) / len(hang), 2) if hang else None,
    }


def _theo_khoa(rows, khoa_fn, thu_tu=None) -> list:
    """[{khoa, a:{...}, b:{...}}] — gom theo khoá (nhóm ưu tiên, lớp). `rows` = (a_rows, b_rows)."""
    ra, rb = rows
    ks = {khoa_fn(r) for r in ra} | {khoa_fn(r) for r in rb}
    ks = sorted(ks, key=(lambda k: (thu_tu.index(k) if thu_tu and k in thu_tu else len(thu_tu or []), k)))
    return [{"khoa": k,
             "a": _thong_ke([r for r in ra if khoa_fn(r) == k]),
             "b": _thong_ke([r for r in rb if khoa_fn(r) == k])} for k in ks]


def _diem_chuan(rows, diem) -> dict:
    """{club_id: điểm thi THẤP NHẤT trong số em được nhận có điểm thi ở CLB đó} (None nếu không có)."""
    ra = {}
    for sid, _b, cid, _h in rows:
        if cid is None:
            continue
        d = (diem.get(cid) or {}).get(sid)
        if d is not None:
            ra[cid] = d if cid not in ra else min(ra[cid], d)
    return ra


def so_sanh_lan_chay(a: dict, b: dict, ctx: dict) -> dict:
    """So sánh hai lần chạy. Thuần hàm.

    `a`, `b`: {"nhan": "chinh_thuc" | "thu", "run_id", "luat" (luật thô), "rows": [(student_id, buoi,
    club_id | None, rank | None)]}. `ctx`: {"students": {sid: {"ten", "lop", "nhom"}}, "clubs": {cid:
    {"ten", "capacity"}}, "diem": {cid: {sid: điểm thi}}, "tiers": [tên nhóm]}.
    Chỉ so các BUỔI mà CẢ HAI lần cùng có dòng (chạy thử một buổi không so với buổi khác).
    Không đọc thứ hạng nguyện vọng ngoài `rank` đã có trong kết quả; chỉ để BÁO CÁO."""
    buoi_a = {r[1] for r in a["rows"]}
    buoi_b = {r[1] for r in b["rows"]}
    chung = sorted(buoi_a & buoi_b)
    ra = [r for r in a["rows"] if r[1] in chung]
    rb = [r for r in b["rows"] if r[1] in chung]
    hs = ctx.get("students") or {}
    clb = ctx.get("clubs") or {}
    diem = ctx.get("diem") or {}
    tiers = [str(t) for t in (ctx.get("tiers") or [])]

    def nhom(r):
        return (hs.get(r[0]) or {}).get("nhom") or ""

    def lop(r):
        return (hs.get(r[0]) or {}).get("lop") or ""

    cho_a = {}
    cho_b = {}
    for r in ra:
        if r[2] is not None:
            cho_a[r[2]] = cho_a.get(r[2], 0) + 1
    for r in rb:
        if r[2] is not None:
            cho_b[r[2]] = cho_b.get(r[2], 0) + 1
    chuan_a, chuan_b = _diem_chuan(ra, diem), _diem_chuan(rb, diem)
    ds_clb = [{"club_id": c, "ten": (clb.get(c) or {}).get("ten") or c,
               "suc_chua": (clb.get(c) or {}).get("capacity"),
               "a": {"da_nhan": cho_a.get(c, 0), "diem_chuan": chuan_a.get(c)},
               "b": {"da_nhan": cho_b.get(c, 0), "diem_chuan": chuan_b.get(c)}}
              for c in sorted(set(clb) | set(cho_a) | set(cho_b))]

    xa = {(r[0], r[1]): r[2] for r in ra}
    xb = {(r[0], r[1]): r[2] for r in rb}

    def ten_clb(c):
        return "" if c is None else ((clb.get(c) or {}).get("ten") or c)

    doi = []
    for k in sorted(set(xa) | set(xb)):
        if xa.get(k) != xb.get(k):
            s = hs.get(k[0]) or {}
            doi.append({"student_id": k[0], "ten": s.get("ten") or "", "lop": s.get("lop") or "",
                        "buoi": k[1], "tu": xa.get(k), "den": xb.get(k),
                        "tu_ten": ten_clb(xa.get(k)), "den_ten": ten_clb(xb.get(k))})
    def the_lan(x):
        return {"nhan": x["nhan"], "run_id": x["run_id"], "run_at": x.get("run_at"), "luat": luat_xep_cua(x["luat"]),
                "mo_ta": mo_ta_tieu_chi(x["luat"], "vi"), "mo_ta_en": mo_ta_tieu_chi(x["luat"], "en"),
                "tang": tieu_de_tang(x["luat"])}

    kq = {
        "a": the_lan(a), "b": the_lan(b),
        "buoi_chung": chung,
        "tong": {"a": _thong_ke(ra), "b": _thong_ke(rb)},
        "clb": ds_clb,
        "nhom": _theo_khoa((ra, rb), nhom, tiers),
        "lop": _theo_khoa((ra, rb), lop),
        "doi": doi,
        "so_doi": len(doi),
    }
    kq["tom_tat"] = {"vi": tom_tat_so_sanh(kq, "vi"), "en": tom_tat_so_sanh(kq, "en")}
    return kq


def _nhan_lan(x: dict) -> str:
    return ("Chạy thử số %s" if x["nhan"] == "thu" else "Chính thức số %s") % x["run_id"]


def _so(v, hau="") -> str:
    return "—" if v is None else ("%s%s" % (str(v).replace(".", ","), hau))


def _so_gon(v, lang: str = "vi") -> str:
    """Số cho câu tóm tắt: bỏ ".0" thừa (60.0 -> 60), dấu thập phân theo ngôn ngữ."""
    xau = ("%s" % v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)
    return xau.replace(".", ",") if _lang(lang) == "vi" else xau


def tom_tat_so_sanh(kq: dict, lang: str = "vi") -> str:
    """MỘT câu, chỉ có số (không kết luận, không "tốt hơn"). Ví dụ: "49 học sinh đổi CLB; được nguyện vọng 1: 53,3% → 60%."
    Số học sinh tính theo từng em (một em đổi ở hai buổi vẫn là một em)."""
    lang = _lang(lang)
    if not kq["so_doi"]:
        return ("Hai lần cho cùng kết quả: không suất nào đổi chỗ." if lang == "vi"
                else "The two runs give the same result: no place changed.")
    n = len({d["student_id"] for d in kq["doi"]})
    ta, tb = kq["tong"]["a"]["pct_nv1"], kq["tong"]["b"]["pct_nv1"]
    dau = "%d học sinh đổi CLB" % n if lang == "vi" else "%d student%s changed club" % (n, "" if n == 1 else "s")
    if ta is None or tb is None:
        return dau + "."
    return "%s; %s: %s%% → %s%%." % (
        dau, "được nguyện vọng 1" if lang == "vi" else "got first choice", _so_gon(ta, lang), _so_gon(tb, lang))


def chenh(a, b, lang: str = "vi") -> str:
    """Chênh lệch B − A bằng CHỮ ("+3", "−2"; dấu trừ U+2212) để không chỉ dựa vào màu; rỗng nếu bằng nhau hoặc thiếu số."""
    if isinstance(a, bool) or isinstance(b, bool) or not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return ""
    d = round(b - a, 2)
    if d == 0:
        return ""
    gon = _so_gon(abs(d), lang)
    return ("+" if d > 0 else "−") + gon


def _nhan_buoi_ss(buoi, lang: str = "vi") -> str:
    """Nhãn buổi cho trang so sánh; không bao giờ trả tên nội bộ `__mac_dinh__`."""
    if not buoi or buoi == "__mac_dinh__":
        return "Mặc định" if _lang(lang) == "vi" else "Default"
    from so_nhap import NHAN_BUOI
    return dict((m, nhan) for nhan, m in NHAN_BUOI).get(buoi, str(buoi))


_CSS_SO_SANH = (
    "body{font-family:system-ui,sans-serif;margin:24px;color:#1b1b1b;background:#fff;line-height:1.5}"
    "h1{font-size:22px;margin:0 0 8px}h2{font-size:18px;margin:24px 0 8px}h3{font-size:15px;margin:12px 0 4px}"
    ".tom-tat{font-size:17px;font-weight:600;margin:8px 0 16px}"
    ".luoi-lan{display:flex;flex-wrap:wrap;gap:16px;margin:8px 0}"
    ".gt2-the-lan{flex:1 1 320px;border:1px solid #bbb;border-radius:8px;padding:12px 16px;background:#fafafa}"
    ".gt2-the-lan h2{margin:0 0 2px;font-size:17px}.gt2-the-lan .ngay{color:#4a5560;font-size:14px;margin:0 0 6px}"
    ".gt2-the-lan ol{margin:0 0 8px;padding-left:22px}.gt2-the-lan li{margin:2px 0}"
    "table{border-collapse:collapse;margin:8px 0 20px;min-width:60%}"
    "th,td{border:1px solid #bbb;padding:6px 10px;text-align:left}"
    "th{background:#eef;position:sticky;top:0}"
    "td.so,th.so{text-align:right;font-variant-numeric:tabular-nums}"
    ".len{color:#0b6b3a;font-weight:600;margin-left:6px}.xuong{color:#9a3a30;font-weight:600;margin-left:6px}"
    "summary{cursor:pointer;font-weight:600;margin:8px 0}")


def _the_lan_html(x: dict) -> str:
    from html import escape as e
    ngay = str(x.get("run_at") or "").replace("T", " ")[:16]
    mo = [m for m in x["mo_ta"] if m["nhom"] != "khong_dung"]
    phan = []
    for tang in ("tang_1", "tang_2"):
        dong = [m for m in mo if m["nhom"] == tang]
        if dong:
            phan.append("<h3>%s</h3><ol>%s</ol>" % (
                e(x["tang"][tang]["vi"]), "".join("<li>%s</li>" % e(m["chu"]) for m in dong)))
    return '<section class="gt2-the-lan"><h2>%s</h2>%s%s</section>' % (
        e(_nhan_lan(x)), ('<p class="ngay">%s</p>' % e(ngay)) if ngay else "", "".join(phan))


def dung_html_so_sanh(kq: dict) -> str:
    """Trang HTML một tệp (chữ + CSS nội tuyến, không nạp gì từ ngoài). Mọi chữ lấy từ dữ liệu đều qua `escape`.

    Cấu trúc (GT4-L7): câu tóm tắt chỉ có số; hai thẻ lần chạy, tiêu chí hai tầng tách riêng; các bảng có tiêu đề cố
    định, số căn phải, chênh lệch có chữ (+/−); danh sách học sinh đổi chỗ gập mặc định; cột Buổi chỉ khi có nhiều buổi."""
    from html import escape as e

    def bang(tieu, dau, dong, so_tu=1):
        """`so_tu`: cột từ chỉ số này trở đi là số (căn phải)."""
        th = "".join('<th%s>%s</th>' % (' class="so"' if i >= so_tu else "", e(c)) for i, c in enumerate(dau))
        tr = "".join("<tr>%s</tr>" % "".join(
            "<td%s>%s</td>" % (' class="so"' if i >= so_tu else "", c if isinstance(c, _Tho) else e(str(c)))
            for i, c in enumerate(d)) for d in dong)
        return "<h2>%s</h2><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (e(tieu), th, tr)

    def ct(a, b, hau=""):
        """Ô giá trị của lần B kèm chênh lệch bằng chữ."""
        c = chenh(a, b)
        lop = "len" if c.startswith("+") else "xuong"
        return _Tho("%s%s" % (e(_so(b, hau)), (' <span class="%s">%s</span>' % (lop, e(c + hau)) if c else "")))

    a, b = kq["a"], kq["b"]
    la, lb = _nhan_lan(a), _nhan_lan(b)
    ta, tb = kq["tong"]["a"], kq["tong"]["b"]
    tong = [("Số suất xét", ta["n"], ct(ta["n"], tb["n"])), ("Đã có chỗ", ta["da_xep"], ct(ta["da_xep"], tb["da_xep"])),
            ("Chưa có chỗ", ta["chua_xep"], ct(ta["chua_xep"], tb["chua_xep"])),
            ("Tỉ lệ đã có chỗ", _so(ta["pct_da_xep"], "%"), ct(ta["pct_da_xep"], tb["pct_da_xep"], "%")),
            ("Tỉ lệ được nguyện vọng 1", _so(ta["pct_nv1"], "%"), ct(ta["pct_nv1"], tb["pct_nv1"], "%")),
            ("Tỉ lệ trong 3 nguyện vọng đầu", _so(ta["pct_top3"], "%"), ct(ta["pct_top3"], tb["pct_top3"], "%")),
            ("Thứ hạng nguyện vọng trung bình", _so(ta["hang_tb"]), ct(ta["hang_tb"], tb["hang_tb"]))]

    def nhom_dong(ds):
        return [(x["khoa"] or "(không có)", x["a"]["n"], _so(x["a"]["pct_da_xep"], "%"),
                 ct(x["a"]["pct_da_xep"], x["b"]["pct_da_xep"], "%"), _so(x["a"]["pct_nv1"], "%"),
                 ct(x["a"]["pct_nv1"], x["b"]["pct_nv1"], "%")) for x in ds]

    dau_nhom = ["Nhóm", "Số suất", "Đã có chỗ — " + la, "Đã có chỗ — " + lb, "NV1 — " + la, "NV1 — " + lb]
    nhieu_buoi = len(kq.get("buoi_chung") or []) > 1
    dau_doi = ["Mã", "Họ tên", "Lớp"] + (["Buổi"] if nhieu_buoi else []) + [la, lb]
    dong_doi = [(d["student_id"], d["ten"], d["lop"]) + ((_nhan_buoi_ss(d["buoi"]),) if nhieu_buoi else ())
                + (d["tu_ten"] or "chưa có chỗ", d["den_ten"] or "chưa có chỗ") for d in kq["doi"]]
    ds_doi = ("<h2>Học sinh đổi câu lạc bộ (%d)</h2><details><summary>Hiện danh sách (%d)</summary>"
              "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></details>" % (
                  kq["so_doi"], kq["so_doi"], "".join("<th>%s</th>" % e(c) for c in dau_doi),
                  "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % e(str(c)) for c in d) for d in dong_doi)))
    return (
        "<!doctype html><html lang=\"vi\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>So sánh hai lần chạy</title><style>%s</style></head><body>"
        "<h1>So sánh hai lần chạy: %s và %s</h1>"
        "<p>Lần chạy thử không được công bố và không thay kết quả chính thức. Số liệu trong tệp này là dữ "
        "liệu hiện có của trường.</p>"
        "<p class=\"tom-tat\">%s</p><div class=\"luoi-lan\">%s%s</div>%s%s%s%s%s</body></html>" % (
            _CSS_SO_SANH, e(la), e(lb), e(kq.get("tom_tat", {}).get("vi") or tom_tat_so_sanh(kq, "vi")),
            _the_lan_html(a), _the_lan_html(b),
            bang("Tổng quan", ["Chỉ số", la, lb], tong),
            bang("Từng câu lạc bộ", ["Câu lạc bộ", "Sức chứa", "Nhận — " + la, "Nhận — " + lb,
                                       "Điểm chuẩn — " + la, "Điểm chuẩn — " + lb],
                 [(c["ten"], _so(c["suc_chua"]), c["a"]["da_nhan"], ct(c["a"]["da_nhan"], c["b"]["da_nhan"]),
                   _so(c["a"]["diem_chuan"]), ct(c["a"]["diem_chuan"], c["b"]["diem_chuan"])) for c in kq["clb"]]),
            bang("Theo nhóm ưu tiên", dau_nhom, nhom_dong(kq["nhom"])),
            bang("Theo lớp", ["Lớp"] + dau_nhom[1:], nhom_dong(kq["lop"])),
            ds_doi))


class _Tho(str):
    """Chuỗi HTML đã thoát sẵn (không thoát lần nữa)."""
