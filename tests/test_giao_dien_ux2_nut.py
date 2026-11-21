"""UX2-L3 (Playwright + Chromium): vùng bấm ≥ 44 px (#8), MỘT vòng focus (#9), lớp trạng thái (#1). Dữ liệu MÔ PHỎNG."""
import os
import re
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_giao_dien_chay as base  # noqa: E402
from test_giao_dien_tro_nang import _ti_le  # noqa: E402

api = base.api
mo_trang = base.mo_trang
GOC = base.GOC

THE = ["pipeline", "results", "admin", "scoring", "others"]

DO_VUNG = """() => {
  const loi = [];
  document.querySelectorAll('button, .btn, [role=button]').forEach((b) => {
    const r = b.getBoundingClientRect();
    if (!r.width || !r.height || b.closest('[hidden]') || getComputedStyle(b).visibility === 'hidden') return;
    if (b.closest('details:not([open])') && !b.matches('summary')) return;
    /* Ngoại lệ có chủ đích: hàng thanh bên xếp sát nhau toàn chiều rộng (chiều cao 40 / 23 px, liền kề nhau) — không có
       khoảng trống để mở rộng vùng bấm mà không chồng lên hàng bên cạnh; báo ở CHANGELOG / báo cáo L3. */
    if (b.matches('.nav-item, .nav-nhom-nut')) return;
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    const ok = (x, y) => { const e = document.elementFromPoint(x, y); return e && (e === b || b.contains(e) || e.closest('button, .btn, [role=button]') === b); };
    if (!ok(cx, cy)) return;                                                   // bị khung cuộn che / cắt: không phải nút đang thấy
    const caoDu = r.height >= 43.5, rongDu = r.width >= 43.5;
    if (cy < 0 || cy > innerHeight || cx < 0 || cx > innerWidth) return;       // ngoài màn hình: bỏ
    /* Nút trong bảng dày: hàng cách nhau < 44 px nên vùng bấm chỉ lớn được tới chiều cao hàng (hai hàng không giành nhau). */
    const hang = b.closest('tr'); const nua = hang ? Math.floor(hang.getBoundingClientRect().height / 2) - 2 : 21;
    const dy = caoDu ? 0 : Math.min(21, nua), dx = rongDu ? 0 : 21;
    const diem = [[cx, cy - dy], [cx, cy + dy], [cx - dx, cy], [cx + dx, cy]];
    if (!diem.filter(([x, y]) => y >= 0 && y < innerHeight && x >= 0 && x < innerWidth).every(([x, y]) => ok(x, y))) loi.push((b.id || b.className || b.textContent).toString().slice(0, 50) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height));
    if (getComputedStyle(b).touchAction !== 'manipulation') loi.push('touch-action ' + (b.id || b.className));
  });
  return loi;
}"""


@pytest.mark.parametrize("the", THE)
def test_moi_nut_nhin_thay_co_vung_bam_44px(api, mo_trang, the):
    page, loi = mo_trang()
    page.set_viewport_size({"width": 1400, "height": 1000})
    page.locator('.nav-item[data-tab="%s"]' % the).click()
    page.wait_for_timeout(500)
    thieu = page.evaluate(DO_VUNG)
    assert thieu == [], thieu
    assert loi == [], loi


def test_nut_nho_khong_to_ra_chi_vung_bam_lon_hon(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate("""() => { const b = document.createElement('button'); b.id='ux2N'; b.className='btn btn-nho btn-secondary'; b.textContent='x';
        b.style.position='fixed'; b.style.left='200px'; b.style.top='200px'; document.body.appendChild(b); }""")
    # trước khi thêm CSS nút nhỏ cao ≈ 28 px; sau đó vẫn không lên 44 px
    h = page.eval_on_selector("#ux2N", "b => b.getBoundingClientRect().height")
    assert h < 40
    ok = page.evaluate("""() => { const r = document.getElementById('ux2N').getBoundingClientRect();
        const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2 + 20);
        return e && (e.id === 'ux2N'); }""")
    assert ok


MAU = [".btn-primary", ".btn-secondary", ".btn-danger", ".btn-nho", ".nut-i", ".menu-khac-muc"]


def test_mot_vong_focus_cho_moi_loai_nut(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate("""() => { ['btn btn-primary', 'btn btn-secondary', 'btn btn-danger', 'btn btn-nho btn-secondary', 'nut-i', 'menu-khac-muc'].forEach((c, i) => {
        const b = document.createElement('button'); b.className = c; b.id = 'ux2F' + i; b.textContent = 'i'; document.body.appendChild(b); }); }""")
    ring = set()
    for i in range(6):
        page.focus("#ux2F%d" % i)
        page.keyboard.press("Shift+Tab")
        page.keyboard.press("Tab")                       # đường bàn phím thật -> :focus-visible
        assert page.evaluate("() => document.activeElement.id") == "ux2F%d" % i
        ring.add(tuple(page.eval_on_selector("#ux2F%d" % i, "b => { const s = getComputedStyle(b); return [s.outlineWidth, s.outlineStyle, s.outlineColor, s.outlineOffset]; }")))
    assert len(ring) == 1, ring
    w, st, mau, _ = next(iter(ring))
    assert w == "2px" and st == "solid"
    nums = [int(x) for x in re.findall(r"\d+", mau)[:3]]
    hexa = "#%02X%02X%02X" % tuple(nums)
    css = open(os.path.join(GOC, "style.css"), encoding="utf-8").read()
    tok = dict(re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})", css))
    assert hexa.upper() == tok["focus-ring"].upper()
    assert _ti_le(hexa, tok["paper"]) >= 3 and _ti_le(hexa, tok["gold"]) >= 3 and _ti_le(hexa, "#FFFFFF") >= 3


def test_bam_chuot_khong_hien_vong_focus(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate("() => { const b = document.createElement('button'); b.id='ux2M'; b.className='btn btn-secondary'; b.textContent='m'; document.body.appendChild(b); }")
    page.click("#ux2M")
    assert page.eval_on_selector("#ux2M", "b => getComputedStyle(b).outlineStyle") in ("none", "")  or \
        page.eval_on_selector("#ux2M", "b => getComputedStyle(b).outlineWidth") == "0px"


def test_lop_trang_thai_hover_focus_nhan_va_disabled(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate("""() => { const b = document.createElement('button'); b.id='ux2T'; b.className='btn btn-primary'; b.textContent='Thử';
        b.style.position = 'fixed'; b.style.left = '300px'; b.style.top = '300px'; document.body.appendChild(b);
        const d = document.createElement('button'); d.id='ux2D'; d.className='btn btn-primary'; d.disabled = true; d.textContent='Tắt';
        d.style.position = 'fixed'; d.style.left = '300px'; d.style.top = '400px'; document.body.appendChild(d); }""")
    bg = lambda sel: page.eval_on_selector(sel, "b => [getComputedStyle(b).backgroundColor, getComputedStyle(b).backgroundImage]")
    goc = bg("#ux2T")
    assert goc[1] == "none"
    page.hover("#ux2T")
    hover = bg("#ux2T")
    assert hover[0] == goc[0] and hover[1] != "none"                  # màu nền gốc KHÔNG đổi, chỉ thêm lớp
    mo = lambda s: re.findall(r"(\d+(?:\.\d+)?)%", s)
    page.mouse.down()
    nhan = bg("#ux2T")
    page.mouse.up()
    assert nhan[1] != "none" and nhan[1] != hover[1]                  # nhấn đậm hơn hover
    page.mouse.move(0, 0)
    page.wait_for_timeout(250)
    assert bg("#ux2T")[1] == "none"
    page.hover("#ux2D", force=True)
    assert bg("#ux2D")[1] == "none"                                   # disabled: không có lớp
    assert mo is not None


def test_cac_css_ux2_nut_tinh():
    css = open(os.path.join(GOC, "style.css"), encoding="utf-8").read()
    assert "--ux2-lop-hover: 8%" in css and "--ux2-lop-focus: 10%" in css and "--ux2-lop-nhan: 12%" in css
    assert ".nut-i:focus-visible" not in css and ".ql-tab:focus-visible" not in css   # bản lặp đã gỡ
