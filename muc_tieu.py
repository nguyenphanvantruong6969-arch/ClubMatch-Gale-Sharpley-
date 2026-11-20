"""MT1-L1 — danh mục MỤC TIÊU (ba thẻ): phần THUẦN, không đọc/ghi CSDL.

Trường trả lời MỘT câu hỏi ở Cài đặt, "Khi một CLB đông người, trường ưu tiên điều gì?", bằng cách chọn một
trong ba thẻ. Mỗi thẻ chỉ đặt lại các luật xếp ĐÃ CÓ (`priority`, `tier_mode`, `score_scope`, `tiers`) và, ở thẻ
`danh_cho`, số chỗ giữ lại của mỗi CLB. Thuật toán lõi không đổi; thẻ không bao giờ chạm `wharton` / `fa_daa`.

Số chỗ giữ = `ceil(tỉ lệ nhóm × sức chứa)` (MT0 F1/F2), chỉ đọc DANH SÁCH HỌC SINH (nhóm của từng em) — không
đọc nguyện vọng, không đọc kết quả lần trước (bất biến 2). Số liệu trong test là MÔ PHỎNG.
"""

from __future__ import annotations

from typing import Optional

from rbda_priority_pipeline import chuan_hoa_tim_kiem

NANG_LUC = "nang_luc"
CO_HOI = "co_hoi"
DANH_CHO = "danh_cho"
TUY_CHINH = "tuy_chinh"
MUC_TIEU_MAC_DINH = NANG_LUC

# Số chỗ giữ từ mức này trở xuống chỉ là "cho có" (MT0 F4): báo một dòng cảnh báo.
CHO_GIU_IT = 2

# Ba thẻ, theo thứ tự hiển thị. `luat` chỉ gồm khoá của LUAT_XEP_MAC_DINH (test canh), không `wharton`/`fa_daa`.
BO_MUC_TIEU = {
    NANG_LUC: {
        "id": NANG_LUC,
        "tieu_de": {"vi": "Theo năng lực", "en": "By ability"},
        "cau": {"vi": "CLB có thi chọn theo điểm; CLB không thi bốc thăm công bằng.",
                "en": "Clubs with a test pick by score; clubs without one use a fair lottery."},
        "luat": {"priority": "score", "tier_mode": "reserve", "score_scope": "per_slot", "tiers": []},
        "doi_cho": False,
    },
    CO_HOI: {
        "id": CO_HOI,
        "tieu_de": {"vi": "Cơ hội như nhau", "en": "Equal chance"},
        "cau": {"vi": "Mọi em có cơ hội như nhau: bốc thăm, không xét điểm thi.",
                "en": "Everyone has the same chance: a lottery, test scores are not used."},
        "luat": {"priority": "tier", "tiers": []},
        "doi_cho": False,
    },
    DANH_CHO: {
        "id": DANH_CHO,
        "tieu_de": {"vi": "Dành chỗ cho một nhóm", "en": "Seats kept for a group"},
        "cau": {"vi": "Giữ một số chỗ ở mỗi CLB cho một nhóm (vd. khối 10, hoàn cảnh khó khăn).",
                "en": "Keep some seats in every club for one group (e.g. grade 10, disadvantaged)."},
        # Cùng bốn khoá với `nang_luc`: đặt lại cả danh sách nhóm và phạm vi điểm, để thẻ sáng lại sau khi
        # luật từng bị sửa tay (khác nhau ở CLB: chỗ giữ cho nhóm).
        "luat": {"priority": "score", "tier_mode": "reserve", "score_scope": "per_slot", "tiers": []},
        "doi_cho": True,
    },
}


def _khoa_nhom(ten) -> str:
    """Khoá so sánh nhóm: cùng cách `xay_tier_rank` chuẩn hoá (hoa/thường, dấu, khoảng trắng)."""
    return " ".join(chuan_hoa_tim_kiem(ten or "").split())


def rules_cua_muc_tieu(muc_tieu: str, rules) -> dict:
    """Bản sao của `rules` đã áp luật của thẻ `muc_tieu`; mọi khoá khác (kể cả `wharton`, `fa_daa`) giữ nguyên.

    Ném `KeyError` khi `muc_tieu` không có trong `BO_MUC_TIEU`. Không sửa `rules` của người gọi.
    """
    vá = BO_MUC_TIEU[muc_tieu]["luat"]
    kq = dict(rules or {})
    for khoa, gia_tri in vá.items():
        kq[khoa] = list(gia_tri) if isinstance(gia_tri, list) else gia_tri
    return kq


def _khop_luat(rules, muc_tieu: str) -> bool:
    """Bốn khoá luật hiện tại của `rules` có đúng như thẻ `muc_tieu` không (thiếu khoá = mặc định)?"""
    r = rules or {}
    mac_dinh = BO_MUC_TIEU[NANG_LUC]["luat"]
    for khoa, mong_doi in BO_MUC_TIEU[muc_tieu]["luat"].items():
        co = r.get(khoa, mac_dinh.get(khoa))
        if khoa == "tiers":
            co = list(co or [])
        if co != mong_doi:
            return False
    return True


def cac_nhom(students) -> list[dict]:
    """Các nhóm có trong danh sách học sinh: `[{nhan, so_em}]`, đông nhất trước, rồi theo tên.

    `students` = `{sid: {"reserve_group": ...}}`. Cùng một nhóm viết khác hoa/thường/dấu/khoảng trắng
    được gộp; nhãn hiện ra là cách viết gặp nhiều nhất. Em không có nhóm không được tính.
    """
    dem: dict[str, dict[str, int]] = {}
    for info in (students or {}).values():
        nhan = " ".join(str((info or {}).get("reserve_group") or "").split())
        khoa = _khoa_nhom(nhan)
        if khoa:
            dem.setdefault(khoa, {})
            dem[khoa][nhan] = dem[khoa].get(nhan, 0) + 1
    ra = []
    for khoa, cach_viet in dem.items():
        nhan = sorted(cach_viet, key=lambda n: (-cach_viet[n], n))[0]
        ra.append({"nhan": nhan, "so_em": sum(cach_viet.values())})
    return sorted(ra, key=lambda x: (-x["so_em"], x["nhan"]))


def de_xuat_cho_giu(students, clubs, nhom: Optional[str]) -> dict:
    """Số chỗ giữ cho `nhom` ở từng CLB: `min(sức chứa, ceil(tỉ lệ nhóm × sức chứa))`.

    Tỉ lệ = số em của nhóm / tổng số em trong `students` (chỉ đọc danh sách học sinh). Tính bằng số nguyên,
    không dùng số thực. Trả:
      * `cho_giu`      — `{club_id: số chỗ}` cho MỌI CLB;
      * `nhom`, `so_em_nhom`, `tong_em`;
      * `canh_bao`     — danh sách mã: `khong_co_nhom` (nhóm không có em nào, hay danh sách rỗng) và
                         `it_qua` (có CLB được giữ 1–2 chỗ: chỉ là "cho có", MT0 F4);
      * `clb_it`       — CLB bị `it_qua`;
      * `clb_ghi_de`   — CLB đang giữ chỗ cho NHÓM KHÁC (thẻ sẽ ghi đè; API dùng để hoàn tác đúng).
    """
    tong = len(students or {})
    khoa = _khoa_nhom(nhom)
    so_nhom = sum(1 for info in (students or {}).values()
                  if khoa and _khoa_nhom((info or {}).get("reserve_group")) == khoa)
    canh_bao: list[str] = []
    cho_giu: dict[str, int] = {}
    if not tong or not so_nhom:
        canh_bao.append("khong_co_nhom")
        cho_giu = {cid: 0 for cid in (clubs or {})}
    else:
        for cid, c in (clubs or {}).items():
            cap = int(c.get("capacity") or 0)
            # ceil(so_nhom * cap / tong) bằng số nguyên
            cho_giu[cid] = min(cap, -(-so_nhom * cap // tong)) if cap > 0 else 0
    clb_it = sorted(cid for cid, n in cho_giu.items() if 1 <= n <= CHO_GIU_IT)
    if clb_it:
        canh_bao.append("it_qua")
    clb_ghi_de = sorted(
        cid for cid, c in (clubs or {}).items()
        if (c.get("reserve_capacity") or 0) > 0
        and _khoa_nhom(c.get("reserve_group")) not in ("", khoa))
    return {"cho_giu": cho_giu, "nhom": nhom, "so_em_nhom": so_nhom, "tong_em": tong,
            "canh_bao": canh_bao, "clb_it": clb_it, "clb_ghi_de": clb_ghi_de}


def nhan_dien_muc_tieu(rules, clubs, da_chon=None, students=None) -> str:
    """Thẻ đang hiệu lực: `nang_luc` / `co_hoi` / `danh_cho`, hoặc `tuy_chinh` khi luật bị sửa tay.

    `da_chon` = `{"id", "nhom"}` đã lưu lần chọn thẻ (khoá cấu hình `muc_tieu`; không có = chưa chọn).
    Luật của `nang_luc` và `danh_cho` giống nhau, nên chỉ phân biệt được nhờ `da_chon` VÀ dữ liệu CLB:
      * luật `co_hoi` (priority = tier, không nhóm) → `co_hoi`;
      * luật `nang_luc` + `da_chon` là `danh_cho` + MỌI CLB đang giữ chỗ cho đúng nhóm đó → `danh_cho`
        (có `students` thì số chỗ từng CLB cũng phải đúng công thức, sửa tay một CLB là `tuy_chinh`);
      * luật `nang_luc` còn lại → `nang_luc` (chỗ giữ lấy từ dữ liệu nhập vẫn giữ nguyên);
      * mọi tổ hợp luật khác → `tuy_chinh`.
    Cấu hình mặc định (không `da_chon`) luôn cho `nang_luc`.
    """
    if _khop_luat(rules, CO_HOI):
        return CO_HOI
    if not _khop_luat(rules, NANG_LUC):
        return TUY_CHINH
    if (da_chon or {}).get("id") == DANH_CHO:
        khoa = _khoa_nhom((da_chon or {}).get("nhom"))
        if not khoa:
            return TUY_CHINH
        if not all(_khoa_nhom(c.get("reserve_group")) == khoa for c in (clubs or {}).values()):
            return TUY_CHINH
        if students is not None:
            mong = de_xuat_cho_giu(students, clubs, da_chon.get("nhom"))["cho_giu"]
            if any((c.get("reserve_capacity") or 0) != mong.get(cid)
                   for cid, c in (clubs or {}).items()):
                return TUY_CHINH
        return DANH_CHO
    return NANG_LUC
