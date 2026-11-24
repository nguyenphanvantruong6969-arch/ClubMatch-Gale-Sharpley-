"""UX5A giai đoạn 2: test hồi quy cho lỗi tìm được khi kiểm tay bằng Chromium thật (dữ liệu MÔ PHỎNG)."""

import pytest

from _ux5a_chung import mo_ux5a  # noqa: F401

# Phần tử trên cùng tại tâm của một mục menu phải chính là mục đó (hoặc nằm trong menu), không bị khung dưới đè.
JS_TREN_CUNG = """(id) => { const e = document.getElementById(id), r = e.getBoundingClientRect();
  const t = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return !!t && (t === e || e.contains(t) || t.closest('.menu-khac-hop') === e.closest('.menu-khac-hop')); }"""


@pytest.mark.parametrize("vai", ["quan_tri", "giao_vien"])
def test_menu_bao_cao_va_phieu_in_khong_bi_khung_duoi_de(mo_ux5a, vai):  # noqa: F811
    page, api, loi = mo_ux5a(vai, "results")
    page.click("#ux1bThemTom")
    for i in ("btnUx1bBaoCao", "btnUx1bPhieuLop", "btnUx1bBaoCaoPdf"):
        assert page.evaluate(JS_TREN_CUNG, i), i
    # cả hộp: mép dưới của hộp cũng không bị đè (dòng gợi ý nằm trong hộp)
    assert page.evaluate("""() => { const h = document.querySelector('#ux1bThemMenu .menu-khac-hop'), r = h.getBoundingClientRect();
      const t = document.elementFromPoint(r.left + r.width / 2, r.bottom - 6); return !!t && !!t.closest('#ux1bThemMenu'); }""")
    assert not loi, loi


def test_menu_xuat_tep_khac_khong_bi_khung_duoi_de(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "others")
    page.click("#xuatMenu > summary")
    assert page.evaluate("""() => { const h = document.querySelector('#xuatMenu .menu-khac-hop'), r = h.getBoundingClientRect();
      const t = document.elementFromPoint(r.left + r.width / 2, r.bottom - 6); return !!t && !!t.closest('#xuatMenu'); }""")
    assert not loi, loi


def test_dong_chon_them_tep_khong_dinh_sat_hang_nut(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri", "others")
    khoang = page.evaluate("""() => document.getElementById('btnXuatTuyChon').getBoundingClientRect().top
      - document.querySelector('#xuatNangCao > summary').getBoundingClientRect().bottom""")
    assert khoang >= 6, khoang
    assert not loi, loi


@pytest.mark.parametrize("vai", ["quan_tri", "giao_vien"])
@pytest.mark.parametrize("tab", ["results", "others"])
def test_tieng_anh_khong_con_tham_so_chua_dien_va_chu_viet(mo_ux5a, vai, tab):  # noqa: F811
    import re
    page, api, loi = mo_ux5a(vai, tab)
    page.click("#btnLangToggle")
    page.wait_for_function("document.documentElement.lang === 'en'")
    page.wait_for_timeout(500)
    page.evaluate("document.querySelectorAll('#view-%s details').forEach(d => d.open = true)" % tab)
    chu = page.evaluate("document.getElementById('view-%s').innerText" % tab)
    assert not re.findall(r"\{\w+\}", chu)
    # chữ có dấu tiếng Việt chỉ được là tên dữ liệu (tên em, tên CLB, tên lớp, buổi)
    dong = [d for d in chu.split("\n") if re.search(r"[ăâđêôơưáàảãạéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ]", d, re.I)]
    xau = [d for d in dong if not re.search(r"HS\d|CLB|Thứ|10A|^\W*$", d)]
    assert not xau, xau[:5]
    assert not loi, loi
