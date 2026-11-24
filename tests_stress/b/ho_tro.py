"""ST-B helpers shared by all lots (UI actions + backend cross-checks). SIMULATED data."""
import sqlite3

from conftest import SO_150

CACH = {"chi_xep": "ux1aChiXep", "chia_100": "ux1aChia100", "huy_chuong": "ux1aHuyChuong"}


def _trong_menu_them(page, sel):
    return page.locator(sel).evaluate("e => !!e.closest('#qlThemMenu')")


def mo_menu_them(page):
    """UX4-L2: tab Điểm quyết tâm, Điểm chuẩn, Bảng điểm, Dữ liệu nằm trong menu "Thêm ▾" (#qlNutThem); mở nếu đang đóng."""
    nut = page.locator("#qlNutThem")
    if nut.get_attribute("aria-expanded") != "true":
        nut.click()


def tab_ql_hien(page, sel):
    """Tab con của Quản lý có đang hiện không (mở menu "Thêm ▾" trước nếu tab nằm trong đó)?"""
    if _trong_menu_them(page, sel):
        mo_menu_them(page)
    return page.locator(sel).is_visible()


def clic_tab_ql(page, sel):
    if _trong_menu_them(page, sel):
        mo_menu_them(page)
    page.locator(sel).click()


def mo_the_che_do(page):
    """UX4-L4: ba thẻ chế độ nằm ở tab Cách xếp, trong mục gập "Tuỳ chỉnh thêm" (#ux1aNangCao); mở ra nếu đang gập."""
    page.locator("#qlTabCachXep").click()
    page.wait_for_selector("#ux1aNangCao > summary", state="visible")
    if page.locator("#ux1aNangCao").get_attribute("open") is None:
        page.locator("#ux1aNangCao > summary").click()


def chon_cach(ui, ma, cho=True):
    """Click a mode card on Cài đặt (view admin). Waits for the card to be checked."""
    p = ui.page
    ui.tab("admin")
    mo_the_che_do(p)
    p.wait_for_selector("#ux1a" + {"chi_xep": "ChiXep", "chia_100": "Chia100", "huy_chuong": "HuyChuong"}[ma], state="visible")
    nut = p.locator("#" + CACH[ma])
    if nut.get_attribute("aria-checked") != "true":
        nut.click()
        if cho:
            p.wait_for_function("id => document.getElementById(id).getAttribute('aria-checked')==='true'", arg=CACH[ma])
            p.wait_for_timeout(250)


def rules(ui):
    return ui.api.get_workspace_config()["data"]["config"]["rules"]


def nap_so_150(ui, cho_hs=150):
    p = ui.page
    ui.tab("pipeline")
    p.set_input_files("#fileAny", SO_150)
    p.wait_for_selector("#btnImportAll", state="visible")
    p.locator("#btnImportAll").click()
    p.wait_for_function("n => document.querySelector('#statStudents').textContent===String(n)", arg=cho_hs, timeout=30000)


def so_dong_run(ui):
    c = sqlite3.connect(ui.api.db_path)
    try:
        return c.execute("select count(*) from run_history").fetchone()[0]
    finally:
        c.close()


def chay_ui(ui, timeout=90000):
    """Click #btnRun on the pipeline tab (confirming overwrite if asked). Returns 'ok' | 'loi'."""
    p = ui.page
    ui.tab("pipeline")
    truoc = so_dong_run(ui)
    p.wait_for_function("!document.getElementById('btnRun').disabled", timeout=timeout)
    p.locator("#btnRun").click()
    try:
        p.wait_for_selector("#runConfirmBar", timeout=3000)
        p.locator("#runConfirmBar .btn-primary").click()
    except Exception:
        pass
    p.wait_for_function(
        "() => !document.getElementById('btnRun').disabled && (!document.getElementById('runXong').hidden"
        " || document.querySelector('#logBox') && document.querySelector('#logPanel') && !document.getElementById('logPanel').hidden)",
        timeout=timeout)
    ok = not p.locator("#runXong").is_hidden()
    return "ok" if ok else "loi", so_dong_run(ui) - truoc


def ket_qua_db(ui):
    """{student_id: set(club name)} of the newest run, from the DB."""
    c = sqlite3.connect(ui.api.db_path)
    try:
        ten = dict(c.execute("select club_id, name from clubs").fetchall())
        out = {}
        for sid, cid in c.execute("select student_id, club_id from match_results"):
            out.setdefault(sid, set())
            if cid:
                out[sid].add(ten.get(cid, cid))
        return out
    finally:
        c.close()


def ket_qua_ui(ui, mong_doi=None, cho_giay=8.0):
    """{student_id: set(club name)} read from the Results tab table. If `mong_doi` (the DB dict) is given, polls until
    the table matches it or `cho_giay` passes (a stale table that later heals is reported via ui.cu_roi_lanh)."""
    import time
    p = ui.page
    ui.tab("results")
    t0 = time.time()
    out = _doc_bang(ui)
    if mong_doi is not None and out != mong_doi:
        while time.time() - t0 < cho_giay and out != mong_doi:
            p.wait_for_timeout(200)
            out = _doc_bang(ui)
        if out == mong_doi:
            ui.cu_roi_lanh = getattr(ui, "cu_roi_lanh", []) + [round(time.time() - t0, 2)]
    return out


def _doc_bang(ui):
    p = ui.page
    p.wait_for_function("document.querySelectorAll('#kqThan tr:not(.ux2-khung-hang)').length>0 || !document.getElementById('kqRong').hidden", timeout=30000)
    rows = p.evaluate("""() => [...document.querySelectorAll('#kqThan tr:not(.ux2-khung-hang)')].map(tr => {
        const td=[...tr.querySelectorAll('td')]; return [td[0].innerText.trim(), td.slice(2).map(x=>x.innerText.trim())]; })""")
    out = {}
    for sid, cells in rows:
        out[sid] = {c for c in cells[1:] if c and c not in ("—", "-")} if False else {c for c in cells if c and c not in ("—", "-")}
    return out


import re

_KHOA_THO = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+){2,}\b|\bundefined\b|\[object Object\]|\bNaN\b")


def khoa_tho(ui, vung="body"):
    """Raw i18n keys / undefined / NaN visible in the (visible) text of `vung`."""
    txt = ui.page.evaluate("s => document.querySelector(s).innerText", vung)
    return sorted(set(_KHOA_THO.findall(txt)))


def dem_db(ui, *bang):
    c = sqlite3.connect(ui.api.db_path)
    try:
        return tuple(c.execute("select count(*) from %s" % b).fetchone()[0] for b in (bang or ("students", "clubs", "preferences", "club_test_selection", "club_scores")))
    finally:
        c.close()


def dat_tep(ui, ten, noi_dung):
    """Drop one in-memory file on the Xếp CLB drop zone; returns the queue text after the preview settles."""
    p = ui.page
    ui.tab("pipeline")
    if p.locator("#btnClearQueue").is_visible():
        p.locator("#btnClearQueue").click()
    p.set_input_files("#fileAny", files=[{"name": ten, "mimeType": "application/octet-stream", "buffer": noi_dung}])
    p.wait_for_function("document.querySelector('#importQueue').innerText.trim().length>0", timeout=60000)
    p.wait_for_timeout(1200)
    return p.locator("#importQueue").inner_text() + "\n" + p.locator("#importWarnings").inner_text()


def nap_tep(ui, ten, noi_dung, cho=3000):
    """dat_tep + click 'import' when offered. Returns (preview_text, imported: bool)."""
    p = ui.page
    txt = dat_tep(ui, ten, noi_dung)
    if p.locator("#btnImportAll").is_visible() and p.locator("#btnImportAll").is_enabled():
        p.locator("#btnImportAll").click()
        p.wait_for_timeout(cho)
        return txt, True
    return txt, False
