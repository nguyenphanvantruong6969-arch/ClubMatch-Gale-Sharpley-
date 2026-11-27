"""UX6-L1: bớt chữ giải thích (quy tắc a/b/c trong docs/phien/UX6_GIAO_THUC.md §0) và thanh "Việc tiếp theo" ngắn.
Phần tĩnh đọc index.html / i18n.js; phần Chromium dùng sổ 120 học sinh MÔ PHỎNG đã chạy xếp (seed 42)."""

import os
import re

import pytest

from _ux5a_chung import GOC, mo_ux5a  # noqa: F401

NGUON = {n: open(os.path.join(GOC, n), encoding="utf-8").read() for n in ("index.html", "i18n.js")}
RE_PT = re.compile(r'<(?:p|span|div)\b[^>]*class="[^"]*\b(?:hint-text|view-desc|hint)\b[^"]*"')

KHOA_XOA = [
    "pipeline_desc", "kq_desc", "ux5a_gt_mo_ta", "ux5a_kq_mo_bang", "others_desc", "xuat_hint_hoc_sinh",
    "do_phu_desc", "nv_desc", "tham_tai_lap", "fallback_desc", "ux5b_fallback_desc_qt", "fallback_buoi_hint",
    "admin_desc", "ux4_mo_clb", "admin_tai_buoi_desc", "ux4_mo_hs", "wh_sua_rong",
    "wh_dang_mo_khong_can", "wh_nk_chon_em", "wh_nhat_ky_rong", "ux4_mo_lam_lai", "danger_zone_safety",
    "ux4_mo_cach_xep", "gt2_tc_nhom_goi_y", "scoring_desc", "cb_desc", "cb_duong_hint", "cb_duong_a_ghi",
    "cb_duong_b_ghi", "cb_buoc_trong", "import_hint", "gt2_tc_mo_ta", "gt2_thu_mo_ta",
]
KHOA_HOI = [  # chuyển sau nút "?": khoá còn, phần tử mang class ux6-hoi-nd, không còn là hint-text
    "xuat_theo_lop_hint", "clb_desc", "du_tru_desc", "chua_co_cho_desc", "tham_desc",
    "dd_goi_y", "v2_goi_y", "mt2_ghi_chu", "buoi_hint_form", "ti_le_choi_giai_thich", "fallback_step3_hc_hint",
    "ph_goi_y_nut", "gt2_ad_ghi_chu", "wh_ql_desc", "dc_mo_ta",
]


def test_toi_da_25_phan_tu_goi_y_trong_index_html():
    dem = len(RE_PT.findall(NGUON["index.html"]))
    assert dem <= 25, dem


@pytest.mark.parametrize("khoa", KHOA_XOA)
def test_khoa_da_xoa_o_ca_vi_va_en(khoa):
    assert not re.search(r"\b%s:" % khoa, NGUON["i18n.js"]), khoa
    assert 'data-i18n="%s"' % khoa not in NGUON["index.html"], khoa


@pytest.mark.parametrize("khoa", KHOA_HOI)
def test_noi_dung_con_duoc_giu_sau_nut_hoi(khoa):
    assert len(re.findall(r"\b%s:" % khoa, NGUON["i18n.js"])) == 2, khoa     # vi + en
    m = re.search(r'<[^>]*data-i18n="%s"[^>]*>' % khoa, NGUON["index.html"])
    assert m and "ux6-hoi-nd" in m.group(0) and "hint-text" not in m.group(0), khoa


def test_cau_va_nut_thanh_tiep_theo_ngan_va_khong_lap_so():
    for ten in ("nap_so", "canh_bao", "chay", "xu_ly", "xuat"):
        vi = re.search(r"\bux1a_cau_%s: \"([^\"]*)\"" % ten, NGUON["i18n.js"]).group(1)
        assert len(vi) <= 45, (ten, vi)
        nut = re.search(r"\bux1a_nut_%s: \"([^\"]*)\"" % ten, NGUON["i18n.js"]).group(1)
        assert "{n}" not in nut, (ten, nut)


def test_thanh_tiep_theo_mot_cau_mot_nut_cung_cho_moi_the(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "results")
    page.wait_for_function("!document.getElementById('viecTiepTheo').hidden")
    hop = {}
    for tab in ("results", "pipeline", "others"):
        page.locator('.nav-item[data-tab="%s"]' % tab).click()
        page.wait_for_timeout(300)
        cuoi = "#viecTiepTheoNut2" if page.locator("#viecTiepTheoNut2").is_visible() else "#viecTiepTheoNut"
        b = page.locator(cuoi).bounding_box()
        k = page.locator("#viecTiepTheo").bounding_box()
        hop[tab] = (round(b["x"] - k["x"]), round(k["x"] + k["width"] - b["x"] - b["width"]))
        assert len(page.locator("#viecTiepTheoCau").inner_text()) <= 45
    assert len(set(hop.values())) == 1, hop                                   # nút nằm đúng một chỗ ở mọi thẻ
    assert hop["results"][1] <= 20, hop                                       # nút sát mép phải của thanh
    assert not loi, loi
