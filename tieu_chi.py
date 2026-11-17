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
