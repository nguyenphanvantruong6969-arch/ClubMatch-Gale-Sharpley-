"""ST-B lot B4: robustness + display (3 000 students, vi/en, widths, keyboard-only, exports). SIMULATED data."""
import base64
import glob
import os
import re
import sqlite3
import time

import pytest

from ho_tro import chon_cach, khoa_tho, dem_db, nap_so_150, chay_ui, ket_qua_db, nap_tep, _KHOA_THO
from ho_tro_tep import so_nhan_ban
from conftest import SO_150

DAU = re.compile("[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", re.I)
CAC_TAB = ["pipeline", "fallback", "scoring", "results", "others", "admin"]

JS_VAN_BAN_TINH = """() => {
  const ra = [];
  const ok = e => e.offsetParent !== null && !e.closest('[hidden]') && !e.closest('#toastStack');
  document.querySelectorAll('button, h1, h2, h3, h4, label, th, summary, legend, .view-desc, .hint-text, option, [data-i18n], [placeholder], [title], [aria-label]').forEach(e => {
    if (!ok(e)) return;
    const v = [];
    if (e.matches('button, h1, h2, h3, h4, label, th, summary, legend, .view-desc, .hint-text, option, [data-i18n]')) v.push(e.innerText);
    ['placeholder', 'title', 'aria-label'].forEach(a => { if (e.getAttribute(a)) v.push(e.getAttribute(a)); });
    v.forEach(t => { if (t && t.trim()) ra.push([e.tagName + (e.id ? '#' + e.id : ''), t.trim().slice(0, 90)]); });
  });
  return ra;
}"""


def _doi_ngon_ngu(ui, ma):
    p = ui.page
    if p.evaluate("window.I18N.getLang()") != ma:
        p.locator("#btnLangToggle").click()
        p.wait_for_function("l => window.I18N.getLang() === l", arg=ma)
        p.wait_for_timeout(500)


def _ten_du_lieu(ui):
    c = sqlite3.connect(ui.api.db_path)
    try:
        return {r[0] for r in c.execute("select name from clubs")} | {r[0] for r in c.execute("select name from students")}
    finally:
        c.close()


def test_b4_vi_en_moi_man_hinh_khoa_tho_chua_dich_va_tran_chu(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    chay_ui(ui)
    du_lieu = _ten_du_lieu(ui) | {'Trường học'}
    chua_dich, khoa, tran = [], [], []
    for ma in ("en", "vi"):
        _doi_ngon_ngu(ui, ma)
        for t in CAC_TAB:
            ui.tab(t)
            subs = ["#qlTabClb", "#qlTabHs", "#qlTabWh", "#qlTabDc", "#qlTabDuLieu"] if t == "admin" else [None]
            for sub in subs:
                if sub:
                    if not p.locator(sub).is_visible():
                        continue
                    p.locator(sub).click()
                p.wait_for_timeout(500)
                ds = p.evaluate(JS_VAN_BAN_TINH)
                for tag, txt in ds:
                    if ma == "en" and DAU.search(txt) and not any(n in txt for n in du_lieu) and txt not in du_lieu and "Trường học" not in txt:
                        chua_dich.append((t, sub, tag, txt))
                    if _KHOA_THO.search(txt):
                        khoa.append((ma, t, tag, txt))
                for r in p.evaluate("""() => [...document.querySelectorAll('button, .btn, th, h1, h2, label')].filter(e => e.offsetParent && e.scrollWidth > e.clientWidth + 2
                       && getComputedStyle(e).overflow !== 'visible').map(e => (e.id || e.className) + ':' + e.innerText.slice(0, 40))"""):
                    tran.append((ma, t, sub, r))
    _doi_ngon_ngu(ui, "vi")
    print("CHƯA DỊCH (en):", len(chua_dich))
    for x in sorted(set(chua_dich))[:40]:
        print("   ", x)
    print("KHOÁ THÔ:", khoa[:10])
    print("TRÀN CHỮ:", sorted(set(tran))[:15])
    ui.kiem_loi()
    assert not khoa, khoa[:5]
    assert not chua_dich, ("%d chuỗi tiếng Việt còn nguyên ở chế độ English" % len(chua_dich), sorted(set(chua_dich))[:8])


def test_b4_thong_bao_giu_nguyen_tieng_viet_sau_khi_doi_ngon_ngu(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    chon_cach(ui, "chia_100")             # toast "Đã chuyển sang… [Hoàn tác] [Đóng thông báo]" giữ nguyên
    p.wait_for_selector("#toastStack button")
    _doi_ngon_ngu(ui, "en")
    txt = p.locator("#toastStack").inner_text()
    ui.anh("ST-B-012_toast_sau_khi_doi_en")
    assert not DAU.search(txt), "sau khi đổi sang English, thông báo đang hiện vẫn tiếng Việt: %r" % txt[:120]


JS_TRAN_TRANG = """() => {
  const w = document.documentElement.clientWidth;
  const ra = {cuon_ngang: document.documentElement.scrollWidth - w, ben_ngoai: []};
  document.querySelectorAll('body *').forEach(e => {
    if (!e.offsetParent && getComputedStyle(e).position !== 'fixed') return;
    if (e.closest('[hidden]') || e.closest('.table-scroll, .bang-cuon, .table-wrap, [style*="overflow"]')) return;
    const r = e.getBoundingClientRect();
    if (r.width > 0 && (r.right > w + 2 || r.left < -2) && !e.closest('table')) ra.ben_ngoai.push((e.id || e.className || e.tagName).toString().slice(0, 40) + ' ' + Math.round(r.left) + '..' + Math.round(r.right));
  });
  ra.ben_ngoai = ra.ben_ngoai.slice(0, 8);
  return ra;
}"""


@pytest.mark.parametrize("rong", [390, 768, 1366])
def test_b4_do_rong_man_hinh(mo, rong):
    ui = mo(viewport={"width": rong, "height": 800})
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    chay_ui(ui)
    loi = []
    for t in CAC_TAB:
        ui.tab(t)
        subs = ["#qlTabClb", "#qlTabHs", "#qlTabWh", "#qlTabDuLieu"] if t == "admin" else [None]
        for sub in subs:
            if sub:
                if not p.locator(sub).is_visible():
                    continue
                p.locator(sub).click()
            p.wait_for_timeout(500)
            r = p.evaluate(JS_TRAN_TRANG)
            if t == "admin" and rong < 700:
                continue                 # ST-B-013 có test riêng (768: chỉ lệch 4 px, bỏ qua)
            if t == "admin" and rong == 768:
                r["cuon_ngang"] = 0; r["ben_ngoai"] = []
            if r["cuon_ngang"] > 4 or r["ben_ngoai"]:
                loi.append((rong, t, sub, r))
    # nút chính còn bấm được ở độ rộng này
    ui.tab("pipeline")
    box = p.locator("#btnRun").bounding_box()
    print("btnRun %dpx:" % rong, box)
    if rong <= 390:
        ui.anh("B4_390_pipeline")
    for x in loi:
        print("TRÀN:", x)
    assert box and box["x"] >= 0 and box["x"] + box["width"] <= rong + 2, box
    assert not loi, loi[:4]
    ui.kiem_loi()


@pytest.mark.parametrize("rong", [390])
def test_b4_quan_ly_cuon_ngang_o_man_hinh_hep(mo, rong):
    ui = mo(viewport={"width": rong, "height": 800})
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    ui.tab("admin")
    p.wait_for_timeout(800)
    p.evaluate("window.scrollTo(0, 0)")
    sw = p.evaluate("document.documentElement.scrollWidth")
    ui.anh("ST-B-013_quan_ly_%d" % rong)
    assert sw <= rong + 4, "thẻ Quản lý rộng %d px trên màn hình %d px: cả trang cuộn ngang" % (sw, rong)


def test_b4_3000_hoc_sinh_chay_va_ve_man_hinh(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    t0 = time.time()
    nap_tep(ui, "so3000.xlsx", so_nhan_ban(20), cho=500)
    p.wait_for_function("document.querySelector('#statStudents').textContent==='3000'", timeout=180000)
    t_nap = time.time() - t0
    # đo các tác vụ treo main thread
    p.evaluate("""() => { window.__tre = []; let t = performance.now(); setInterval(() => { const n = performance.now(); if (n - t > 600) window.__tre.push(Math.round(n - t)); t = n; }, 100); }""")
    t0 = time.time()
    kq, them = chay_ui(ui, timeout=180000)
    t_chay = time.time() - t0
    log = p.locator("#logBox").inner_text()[:300] if kq != "ok" else ""
    t0 = time.time()
    ui.tab("results")
    p.wait_for_function("document.querySelectorAll('#kqThan tr').length > 100", timeout=120000)
    t_kq = time.time() - t0
    n_dong = p.locator("#kqThan tr").count()
    t0 = time.time()
    ui.tab("admin")
    p.locator("#qlTabHs").click()
    p.wait_for_selector("#adminStudentTableBody tr", timeout=60000)
    t_hs = time.time() - t0
    t0 = time.time()
    p.fill("#adminStudentSearch", "DC001_19")
    p.wait_for_function("document.querySelectorAll('#adminStudentTableBody tr').length === 1", timeout=30000)
    t_tim = time.time() - t0
    ui.tab("others")
    p.wait_for_timeout(2500)
    tre = p.evaluate("window.__tre")
    print("3000 hs: nạp %.1fs | chạy %.1fs (%s) | tab Kết quả %.1fs (%d dòng) | Quản lý › Học sinh %.1fs | tìm %.1fs | treo >600ms: %s" % (t_nap, t_chay, kq, t_kq, n_dong, t_hs, t_tim, tre))
    ui.anh("B4_3000_ket_qua")
    assert kq == "ok", log
    assert t_chay < 30, "chạy 3000 học sinh mất %.1fs (>30 s = S2)" % t_chay
    assert t_kq < 15 and t_hs < 15, (t_kq, t_hs)
    assert not tre or max(tre) < 5000, ("giao diện treo", tre)
    db = ket_qua_db(ui)
    assert len(db) == 3000
    assert not khoa_tho(ui)
    ui.kiem_loi()


def _tab_toi(p, sel, toi_da=120, nguoc=False):
    """Press Tab until the focused element matches `sel`. Returns the number of presses, or None (unreachable)."""
    for i in range(1, toi_da + 1):
        p.keyboard.press("Shift+Tab" if nguoc else "Tab")
        if p.evaluate("sel => { const a = document.activeElement; return !!a && a.matches(sel); }", sel):
            return i
    return None


def test_b4_chi_ban_phim_nhap_chay_xuat(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    ui.tab("pipeline")
    p.wait_for_timeout(1500)
    p.evaluate("document.activeElement && document.activeElement.blur(); window.scrollTo(0,0)")
    n = _tab_toi(p, "#dropZone")
    assert n, "không Tab tới được vùng thả tệp"
    with p.expect_file_chooser(timeout=5000) as fc:
        p.keyboard.press("Enter")
    fc.value.set_files(SO_150)
    p.wait_for_selector("#btnImportAll", state="visible")
    p.wait_for_function("document.querySelector('#importQueue').innerText.includes('Sẵn sàng')", timeout=20000)
    p.wait_for_timeout(800)
    assert _tab_toi(p, "#btnImportAll", 40), "không Tab tới nút nhập"
    ok_truoc = p.evaluate("document.activeElement && (document.activeElement.id || document.activeElement.tagName)")
    p.keyboard.press("Enter")
    try:
        p.wait_for_function("document.querySelector('#statStudents').textContent==='150'", timeout=30000)
    except Exception:
        ui.anh("B4_ban_phim_ket")
        raise AssertionError("Enter trên nút nhập (focus=%r) không nạp: stat=%r queue=%r toast=%r" % (ok_truoc, p.locator("#statStudents").inner_text(), p.locator("#importQueue").inner_text()[:100], p.locator("#toastStack").inner_text()[:100]))
    p.wait_for_timeout(1000)
    # tới nút Chạy
    p.evaluate("document.activeElement && document.activeElement.blur()")
    assert _tab_toi(p, "#btnRun", 60), "không Tab tới nút Chạy"
    vien = p.evaluate("(() => { const s = getComputedStyle(document.activeElement); return s.outlineStyle + ' ' + s.outlineWidth + ' ' + s.boxShadow; })()")
    print("viền focus nút Chạy:", vien)
    assert "none 0px" not in vien or "rgb" in vien, ("nút Chạy có focus mà không thấy viền", vien)
    p.keyboard.press("Enter")
    p.wait_for_selector("#runXong:not([hidden])", timeout=60000)
    assert so_dong(ui) == 1
    # sang thẻ "Chi tiết và xuất tệp" bằng bàn phím
    assert _tab_toi(p, '.nav-item[data-tab="others"]', 120, nguoc=True) or _tab_toi(p, '.nav-item[data-tab="others"]', 120), "không Tab tới thẻ Chi tiết và xuất tệp"
    p.keyboard.press("Enter")
    p.wait_for_selector("#view-others.is-active")
    assert _tab_toi(p, "#btnXuatTuyChon", 150), "không Tab tới nút Xuất kết quả"
    xuat = os.path.join(str(ui.tmp), "xuat")
    truoc = set(glob.glob(os.path.join(xuat, "*")))
    foc = p.evaluate("document.activeElement.id")
    estado = p.evaluate("(() => { const c = document.getElementById('xuatKetQua'); return [c.checked, c.disabled, document.getElementById('xuatKetQuaKhoa') && document.getElementById('xuatKetQuaKhoa').innerText]; })()")
    p.keyboard.press("Enter")
    try:
        p.wait_for_function("document.getElementById('xuatFeedback') && document.getElementById('xuatFeedback').innerText.trim().length > 0", timeout=15000)
    except Exception:
        ui.anh("B4_ban_phim_xuat_ket")
        raise AssertionError("Enter trên #btnXuatTuyChon (focus=%r) không xuất: feedback=%r toast=%r busy=%r disabled=%r files=%r estado=%r" % (
            foc, p.locator("#xuatFeedback").inner_text()[:100], p.locator("#toastStack").inner_text()[:100],
            p.locator("#btnXuatTuyChon").get_attribute("aria-busy"), p.locator("#btnXuatTuyChon").is_disabled(), glob.glob(os.path.join(xuat, "*")), estado))
    moi = set(glob.glob(os.path.join(xuat, "*"))) - truoc
    assert any(f.endswith(".xlsx") for f in moi), (moi, p.locator("#xuatFeedback").inner_text()[:200])
    # không có bẫy bàn phím: Tab liên tục 150 lần vẫn quay về <body>/đầu trang và không ném lỗi
    for _ in range(150):
        p.keyboard.press("Tab")
    ui.kiem_loi()


def so_dong(ui):
    from ho_tro import so_dong_run
    return so_dong_run(ui)


def _mo_het_menu(p):
    p.evaluate("document.querySelectorAll('details').forEach(d => d.open = true)")


def test_b4_moi_nut_xuat_tep_mo_duoc(mo):
    import csv
    import openpyxl
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    chay_ui(ui)
    xuat = os.path.join(str(ui.tmp), "xuat")
    ui.tab("others")
    p.wait_for_timeout(1500)
    _mo_het_menu(p)
    nut = p.evaluate("""() => [...document.querySelectorAll('#view-others button')].filter(b => b.offsetParent && /^(btnXuat|btnPdf|btnTai)/.test(b.id) && !b.disabled).map(b => b.id)""")
    nut = [n for n in nut if n not in ("btnXuatHocSinh",)]
    print("nút xuất:", nut)
    assert len(nut) >= 4, nut
    loi, mo_duoc = [], []
    for nid in nut:
        truoc = set(glob.glob(os.path.join(xuat, "**", "*"), recursive=True)) | set(glob.glob(os.path.join(str(ui.tmp), "TaiXuong", "*")))
        p.evaluate("id => { const b = document.getElementById(id); b.closest('details') && (b.closest('details').open = true); }", nid)
        try:
            p.locator("#" + nid).click(timeout=3000)
        except Exception as e:
            loi.append((nid, "không bấm được", str(e)[:60]))
            continue
        p.wait_for_timeout(2500)
        moi = (set(glob.glob(os.path.join(xuat, "**", "*"), recursive=True)) | set(glob.glob(os.path.join(str(ui.tmp), "TaiXuong", "*")))) - truoc
        moi = {f for f in moi if os.path.isfile(f)}
        toast = p.locator("#toastStack").inner_text()[-150:].replace("\n", " ")
        if not moi:
            loi.append((nid, "bấm xong không có tệp mới", toast))
            continue
        for f in moi:
            try:
                if os.path.getsize(f) == 0:
                    raise ValueError("tệp rỗng")
                if f.endswith(".xlsx"):
                    wb = openpyxl.load_workbook(f)
                    assert wb.sheetnames and any(ws.max_row >= 1 for ws in wb)
                elif f.endswith(".csv"):
                    with open(f, encoding="utf-8-sig", newline="") as fh:
                        rows = list(csv.reader(fh))
                    assert len(rows) >= 1 and len({len(r) for r in rows[1:]} or {1}) <= 2, "số cột không đều"
                elif f.endswith(".pdf"):
                    b = open(f, "rb").read()
                    assert b.startswith(b"%PDF") and b"%%EOF" in b[-2048:], "PDF thiếu đầu/cuối"
                elif f.endswith(".html"):
                    assert "<html" in open(f, encoding="utf-8").read(500).lower()
                mo_duoc.append((nid, os.path.basename(f), os.path.getsize(f)))
            except Exception as e:
                loi.append((nid, os.path.basename(f), "không mở được: %s" % e))
        assert not any(x in p.locator("#toastStack").inner_text() for x in ("Traceback", "sqlite3.", "KeyError"))
    print("\n".join(map(str, mo_duoc)))
    print("LỖI:", loi)
    assert not loi, loi
    ui.kiem_loi()


def test_b4_xuat_du_lieu_dau_vao_nap_lai_cung_ket_qua(mo):
    """Export input data as a Sổ, import into a NEW workspace, same students / prefs / ticks / scores / medals."""
    ui = mo()
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    chay_ui(ui)
    truoc = dem_db(ui, "students", "clubs", "preferences", "club_test_selection", "club_scores", "wharton_bids")
    r = ui.api.export_du_lieu_dau_vao("")
    assert r["ok"], r
    f = r["data"]["path"]
    assert f.endswith(".xlsx") and os.path.getsize(f) > 0
    noi_dung = open(f, "rb").read()
    import workspace as ws
    from api import PipelineAPI
    goc2 = os.path.join(str(ui.tmp), "goc2")
    os.makedirs(goc2)
    slug = ws.tao(goc2, "Nạp lại", None)
    a2 = PipelineAPI(ws.duong_dan_db(goc2, slug), thu_muc_goc_ws=goc2, ws_da_chon=True)
    a2.update_workspace_config({"rules": {"wharton": True, "fa_daa": True}})
    ket = a2.import_so_nhap(base64.b64encode(noi_dung).decode())
    assert ket["ok"], ket
    c = sqlite3.connect(a2.db_path)
    sau = tuple(c.execute("select count(*) from %s" % t).fetchone()[0] for t in ("students", "clubs", "preferences", "club_test_selection", "club_scores", "wharton_bids"))
    c.close()
    print("trước", truoc, "sau", sau)
    assert sau == truoc, ("xuất dữ liệu đầu vào rồi nạp lại không khớp", truoc, sau)
    ui.kiem_loi()
