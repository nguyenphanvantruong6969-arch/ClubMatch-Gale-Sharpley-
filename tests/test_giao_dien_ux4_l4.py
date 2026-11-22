"""UX4-L4: tab Cách xếp. Một câu hỏi MT1 + câu hỏi cách chọn, "Tuỳ chỉnh thêm" gập ba ô chọn cũ (ô không áp dụng thì ẩn),
"Thử cách xếp này" là nút vàng duy nhất, hai ô chọn lần chạy nằm trong "So sánh với lần khác".
Chromium thật qua `browser_host`; dữ liệu MÔ PHỎNG (bộ do_anh_huong_seed). Dùng lại fixture của test_giao_dien_gt2_thu."""

import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_giao_dien_gt2_thu import mo  # noqa: E402,F401 (fixture)

JS_DEM = """() => {
  const vis = e => e.checkVisibility({checkVisibilityCSS: true, contentVisibilityAuto: true});
  const root = document.getElementById('qlPanelCachXep');
  const q = 'button, select, input:not([type=hidden]), textarea, summary, a[href]';
  return Array.from(root.querySelectorAll(q)).filter(e => vis(e) && !e.disabled && !e.closest('tbody')).map(e => e.id || e.tagName);
}"""
JS_VANG = "() => Array.from(document.querySelectorAll('.btn-primary')).filter(e => e.checkVisibility()).map(e => e.id)"
CAM = ["cấu hình", "suất", "nhãn", "Quỹ 1", "Phóng", "Nâng cao"]


def _vao(mo_, gap=False):
    page, api, db, loi = mo_(chay=True)
    page.evaluate("document.getElementById('ux1aNangCao').open = %s" % ("true" if gap else "false"))
    page.evaluate("document.getElementById('gt2ThuSoSanhKhac').open = false")
    return page, api, db, loi


def _luat(api):
    return api.get_workspace_config()["data"]["config"]["rules"]


def test_ngan_sach_hick_va_mot_nut_vang_o_cach_xep(mo):  # noqa: F811
    page, api, db, loi = _vao(mo)
    ds = page.evaluate(JS_DEM)
    assert len(ds) <= 9, ds
    assert "gt2TcPriority" not in ds and "gt2ThuChay" in ds
    for nhom in page.locator("#ux1aCaiDat [role=radiogroup]").all():
        n = nhom.locator("[role=radio]").count()
        assert 0 < n <= 3
    assert page.evaluate(JS_VANG) == ["gt2ThuChay"]
    assert page.locator("#gt2ThuChay").inner_text().strip() == "Thử cách xếp này"
    assert page.locator("#ux1aNangCao > summary").inner_text().strip() == "Tuỳ chỉnh thêm"
    assert page.locator("#gt2ThuSoSanhKhac > summary").inner_text().strip() == "So sánh với lần khác"
    assert page.locator("#gt2ThuChon").is_hidden() and page.locator("#gt2ThuSoSanh").is_hidden()
    assert not loi, loi


def test_o_khong_ap_dung_bi_an_khong_chi_vo_hieu(mo):  # noqa: F811
    page, api, db, loi = _vao(mo, gap=True)
    an = lambda i: page.locator("#" + i).evaluate("e => !e.closest('.club-field').checkVisibility()")  # noqa: E731
    page.select_option("#gt2TcPriority", "score")
    assert an("gt2TcTierMode") and an("gt2TcTiers") and not an("gt2TcScoreScope")
    page.select_option("#gt2TcPriority", "score+tier")
    assert not an("gt2TcTierMode") and not an("gt2TcTiers") and not an("gt2TcScoreScope")
    page.select_option("#gt2TcPriority", "tier")
    assert not an("gt2TcTierMode") and not an("gt2TcTiers") and an("gt2TcScoreScope")
    assert not loi, loi


def test_nhan_de_hieu_gia_tri_van_la_ma_cu(mo):  # noqa: F811
    page, api, db, loi = _vao(mo, gap=True)
    opt = lambda i: page.eval_on_selector_all("#%s option" % i, "ns => ns.map(n => [n.value, n.textContent])")  # noqa: E731
    assert opt("gt2TcPriority") == [["score", "Điểm bài thi cao hơn"], ["tier", "Học sinh thuộc nhóm ưu tiên"],
                                    ["score+tier", "Cả hai"]]
    assert opt("gt2TcTierMode") == [["reserve", "Giữ một số chỗ riêng cho nhóm"], ["strict", "Nhóm luôn được xét trước"]]
    assert opt("gt2TcScoreScope")[0][1].startswith("Mỗi ") and opt("gt2TcScoreScope")[1][1].startswith("Một điểm chung")
    assert page.locator("#gt2TcPriorityNhan").inner_text().strip() == "Khi CLB hết chỗ, ai được xét trước?"
    assert not loi, loi


@pytest.mark.parametrize("priority, tier_mode, score_scope", [
    ("score", "reserve", "per_slot"), ("score+tier", "strict", "per_slot"),
    ("score+tier", "reserve", "per_person"), ("tier", "strict", "per_slot")])
def test_luu_tuy_chinh_gui_dung_cung_gia_tri_nhu_o_chon_cu(mo, priority, tier_mode, score_scope):  # noqa: F811
    page, api, db, loi = _vao(mo, gap=True)
    page.select_option("#gt2TcPriority", priority)
    # ô ẩn vẫn giữ giá trị của nó; ô hiện chọn đúng giá trị cần thử
    page.evaluate("(v) => { document.getElementById('gt2TcTierMode').value = v[0]; document.getElementById('gt2TcScoreScope').value = v[1]; }", [tier_mode, score_scope])
    page.evaluate("document.getElementById('gt2TcTiers').value = 'khoi_10'")
    page.click("#gt2TcLuu")
    page.wait_for_function("document.getElementById('gt2TcPhanHoi').innerText.length > 0")
    r = _luat(api)
    assert (r["priority"], r["tier_mode"], r["score_scope"]) == (priority, tier_mode, score_scope)
    assert r["tiers"] == ["khoi_10"]
    assert not loi, loi


def test_chu_cam_va_thu_tu_bat_bien_2_o_cach_xep(mo):  # noqa: F811
    page, api, db, loi = _vao(mo, gap=True)
    page.evaluate("document.getElementById('gt2ThuSoSanhKhac').open = true")
    chu = page.locator("#qlPanelCachXep").inner_text()
    for c in CAM:
        assert c not in chu, c
    assert not re.search(r"\d{4}-\d\d-\d\d \d\d:", chu)
    assert "Phần mềm không dùng thứ hạng nguyện vọng" in chu        # bất biến 2 còn nguyên
    assert not loi, loi


def test_thu_cach_xep_so_sanh_voi_lan_chinh_thuc_va_ngay_gio_de_doc(mo):  # noqa: F811
    page, api, db, loi = _vao(mo)
    page.click("#gt2ThuChay")
    page.wait_for_selector("#gt2ThuKetQua table, #gt2ThuKetQua .gt2-bang-cuon", state="attached")
    page.evaluate("document.getElementById('gt2ThuSoSanhKhac').open = true")
    tx = page.eval_on_selector_all("#gt2ThuA option, #gt2ThuB option", "ns => ns.map(n => n.textContent)")
    assert tx and all(re.search(r"\d\d/\d\d/\d{4} \d\d:\d\d", x) and not re.search(r"\d{4}-\d\d-\d\d", x) for x in tx), tx
    assert any(x.startswith("Xếp chính thức lần") for x in tx) and any(x.startswith("Thử lần") for x in tx), tx
    assert page.locator("#gt2ThuChon").is_visible() and page.locator("#gt2ThuSoSanh").is_visible()
    assert not loi, loi
