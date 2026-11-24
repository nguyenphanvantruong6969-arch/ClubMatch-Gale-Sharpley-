"""Câu giải thích kết quả FA-DAA cho học sinh (V§9.1) — MỘT nơi duy nhất giữ mẫu câu.

Hàm nhận MỘT dòng lý do (`fa_daa.ly_do_ket_qua`) và tên CLB; câu chỉ nói về học sinh đó và CLB —
KHÔNG bao giờ chứa mã hay tên học sinh khác (rủi ro C3). Không hứa "ưu tiên bù kỳ sau": ưu tiên bù
(D1) chưa làm trong kỳ này.

Dữ liệu trong test là dữ liệu MÔ PHỎNG.
"""

from __future__ import annotations


def _so(x) -> str:
    """12.0 -> '12'; 7.5 -> '7.5'."""
    if x is None:
        return ""
    f = float(x)
    return str(int(f)) if f.is_integer() else str(round(f, 2))


def cau_ly_do(dong: dict, ten_clb: str) -> str:
    """Câu tiếng Việt giải thích `dong` (một dòng `fa_ly_do`) cho chính học sinh đó."""
    ma = dong.get("reason")
    if dong.get("outcome") == "ACCEPTED":
        return "Em được xếp vào %s – nguyện vọng %s của em." % (ten_clb, dong.get("rank_in_list"))
    if ma == "SCORE":
        return ("%s đủ chỗ với các bạn có điểm thử thách cao hơn (điểm chuẩn %s, em %s)."
                % (ten_clb, _so(dong.get("cut_score")), _so(dong.get("diem_em"))))
    if ma == "MEDAL":
        if dong.get("diem_em") is None:        # CLB không có điểm thi (xét huy chương ngay): không nói "bằng điểm"
            return "Các bạn đặt huy chương cao hơn ở %s được xét trước." % ten_clb
        return ("Em và các bạn bằng điểm; các bạn có huy chương cao hơn ở %s được xét trước."
                % ten_clb)
    if ma == "RESERVED":
        return "%s dành chỗ cho các bạn đã được giữ chỗ nên em chưa vào được." % ten_clb
    if ma == "LOTTERY":
        cau = ("Em bằng %s bạn khác ở mọi tiêu chí, tranh %s chỗ cuối; số bốc thăm của em chưa trúng."
               % (dong.get("n_hoa"), dong.get("k_cho")))
        if dong.get("waitlist_pos"):
            cau += " Em đứng thứ %s danh sách chờ." % dong["waitlist_pos"]
        return cau
    if ma == "BELOW_PASS":
        return "Em chưa đạt mốc %s điểm của %s." % (_so(dong.get("cut_score")), ten_clb)
    if ma == "NOT_ATTEMPTED":
        return "Em chưa làm bài thử thách của %s nên chưa được xét ở CLB này." % ten_clb
    if ma == "CLUB_CLOSED":
        return "%s không đủ thành viên tối thiểu nên tạm không mở kỳ này." % ten_clb
    if ma == "KHONG_DANG_KY":
        return "Em chưa đăng ký CLB nào ở buổi này nên được xếp vào %s (CLB Tự do)." % ten_clb
    if ma == "HET_NGUYEN_VONG":
        return ("Các CLB em đã chọn ở buổi này đều đủ chỗ nên em được xếp vào %s (CLB Tự do)."
                % ten_clb)
    return ""


# GT1-L1: câu giải thích cho lần chạy RB-DA thường (FA tắt). Mã do `giai_trinh.py` quyết định; câu CHỈ ở đây.
# GT4-L4: MỘT câu cố định đi kèm bảng khi có hàng "chỗ dành riêng" (RESERVED): con số "mức vào được" là mức của người
# nhận cuối ở các chỗ thường, không phải ngưỡng riêng của học sinh đó. Không số, không xưng hô: dùng cho cả ba nơi đọc.
CAU_GIU_CHO = ("Một số chỗ của CLB được giữ riêng cho nhóm theo quy định của trường; "
               "mức vào được chỉ áp dụng cho các chỗ còn lại.")

GIONG_HOC_SINH = "hoc_sinh"
GIONG_GIAO_VIEN = "giao_vien"


def _cau_rbda_giao_vien(ma, hang, cut, diem_em, ten_clb):
    """Giọng trung tính (ngôi thứ ba) cho màn giáo viên / quản trị — cùng nội dung, không xưng "Em"."""
    if ma == "ACCEPTED":
        return ("Học sinh được xếp vào %s – nguyện vọng %s." % (ten_clb, hang) if hang
                else "Học sinh được xếp vào %s." % ten_clb)
    if ma == "HIGHER_CHOICE_ACCEPTED":
        return "Học sinh đã được xếp vào một CLB xếp cao hơn nên %s không cần xét." % ten_clb
    if ma == "FULL_SCORE":
        cau = "%s đã đủ chỗ với các học sinh có điểm thử thách cao hơn" % ten_clb
        if cut is not None and diem_em is not None:
            cau += " (điểm chuẩn %s, học sinh %s)" % (_so(cut), _so(diem_em))
        return cau + "."
    if ma == "FULL_LOTTERY":
        return ("%s đã đủ chỗ; học sinh bằng các học sinh khác ở mọi tiêu chí nên chỗ cuối được quyết định bằng bốc "
                "thăm, và số bốc thăm của học sinh chưa trúng." % ten_clb)
    if ma == "FULL_GROUP":
        return "%s đã đủ chỗ; các học sinh thuộc nhóm ưu tiên cao hơn được xét trước." % ten_clb
    if ma == "FULL_WHARTON":
        return ("%s đã đủ chỗ; học sinh bằng các học sinh khác ở các tiêu chí trước, và các học sinh có điểm quyết "
                "tâm cao hơn được xét trước." % ten_clb)
    if ma == "RESERVED":
        return "%s dành một số chỗ cho nhóm được giữ chỗ nên học sinh chưa vào được." % ten_clb
    if ma == "NOT_TESTED":
        return ("%s có thử thách đầu vào; học sinh chưa có điểm nên được xét sau các học sinh đã có điểm, "
                "và CLB đã đủ chỗ." % ten_clb)
    if ma == "NO_CHOICES":
        return "Học sinh chưa đăng ký nguyện vọng nào ở buổi này nên chưa được xếp CLB."
    if ma == "UNASSIGNED":
        return "Học sinh chưa có chỗ ở buổi này: các CLB đã chọn đều đã đủ chỗ."
    return ""


def cau_ly_do_rbda(dong: dict, ten_clb: str, giong: str = GIONG_HOC_SINH) -> str:
    """Câu tiếng Việt cho một lựa chọn của chính học sinh trong lần chạy RB-DA thường.

    `dong["ma"]`: ACCEPTED, HIGHER_CHOICE_ACCEPTED, FULL_SCORE, FULL_LOTTERY, FULL_GROUP, FULL_WHARTON,
    RESERVED, NOT_TESTED. Chỉ nói về học sinh đó và CLB — không mã, tên hay số bốc thăm của em khác.
    `giong`: "hoc_sinh" (mặc định, giữ nguyên từng byte câu của GT1: phiếu in, màn học sinh) hoặc "giao_vien"
    (GT4-L4: trung tính, cho khung tra cứu của giáo viên / quản trị). Giá trị lạ dùng như mặc định.
    """
    ma = dong.get("ma")
    if giong == GIONG_GIAO_VIEN:
        return _cau_rbda_giao_vien(ma, dong.get("rank_in_list"), dong.get("cut_score"), dong.get("diem_em"), ten_clb)
    if ma == "ACCEPTED":
        hang = dong.get("rank_in_list")
        return ("Em được xếp vào %s – nguyện vọng %s của em." % (ten_clb, hang) if hang
                else "Em được xếp vào %s." % ten_clb)
    if ma == "HIGHER_CHOICE_ACCEPTED":
        return "Em đã được xếp vào một CLB em xếp cao hơn nên %s không cần xét." % ten_clb
    if ma == "FULL_SCORE":
        cau = "%s đã đủ chỗ với các bạn có điểm thử thách cao hơn" % ten_clb
        if dong.get("cut_score") is not None and dong.get("diem_em") is not None:
            cau += " (điểm chuẩn %s, em %s)" % (_so(dong["cut_score"]), _so(dong["diem_em"]))
        return cau + "."
    if ma == "FULL_LOTTERY":
        return ("%s đã đủ chỗ; em bằng các bạn ở mọi tiêu chí nên chỗ cuối được quyết định bằng bốc thăm, "
                "và số bốc thăm của em chưa trúng." % ten_clb)
    if ma == "FULL_GROUP":
        return "%s đã đủ chỗ; các bạn thuộc nhóm ưu tiên cao hơn được xét trước." % ten_clb
    if ma == "FULL_WHARTON":
        return ("%s đã đủ chỗ; em bằng các bạn ở các tiêu chí trước, và các bạn có điểm quyết tâm "
                "cao hơn được xét trước." % ten_clb)
    if ma == "RESERVED":
        return "%s dành một số chỗ cho nhóm được giữ chỗ nên em chưa vào được." % ten_clb
    if ma == "NOT_TESTED":
        return ("%s có thử thách đầu vào; em chưa có điểm nên được xét sau các bạn đã có điểm, "
                "và CLB đã đủ chỗ." % ten_clb)
    if ma == "NO_CHOICES":
        return "Em chưa đăng ký nguyện vọng nào ở buổi này nên chưa được xếp CLB."
    if ma == "UNASSIGNED":
        return "Em chưa có chỗ ở buổi này: các CLB em chọn đều đã đủ chỗ."
    return ""
