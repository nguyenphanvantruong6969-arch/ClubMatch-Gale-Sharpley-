"""UX2-L8 (Playwright + Chromium): chuyển cảnh mượt (#10): hàng mới trượt vào, <details> mở theo chiều cao. Chỉ trang trí. Dữ liệu MÔ PHỎNG."""
import os
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser_host  # noqa: E402
import test_giao_dien_chay as base  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_giao_dien_chay import _cham  # noqa: E402

GOC = base.GOC
api = base.api

# Ghi lại, NGAY lúc hàng được gắn lớp ux2-vao, kiểu hoạt ảnh tính ra của nó.
GHI = """() => { window.__vao = []; new MutationObserver((ms) => ms.forEach((m) => {
    if (m.target.classList && m.target.classList.contains('ux2-vao') && m.target.nodeName === 'TR') {
      const s = getComputedStyle(m.target);
      window.__vao.push({ ten: s.animationName, dai: s.animationDuration, tre: s.animationDelay, pe: s.pointerEvents, skel: m.target.classList.contains('ux2-khung-hang') }); } }))
    .observe(document.body, { attributes: true, attributeFilter: ['class'], subtree: true }); }"""


def _them_hs(api, n):
    for i in range(n):
        api.create_student_if_missing("HS%04d" % i, "Học sinh %d" % i)


@pytest.fixture
def mo(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def _mo(reduced=False):
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        kw = {"reduced_motion": "reduce"} if reduced else {}
        page = br.new_page(locale="vi-VN", viewport={"width": 1400, "height": 1000}, bypass_csp=True, **kw)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        return page, loi

    yield _mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _vao_hs(page):
    page.locator('.nav-item[data-tab="admin"]').click()
    page.click("#qlTabHs")


def test_hang_moi_truot_vao_toi_da_20_hang_180ms_tong_khong_qua_200ms(api, mo):
    _them_hs(api, 30)
    page, loi = mo()
    page.evaluate(GHI)
    _vao_hs(page)
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr').length >= 30")
    page.wait_for_timeout(100)
    ghi = page.evaluate("() => window.__vao")
    assert len(ghi) == 20                                                     # đúng 20 hàng đầu, 10 hàng còn lại không
    assert {g["ten"] for g in ghi} == {"ux2Vao"} and {g["dai"] for g in ghi} == {"0.18s"}
    assert max(float(g["tre"].rstrip("s")) for g in ghi) * 1000 + 180 <= 200
    assert all(g["pe"] != "none" for g in ghi) and not any(g["skel"] for g in ghi)
    page.wait_for_timeout(500)
    assert page.evaluate("() => document.querySelectorAll('.ux2-vao').length") == 0          # dọn sạch sau khi xong
    assert loi == [], loi


def test_hang_bam_duoc_ngay_khi_dang_truot(api, mo):
    _them_hs(api, 5)
    page, loi = mo()
    _vao_hs(page)
    page.wait_for_selector("#adminStudentTableBody .admin-row-checkbox")
    hang = page.evaluate("""() => { const c = document.querySelector('#adminStudentTableBody .admin-row-checkbox'); const r = c.getBoundingClientRect();
        const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return [e === c, getComputedStyle(c.closest('tr')).pointerEvents]; }""")
    assert hang[0] is True and hang[1] != "none"
    page.click("#adminStudentTableBody .admin-row-checkbox")                  # bấm ngay, không chờ hoạt ảnh
    assert page.eval_on_selector("#adminStudentTableBody .admin-row-checkbox", "c => c.checked") is True


def test_khong_hang_nao_truot_khi_tat_hieu_ung(api, mo):
    _them_hs(api, 25)
    page, loi = mo()
    page.evaluate("() => document.documentElement.classList.add('tat-hieu-ung')")
    page.evaluate(GHI)
    _vao_hs(page)
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr').length >= 25")
    page.wait_for_timeout(300)
    assert page.evaluate("() => window.__vao") == []


def test_khong_hang_nao_truot_khi_giam_chuyen_dong(api, mo):
    _them_hs(api, 25)
    page, loi = mo(reduced=True)
    page.evaluate(GHI)
    _vao_hs(page)
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr').length >= 25")
    page.wait_for_timeout(300)
    assert page.evaluate("() => window.__vao") == []


def test_khung_cho_L7_khong_bi_gan_hieu_ung_truot(api, mo):
    _them_hs(api, 8)
    api.list_students_admin = _cham(api.list_students_admin, 1.4)
    page, loi = mo()
    page.evaluate(GHI)
    _vao_hs(page)
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody .ux2-khung-hang').length > 0", timeout=3000)
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr:not(.ux2-khung-hang)').length >= 8", timeout=15000)
    ghi = page.evaluate("() => window.__vao")
    assert len(ghi) == 8 and not any(g["skel"] for g in ghi)                  # chỉ hàng dữ liệu thật trượt, khung thì không


def _mo_nang_cao(page):
    page.locator('.nav-item[data-tab="others"]').click()
    page.wait_for_selector("#xuatNangCao > summary")
    page.click("#xuatNangCao > summary")


def test_details_nang_cao_mo_theo_chieu_cao_roi_tra_overflow_va_chu_doc_duoc(api, mo):
    page, loi = mo()
    ho_tro = page.evaluate("() => CSS.supports('selector(::details-content)')")
    _mo_nang_cao(page)
    ten = page.evaluate("() => getComputedStyle(document.getElementById('xuatNangCao'), '::details-content').animationName")
    if ho_tro:
        assert ten == "ux2Abre"                                                # đang chạy hoạt ảnh chiều cao
    page.wait_for_timeout(500)                                                 # xong hoạt ảnh
    st = page.evaluate("""() => { const d = document.getElementById('xuatNangCao'); const p = getComputedStyle(d, '::details-content');
        const lab = d.querySelector('#xuatKemCsv').closest('label'); const r = lab.getBoundingClientRect();
        const dc = d.querySelector('.xuat-tuy-chon') || d;
        return { ten: p.animationName, ovf: p.overflowY, lab: [Math.round(r.width), Math.round(r.height)], cat: lab.scrollWidth > lab.clientWidth + 1 || lab.scrollHeight > lab.clientHeight + 1,
                 nhin: lab.offsetParent !== null }; }""")
    assert st["ovf"] == "visible" and st["nhin"] and not st["cat"] and st["lab"][1] > 8        # overflow trả về, chữ không bị cắt
    page.evaluate("() => { const o = document.querySelector('#xuatNangCao input:not([disabled])'); window.__id = o.id || o.type; o.focus(); }")   # focus vào nội dung vừa mở vẫn được
    assert page.evaluate("() => document.activeElement.matches('#xuatNangCao input')") is True
    assert loi == [], loi


def test_details_khong_chuyen_dong_khi_tat_hieu_ung_va_giam_chuyen_dong(api, mo):
    page, loi = mo()
    page.evaluate("() => document.documentElement.classList.add('tat-hieu-ung')")
    _mo_nang_cao(page)
    assert page.evaluate("() => getComputedStyle(document.getElementById('xuatNangCao'), '::details-content').animationName") == "none"
    assert page.eval_on_selector("#xuatNangCao", "d => d.open") is True       # mở tức thì, nội dung có đó


def test_details_giam_chuyen_dong_mo_tuc_thi(api, mo):
    page, loi = mo(reduced=True)
    _mo_nang_cao(page)
    assert page.evaluate("() => getComputedStyle(document.getElementById('xuatNangCao'), '::details-content').animationName") == "none"
    assert page.is_visible("#xuatKemCsv")


def test_menu_khac_khong_bi_hoat_anh_chieu_cao_de_hop_nut_khong_bi_cat(api, mo):
    page, loi = mo()
    page.click("#menuThanhBen > summary")
    assert page.evaluate("() => getComputedStyle(document.getElementById('menuThanhBen'), '::details-content').animationName") == "none"
    assert page.eval_on_selector("#menuThanhBen", "d => d.open") is True


def test_css_chuyen_canh_nam_trong_supports_va_no_preference_de_lui_ve_tuc_thi():
    with open(os.path.join(GOC, "style.css"), encoding="utf-8") as f:
        css = f.read()
    import re
    i = css.index("/* UX2 — L8")
    khoi = css[i:]
    khoi = khoi[:khoi.index("/* UX4:")]     # chỉ khối L8: CSS các tính năng thêm sau (DK…) không thuộc phạm vi test này
    assert "@supports selector(::details-content)" in khoi
    assert "overflow" not in re.sub(r"/\*.*?\*/", "", khoi[khoi.index("@supports"):], flags=re.S)     # nội dung <details> KHÔNG bị cắt khi mở
    j = khoi.index("@supports")
    assert "prefers-reduced-motion: no-preference" in khoi[j:j + 200]
    khong_chu_thich = re.sub(r"/\*.*?\*/", "", khoi, flags=re.S)
    assert "::details-content" not in khong_chu_thich[:khong_chu_thich.index("@supports")]   # ngoài @supports không có gì động tới ::details-content
    assert ".menu-khac" not in khoi[j:]                                       # hộp nút trôi tuyệt đối không bị cắt


# ---------- FIX L8 vòng 1: chỉ hàng THẬT SỰ MỚI mới trượt vào; vẽ lại cùng dữ liệu thì bảng đứng yên ----------
def _vao_hs_xong(page, n):
    _vao_hs(page)
    page.wait_for_function("n => document.querySelectorAll('#adminStudentTableBody tr').length >= n", arg=n)
    page.wait_for_timeout(450)                                               # đợi hoạt ảnh lần đầu xong rồi mới xoá sổ ghi
    page.evaluate("() => { window.__vao = []; }")


def _so_vao(page):
    page.wait_for_timeout(350)
    return len(page.evaluate("() => window.__vao"))


def test_ve_lai_cung_du_lieu_khong_hang_nao_truot_tai_lai_sap_xep_doi_ngon_ngu_tim_kiem(api, mo):
    _them_hs(api, 25)
    page, loi = mo()
    page.evaluate(GHI)
    _vao_hs_xong(page, 25)
    page.evaluate("() => { loadAdminStudents(); }")                           # tải lại y nguyên
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr').length >= 25")
    assert _so_vao(page) == 0
    page.evaluate("() => { window.__vao = []; }")
    page.click("#adminHsThemTuyChon")   # UX4-L3
    page.select_option("#adminSapXep", index=1)                               # đổi thứ tự sắp
    page.wait_for_timeout(500)
    assert page.evaluate("() => document.querySelectorAll('#adminStudentTableBody tr').length") >= 25
    assert _so_vao(page) == 0
    page.evaluate("() => { window.__vao = []; window.I18N.setLang('en'); }")  # đổi ngôn ngữ (vẽ lại cả bảng)
    page.wait_for_timeout(600)
    assert _so_vao(page) == 0
    page.evaluate("() => { window.__vao = []; }")
    page.fill("#adminStudentSearch", "HS000")                                 # lọc: tập con của dữ liệu đã thấy
    page.wait_for_timeout(900)
    n_loc = page.evaluate("() => document.querySelectorAll('#adminStudentTableBody tr').length")
    assert 0 < n_loc < 25
    assert _so_vao(page) == 0
    page.evaluate("() => { window.__vao = []; }")
    page.fill("#adminStudentSearch", "")                                      # bỏ lọc: các hàng quay lại cũng KHÔNG trượt lại
    page.wait_for_function("n => document.querySelectorAll('#adminStudentTableBody tr').length >= n", arg=25)
    assert _so_vao(page) == 0
    assert loi == [], loi


def test_them_mot_hoc_sinh_dung_hang_do_truot_vao(api, mo):
    _them_hs(api, 12)
    page, loi = mo()
    page.evaluate(GHI)
    page.evaluate("""() => { window.__chu = []; new MutationObserver((ms) => ms.forEach((m) => { if (m.target.classList && m.target.classList.contains('ux2-vao')) window.__chu.push(m.target.textContent); }))
        .observe(document.body, { attributes: true, attributeFilter: ['class'], subtree: true }); }""")
    _vao_hs_xong(page, 12)
    page.evaluate("() => { window.__chu = []; }")
    api.create_student_if_missing("HS9999", "Em Mới Thêm")
    page.evaluate("() => { loadAdminStudents(); }")
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr').length >= 13")
    page.wait_for_timeout(300)
    assert len(page.evaluate("() => window.__vao")) == 1
    chu = page.evaluate("() => window.__chu")
    assert len(chu) == 1 and "HS9999" in chu[0]                              # đúng hàng vừa thêm
    assert loi == [], loi


def test_them_mot_clb_dung_hang_do_truot_vao_va_bang_rong_roi_co_du_lieu_la_lan_dau(api, mo):
    page, loi = mo()
    page.evaluate(GHI)
    page.locator('.nav-item[data-tab="admin"]').click()
    page.wait_for_selector("#adminClubEmptyState:not([hidden])")               # bảng CLB trống
    api.create_or_update_club("clb_x", "CLB X", 10, 0, "")
    page.evaluate("() => { loadAdminClubs(); }")
    page.wait_for_selector("#adminClubTableBody tr")
    page.wait_for_timeout(300)
    assert len(page.evaluate("() => window.__vao")) == 1                      # trống -> có 1 hàng: là lần đầu
    page.wait_for_timeout(400)
    page.evaluate("() => { window.__vao = []; loadAdminClubs(); }")
    page.wait_for_timeout(600)
    assert len(page.evaluate("() => window.__vao")) == 0                      # tải lại cùng dữ liệu: đứng yên
    api.create_or_update_club("clb_y", "CLB Y", 10, 0, "")
    page.evaluate("() => { window.__vao = []; loadAdminClubs(); }")
    page.wait_for_function("document.querySelectorAll('#adminClubTableBody tr').length >= 2")
    page.wait_for_timeout(300)
    assert len(page.evaluate("() => window.__vao")) == 1                      # thêm CLB Y: chỉ hàng Y
    assert loi == [], loi


def test_details_noi_dung_dai_khong_bi_cat_sau_khi_mo(api, mo):
    page, loi = mo()
    page.evaluate("""() => { const d = document.createElement('details'); d.className = 'nang-cao'; d.id = 'ux2Dai';
        d.innerHTML = '<summary>Dài</summary><div id="ux2DaiNd">' + Array.from({ length: 40 }, (_, i) => '<p>Dòng chữ dài số ' + i + ' để thử việc không bị cắt.</p>').join('') + '</div>';
        document.body.appendChild(d); }""")
    page.click("#ux2Dai > summary")
    page.wait_for_timeout(600)
    st = page.evaluate("""() => { const nd = document.getElementById('ux2DaiNd'); const d = document.getElementById('ux2Dai');
        const dc = getComputedStyle(d, '::details-content');
        return { sh: nd.scrollHeight, ch: nd.clientHeight, cao: nd.getBoundingClientRect().height, ovf: dc.overflowY, hdc: parseFloat(dc.height) || 0, ten: dc.animationName }; }""")
    assert st["sh"] == st["ch"] and st["ovf"] == "visible"                  # nội dung dài không bị cắt, overflow đã trả về visible
    assert abs(st["hdc"] - st["cao"]) <= 2 or st["hdc"] == 0                  # vùng nội dung cao đủ chứa hết chữ
    assert page.evaluate("() => { const r = document.querySelector('#ux2DaiNd p:last-child').getBoundingClientRect(); return r.height > 8 && r.bottom <= document.documentElement.scrollHeight + 2; }")
    assert loi == [], loi


def test_o_nhap_trong_hang_55px_khi_ve_lai_khong_co_hieu_ung_truot_de_len_o(api, mo):
    """Con trỏ / focus trong ô lớp của hàng 55 px: vẽ lại cùng dữ liệu KHÔNG gắn hiệu ứng trượt lên hàng đó (hàng bị dựng lại như
    hành vi cũ của bảng; L8 không được làm tệ thêm: không transform / opacity phủ lên ô vừa dựng lại)."""
    _them_hs(api, 6)
    page, loi = mo()
    page.evaluate(GHI)
    _vao_hs_xong(page, 6)
    assert page.eval_on_selector("#adminStudentTableBody tr", "r => r.offsetHeight") == 51      # TK1-L1: đệm ô 14→12 px (lưới 4 pt): hàng 55→51 px
    page.click("#adminStudentTableBody tr .lop-sua")
    page.keyboard.type("10A")
    page.evaluate("() => { loadAdminStudents(); }")
    page.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr').length >= 6")
    page.wait_for_timeout(350)
    assert len(page.evaluate("() => window.__vao")) == 0
    st = page.eval_on_selector("#adminStudentTableBody tr .lop-sua", "o => ({ op: getComputedStyle(o.closest('tr')).opacity, tf: getComputedStyle(o.closest('tr')).transform })")
    assert st == {"op": "1", "tf": "none"}
    assert loi == [], loi


def test_o_nhap_trong_details_bam_duoc_tu_khung_hinh_dau_tien_ca_khi_cpu_cham(api, mo):
    """FIX CI-1: hoạt ảnh mở KHÔNG được cắt nội dung (bản mở theo chiều cao làm ô nhập trượt hit-test trong ~30 ms đầu).
    Lấy mẫu elementFromPoint ngay từ khung hình đầu và mỗi 8 ms trong 400 ms, với CPU thường và CPU bị bóp 6 lần: ô LUÔN là phần tử trúng."""
    page, loi = mo()
    cdp = page.context.new_cdp_session(page)
    for ty_le in (1, 6):
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": ty_le})
        page.locator('.nav-item[data-tab="others"]').click()
        page.wait_for_selector("#xuatNangCao > summary")
        page.evaluate("() => { document.getElementById('xuatNangCao').open = false; }")
        page.wait_for_timeout(400)
        mau = page.evaluate("""() => new Promise((xong) => { const d = document.getElementById('xuatNangCao'); const c = document.getElementById('xuatKetQua'); const ra = [];
            const t0 = performance.now(); d.open = true;
            const doc = () => { const r = c.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
                ra.push(e === c || (e && e.closest('label') === c.closest('label'))); if (performance.now() - t0 < 400) setTimeout(doc, 8); else xong(ra); };
            doc(); })""")
        assert len(mau) > 10 and all(mau), (ty_le, mau.count(False), len(mau))
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 1})
    # bấm chuột THẬT vào ô (đang bật) NGAY sau khi mở: ô tick tự dựng trong một <details class="nang-cao"> (ô Xuất thật bị khoá khi chưa có kết quả)
    page.evaluate("""() => { const d = document.createElement('details'); d.className = 'nang-cao'; d.id = 'ux2Ck'; d.style.cssText = 'position:fixed;left:300px;top:300px;z-index:60;background:#fff;padding:8px';
        d.innerHTML = '<summary>Mở</summary><label><input type="checkbox" id="ux2CkO"> ô thử</label>'; document.body.appendChild(d); }""")
    page.click("#ux2Ck > summary")
    r = page.eval_on_selector("#ux2CkO", "e => { const b = e.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; }")
    page.mouse.click(r[0], r[1])                                              # không chờ hoạt ảnh
    assert page.eval_on_selector("#ux2CkO", "e => e.checked") is True
    assert loi == [], loi
