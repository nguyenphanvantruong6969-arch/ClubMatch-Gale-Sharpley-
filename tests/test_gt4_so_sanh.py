"""GT4-L7 — trang so sánh: một câu tóm tắt chỉ có số, chênh lệch có chữ (+3 / −2), hai thẻ lần chạy với tiêu chí hai
tầng tách riêng, danh sách đổi chỗ gập mặc định, bỏ cột Buổi khi chỉ có một buổi, không bao giờ in `__mac_dinh__`.
Dữ liệu MÔ PHỎNG."""

import re

import tieu_chi
from test_gt2_so_sanh import A_ROWS, B_ROWS, CTX, _lan


def _kq(a_rows=None, b_rows=None, luat_a=None, luat_b=None):
    return tieu_chi.so_sanh_lan_chay(
        dict(_lan("chinh_thuc", 1, a_rows or A_ROWS), luat=luat_a or {}, run_at="2026-11-17T10:00:00"),
        dict(_lan("thu", 2, b_rows or B_ROWS), luat=luat_b or {"priority": "tier", "tiers": ["G1"]},
             run_at="2026-11-17T10:05:00"), CTX)


def _so(v, lang="vi"):
    s = ("%s" % v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v)
    return s.replace(".", ",") if lang == "vi" else s


def test_tom_tat_chi_co_so_va_dung_so_lieu():
    kq = _kq()
    ta, tb = kq["tong"]["a"]["pct_nv1"], kq["tong"]["b"]["pct_nv1"]
    doi = len({d["student_id"] for d in kq["doi"]})
    assert doi == 4
    vi = tieu_chi.tom_tat_so_sanh(kq, "vi")
    assert vi == "%d học sinh đổi CLB; được nguyện vọng 1: %s%% → %s%%." % (doi, _so(ta), _so(tb))
    en = tieu_chi.tom_tat_so_sanh(kq, "en")
    assert en == "%d students changed club; got first choice: %s%% → %s%%." % (doi, _so(ta, "en"), _so(tb, "en"))
    assert kq["tom_tat"] == {"vi": vi, "en": en}
    assert "kết luận" not in vi and "tốt hơn" not in vi and "better" not in en


def test_tom_tat_khong_doi_va_thieu_so():
    cung = _kq(A_ROWS, A_ROWS)
    assert tieu_chi.tom_tat_so_sanh(cung, "vi") == "Hai lần cho cùng kết quả: không suất nào đổi chỗ."
    assert tieu_chi.tom_tat_so_sanh(cung, "en") == "The two runs give the same result: no place changed."
    kq = _kq()
    kq["tong"]["a"]["pct_nv1"] = None                       # thiếu số thì bỏ vế sau, không in "None"
    assert tieu_chi.tom_tat_so_sanh(kq, "vi") == "4 học sinh đổi CLB."


def test_chenh_lech_co_dau_bang_chu():
    assert tieu_chi.chenh(3, 6) == "+3" and tieu_chi.chenh(6, 4) == "−2"        # U+2212
    assert tieu_chi.chenh(53.3, 60.0) == "+6,7" and tieu_chi.chenh(5, 5) == ""
    assert tieu_chi.chenh(None, 4) == "" and tieu_chi.chenh("x", 4) == ""
    assert tieu_chi.chenh(53.3, 60.0, "en") == "+6.7"


def test_the_lan_chay_co_ngay_va_tieu_de_tang():
    kq = _kq()
    for x in (kq["a"], kq["b"]):
        assert x["run_at"] and set(x["tang"]) == {"tang_1", "tang_2"}
    assert kq["b"]["tang"]["tang_2"]["vi"] == "Mọi học sinh"           # chỉ xét nhóm: một tầng "Mọi học sinh"


def test_html_cau_truc_moi():
    out = tieu_chi.dung_html_so_sanh(_kq())
    assert out.count('class="gt2-the-lan"') == 2
    the_b = out.split('class="gt2-the-lan"')[2].split("</section>")[0]
    assert "<ol" in the_b and "Mọi học sinh" in the_b
    the_a = out.split('class="gt2-the-lan"')[1].split("</section>")[0]
    assert the_a.count("<ol") == 2 and "Học sinh đã có điểm thi" in the_a and "Học sinh chưa có điểm thi" in the_a
    assert out.index("học sinh đổi CLB") < out.index("<table")                 # câu tóm tắt nằm trước mọi bảng
    assert "position:sticky" in out and "text-align:right" in out
    assert "<details" in out and "<details open" not in out                    # danh sách đổi chỗ gập mặc định
    assert re.search(r"<summary>Hiện danh sách \(\d+\)", out)
    assert "+" in out and "−" in out                                           # chênh lệch có chữ
    assert "__mac_dinh__" not in out and "<script" not in out
    assert "<th>Buổi</th>" not in out                                          # một buổi: không cột Buổi


def test_html_nhieu_buoi_hien_cot_va_nhan_than_thien():
    a = [("s1", "__mac_dinh__", "X", 1), ("s1", "thu_2", "Y", 1), ("s2", "thu_2", "X", 2)]
    b = [("s1", "__mac_dinh__", "Y", 2), ("s1", "thu_2", "X", 1), ("s2", "thu_2", "X", 2)]
    out = tieu_chi.dung_html_so_sanh(_kq(a, b))
    assert "<th>Buổi</th>" in out and "Mặc định" in out and "Thứ 2" in out and "__mac_dinh__" not in out


def test_html_mot_buoi_mac_dinh_khong_in_ten_noi_bo():
    a = [("s1", "__mac_dinh__", "X", 1)]
    b = [("s1", "__mac_dinh__", "Y", 1)]
    out = tieu_chi.dung_html_so_sanh(_kq(a, b))
    assert "__mac_dinh__" not in out and "<th>Buổi</th>" not in out
