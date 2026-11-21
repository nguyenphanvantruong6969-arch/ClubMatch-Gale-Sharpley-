"""UX2-L3 (Playwright + Chromium): vùng bấm ≥ 44 px (#8), MỘT vòng focus (#9), lớp trạng thái (#1). Dữ liệu MÔ PHỎNG."""
import os
import re
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_giao_dien_chay as base  # noqa: E402
from test_giao_dien_tro_nang import _ti_le  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

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
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    /* Vùng nới ra mà trùng với một ô nhập / summary / nhãn bên cạnh thì ô đó thắng (FIX L3 vòng 2): vẫn tính là "có chỗ bấm". */
    const ok = (x, y) => { const e = document.elementFromPoint(x, y); return e && (e === b || b.contains(e) || e.closest('button, .btn, [role=button]') === b || e.closest('input, select, textarea, summary, label')); };
    if (!ok(cx, cy)) return;                                                   // bị khung cuộn che / cắt: không phải nút đang thấy
    if (cy < 0 || cy > innerHeight || cx < 0 || cx > innerWidth) return;       // ngoài màn hình: bỏ
    /* Lead (L3 fix1): .nav-item phải đủ 44 px. Ba nhóm còn lại không nới 44 được vì hàng liền kề đè nhau, nên chỉ đòi
       ≥ 24 px (WCAG 2.5.8 AA): tiêu đề nhóm thanh bên (.nav-nhom-nut), nút chữ trần trong td / li. Ngoại lệ: .ranking-list
       (hàng cách ~22 px, 24 px sẽ đè hàng bên) giữ 20 px. */
    const nhoGon = b.matches('.nav-nhom-nut') || (b.closest('td, li') && !b.matches('.btn'));
    const can = nhoGon ? (b.closest('.ranking-list') ? 9 : 11) : 21;
    const dy = r.height >= 2 * (can + 1) ? 0 : can, dx = r.width >= 2 * (can + 1) ? 0 : can;
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


# ---------- FIX L3 vòng 2: vùng bấm ::after của nút KHÔNG được cướp cú bấm của ô nhập ----------
MK_THU = "matkhau-gia-1"
CAC_THE = ["pipeline", "results", "admin", "scoring", "others", "fallback"]

DO_O_NHAP = """() => {
  const loi = [];
  document.querySelectorAll('details').forEach((d) => { d.open = true; });   // ô trong <details> đóng chưa có hộp thật
  document.querySelectorAll('input, select, textarea, summary, label').forEach((c) => {
    if (c.closest('[hidden]') || c.type === 'hidden') return;
    const cs = getComputedStyle(c);
    if (cs.visibility === 'hidden' || cs.display === 'none' || cs.pointerEvents === 'none') return;
    c.scrollIntoView({ block: 'center', inline: 'center' });
    const r = c.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) return;                                    // ô tự vẽ lại (ẩn thật): bỏ
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    if (cx < 0 || cy < 0 || cx > innerWidth || cy > innerHeight) return;
    const e = document.elementFromPoint(cx, cy);
    if (!e) return;
    const lab = c.matches('label') ? c : c.closest('label');
    const cua = e === c || c.contains(e) || (lab && (e === lab || lab.contains(e))) ||
      (c.labels && Array.from(c.labels).some((l) => l === e || l.contains(e)));
    if (cua) return;
    /* bị phần tử KHÁC che (không phải nút): hộp thoại / menu nổi hợp lệ, không thuộc lỗi này */
    if (!e.closest('button, .btn, [role=button]')) return;
    loi.push((c.id || c.name || c.className || c.tagName) + ' <- ' + (e.id || e.className || e.tagName));
  });
  return loi;
}"""


@pytest.fixture(params=["quan_tri", "giao_vien"])
def mo_vai(request, api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    base._nap_du_lieu(api)
    assert api.run_pipeline(seed=9)["ok"]            # có kết quả: thẻ Xuất hiện đủ các ô tick
    assert api.tao_tai_khoan("quantri", MK_THU, "quan_tri")["ok"]
    if request.param == "giao_vien":
        assert api.tao_tai_khoan("gv1", MK_THU, "giao_vien")["ok"]
        api.dang_xuat()
        assert api.dang_nhap("gv1", MK_THU)["ok"]
    with base.sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = base.browser_host.serve(api, GOC, "index.html", open_browser=False)
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1000}, bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        page.wait_for_function("document.body.dataset.vai !== undefined")
        yield page, request.param, loi
        br.close()


def test_nut_khong_cuop_cu_bam_cua_o_nhap(mo_vai):
    page, vai, loi = mo_vai
    thay = 0
    for the in CAC_THE:
        nut = page.locator('.nav-item[data-tab="%s"]' % the)
        if not nut.is_visible():
            continue
        nut.click()
        page.wait_for_timeout(400)
        thay += 1
        sai = page.evaluate(DO_O_NHAP)
        assert sai == [], (vai, the, sai)
    assert thay >= 4
    assert loi == [], loi


def test_bam_chuot_vao_o_tick_xuat_khong_kich_nut_xuat(mo_vai):
    """Đường người dùng thật: mở mục "nâng cao" bằng cú bấm vào summary, rồi bấm chuột vào từng ô tick."""
    page, vai, loi = mo_vai
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#xuatKemCsv", state="attached")
    page.evaluate("() => { window.__x = 0; document.getElementById('btnXuatTuyChon').addEventListener('click', () => { window.__x += 1; }); }")
    page.locator("#xuatNangCao > summary").click()
    for sel in ("#xuatKetQua", "#xuatKemCsv"):
        if not page.is_visible(sel) or page.eval_on_selector(sel, "e => e.disabled"):
            continue
        truoc = page.eval_on_selector(sel, "e => e.checked")
        page.mouse.click(*page.eval_on_selector(sel, "e => { e.scrollIntoView({ block: 'center' }); const b = e.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; }"))
        assert page.eval_on_selector(sel, "e => e.checked") != truoc, sel
    assert page.evaluate("() => window.__x") == 0


def test_o_nhap_sat_nut_van_nhan_cu_bam_vung_bam_khong_cuop(mo_vai):
    """Dựng đúng tình huống lỗi: nút hẹp (<44 px) có ô tick sát cạnh, tâm ô nằm trong phần vùng bấm ::after nới ra của nút."""
    page, vai, loi = mo_vai
    page.evaluate("""() => { const d = document.createElement('div');
      d.style.cssText = 'position:fixed;left:200px;top:200px;z-index:50;background:#fff;padding:20px';
      d.innerHTML = '<button id="ux2Btn" class="btn btn-nho btn-secondary" type="button" style="padding:5px 4px">x</button><input id="ux2Ck" type="checkbox" style="margin:0">';
      document.body.appendChild(d); window.__n = 0; document.getElementById('ux2Btn').addEventListener('click', () => { window.__n += 1; }); }""")
    page.mouse.click(*page.eval_on_selector("#ux2Ck", "e => { const b = e.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; }"))
    assert page.eval_on_selector("#ux2Ck", "e => e.checked") is True
    assert page.evaluate("() => window.__n") == 0
