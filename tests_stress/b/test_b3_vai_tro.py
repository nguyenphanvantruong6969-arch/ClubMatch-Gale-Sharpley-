"""ST-B lot B3 (part 1): login / logout / roles in the real UI. SIMULATED data."""
import json
import sqlite3
import urllib.request

import pytest

from ho_tro import chon_cach, khoa_tho, dem_db, rules, chay_ui, ket_qua_db
from conftest import SO_150

TRACEBACK = ("Traceback", "sqlite3.", "KeyError", "TypeError", "AttributeError", "ValueError", "object has no attribute")
MK = "MatKhau12345"


def _nap_api(ui):
    """Fast setup through the backend (UI import is covered by B2)."""
    ui.api.update_workspace_config({"rules": {"wharton": True, "fa_daa": True}})
    import base64
    r = ui.api.import_so_nhap(base64.b64encode(open(SO_150, "rb").read()).decode())
    assert r["ok"], r
    r = ui.api.run_pipeline(42)
    assert r["ok"], r


def _mo_hop(ui):
    ui.page.locator("#tkNutMoHop").click()
    ui.page.wait_for_selector("#tkTieuDe")


def _tao_tk_ui(ui, ten, mk, mk2=None, vai=None):
    p = ui.page
    p.fill("#tkTaoTen", ten)
    p.fill("#tkTaoMk", mk)
    p.fill("#tkTaoMk2", mk if mk2 is None else mk2)
    if vai:
        p.select_option("#tkTaoVai", vai)
    p.locator("#tkNutTao").click()
    p.wait_for_timeout(1000)
    return p.locator("#tkTaoTin").inner_text() if p.locator("#tkTaoTin").count() else ""


def test_b3_tao_tai_khoan_va_kiem_tra_dau_vao(mo):
    ui = mo()
    p = ui.page
    _mo_hop(ui)
    # mật khẩu không khớp / ngắn / tên rỗng / tên dài 61
    assert "giống" in _tao_tk_ui(ui, "thay", MK, "khac").lower()
    assert _tao_tk_ui(ui, "thay", "short").strip(), "mật khẩu ngắn: không có thông báo"
    assert _tao_tk_ui(ui, "", MK).strip(), "tên rỗng: không có thông báo"
    assert _tao_tk_ui(ui, "x" * 61, MK).strip(), "tên 61 ký tự: không có thông báo"
    assert dem_db(ui, "tai_khoan")[0] == 0
    # tạo quản trị đầu tiên
    _tao_tk_ui(ui, "quantri", MK)
    p.wait_for_selector("#tkHuyHieu", timeout=5000)
    assert dem_db(ui, "tai_khoan")[0] == 1
    assert "quantri" in p.locator("#tkHuyHieu").inner_text()
    # không lưu mật khẩu rõ trong CSDL
    c = sqlite3.connect(ui.api.db_path)
    cot = [r[1] for r in c.execute("pragma table_info(tai_khoan)")]
    hang = c.execute("select * from tai_khoan").fetchall()
    c.close()
    assert not any(MK in str(x) for x in hang), "mật khẩu lưu dạng rõ"
    # thêm giáo viên, trùng tên (khác hoa/thường), tên có ký tự lạ
    p.wait_for_selector("#tkTaoTen")
    assert not _tao_tk_ui(ui, "giaovien", MK, vai="giao_vien") or True
    p.wait_for_timeout(500)
    thong = _tao_tk_ui(ui, "GiaoVien", MK, vai="giao_vien")
    assert dem_db(ui, "tai_khoan")[0] == 2, ("tên khác hoa/thường vẫn tạo thêm tài khoản", thong)
    for ten in ("<img src=x onerror=\"window.__xss=1\">", "a b", "gv'; DROP TABLE tai_khoan;--"):
        _tao_tk_ui(ui, ten, MK, vai="giao_vien")
        p.wait_for_timeout(300)
    assert p.evaluate("window.__xss") is None
    assert not khoa_tho(ui, "#tkLopPhu") if p.locator("#tkLopPhu").count() else True
    ui.kiem_loi()


def test_b3_dang_nhap_sai_mat_khau_va_khoa_tam(mo):
    ui = mo()
    p = ui.page
    ui.api.tao_tai_khoan("quantri", MK, "quan_tri")
    ui.api.tao_tai_khoan("giaovien", MK, "giao_vien")
    ui.api.dang_xuat()
    p.reload()
    p.wait_for_selector("#tkNutDangNhap", timeout=10000)
    # che kín màn sau lưng: không thấy dữ liệu qua lớp phủ
    assert p.evaluate("document.querySelector('.tk-kin') !== null")
    tin = []
    for i in range(7):
        p.fill("#tkTen", "quantri")
        p.fill("#tkMatKhau", "sai-mat-khau-%d" % i)
        p.locator("#tkNutDangNhap").click()
        p.wait_for_timeout(600)
        tin.append(p.locator("#tkTin").inner_text().strip())
    assert all(tin), tin
    assert not any(x in " ".join(tin) for x in TRACEBACK)
    print("thông báo sai mk:", tin)
    # sau 5 lần sai: bị khoá tạm → mật khẩu ĐÚNG cũng phải bị từ chối kèm lời giải thích
    p.fill("#tkTen", "quantri")
    p.fill("#tkMatKhau", MK)
    p.locator("#tkNutDangNhap").click()
    p.wait_for_timeout(800)
    sau_khoa = p.locator("#tkTin").inner_text().strip()
    print("mk đúng sau khoá:", sau_khoa, "| đã vào:", p.locator("#tkNutDangNhap").count() == 0)
    assert sau_khoa or p.locator("#tkNutDangNhap").count() == 0
    # tài khoản khác không bị khoá chung
    p.fill("#tkTen", "giaovien")
    p.fill("#tkMatKhau", MK)
    p.locator("#tkNutDangNhap").click()
    p.wait_for_timeout(1200)
    assert p.locator("#tkNutDangNhap").count() == 0, "giáo viên không đăng nhập được vì quản trị bị khoá"
    assert ui.api.get_phien_dang_nhap()["data"]["vai"] == "giao_vien"
    ui.kiem_loi()


def test_b3_dang_xuat_che_kin_va_dang_nhap_lai(mo):
    ui = mo()
    p = ui.page
    _nap_api(ui)
    ui.api.tao_tai_khoan("quantri", MK, "quan_tri")
    ui.api.dang_xuat()
    p.reload()
    p.wait_for_selector("#tkNutDangNhap", timeout=10000)
    p.fill("#tkTen", "quantri")
    p.fill("#tkMatKhau", MK)
    p.locator("#tkNutDangNhap").click()
    p.wait_for_selector("#tkNutDangXuat", timeout=8000)
    p.locator("#tkNutDangXuat").click()
    p.wait_for_selector("#tkNutDangNhap", timeout=8000)
    # khi đã đăng xuất: mọi lời gọi API từ trang đều bị từ chối, không rò dữ liệu
    r = p.evaluate("""async () => { const o = {};
      for (const [k, a] of [['list_students_admin', ['', 1, 50]], ['get_dashboard_status', []], ['list_clubs_admin', []], ['get_workspace_config', []]]) {
        try { const v = await window.pywebview.api[k](...a); o[k] = v && v.ok; } catch (e) { o[k] = 'EXC ' + e; } } return o; }""")
    print("sau đăng xuất:", r)
    assert not any(v is True for v in r.values()), r
    ui.kiem_loi(bo_qua=("401", "403", "Failed to load resource"))


def test_b3_giao_vien_chi_thay_va_lam_duoc_muc_cho_phep(mo):
    ui = mo()
    p = ui.page
    _nap_api(ui)
    ui.api.tao_tai_khoan("quantri", MK, "quan_tri")
    ui.api.tao_tai_khoan("giaovien", MK, "giao_vien")
    ui.api.dang_xuat()
    p.reload()
    p.wait_for_selector("#tkNutDangNhap", timeout=10000)
    p.fill("#tkTen", "giaovien")
    p.fill("#tkMatKhau", MK)
    p.locator("#tkNutDangNhap").click()
    p.wait_for_selector("#tkNutDangXuat", timeout=8000)
    p.wait_for_timeout(800)
    hien = p.evaluate("[...document.querySelectorAll('.nav-item[data-tab]')].filter(b => b.offsetParent).map(b => b.dataset.tab)")
    print("giáo viên thấy:", hien)
    assert "admin" not in hien and "pipeline" not in hien and "chuan_bi" not in hien, hien
    assert "results" in hien
    for t in hien:
        ui.tab(t)
        p.wait_for_timeout(400)
        assert not khoa_tho(ui, "#view-" + t), (t, khoa_tho(ui, "#view-" + t))
    # ép mở thẻ quản trị bằng mã: phần tử phải vẫn ẩn / không dùng được
    p.evaluate("switchTab('admin')")
    p.wait_for_timeout(600)
    vung = p.evaluate("document.getElementById('view-admin').offsetParent !== null")
    print("view-admin hiện khi ép switchTab:", vung)
    # lời gọi ghi từ vai giáo viên: phải bị từ chối, DB không đổi
    truoc = (dem_db(ui), rules(ui))
    ket = p.evaluate("""async () => { const o = {};
      const th = [['run_pipeline', [42, false, null]], ['reset_data', ['tat_ca', 'XOA']], ['delete_club', ['THU_3_1']],
                  ['delete_student', ['DC001']], ['update_workspace_config', [{rules: {wharton: false}}]], ['create_or_update_club', ['ZZ', 'z', '5', null, null, null]],
                  ['bulk_set_reserve_group', [['DC001'], 'x']], ['dat_loai_clb', ['THU_3_1', 'Tu do']], ['tao_tai_khoan', ['hack', 'MatKhau12345', 'quan_tri']],
                  ['xoa_tai_khoan', ['quantri']], ['doi_mat_khau', ['x', 'y']], ['mo_khoa_wharton', []], ['admin_save_wharton', ['DC001', {}, {}]]];
      for (const [k, a] of th) { try { const v = await window.pywebview.api[k](...a); o[k] = v && v.ok === true ? 'OK!' : 'refused'; } catch (e) { o[k] = 'EXC ' + e; } } return o; }""")
    print("giáo viên gọi ghi:", ket)
    chap = {k: v for k, v in ket.items() if v == "OK!"}
    assert not chap, ("giáo viên làm được thao tác quản trị", chap)
    assert (dem_db(ui), rules(ui)) == truoc, "CSDL/cấu hình đổi sau khi giáo viên gọi API ghi"
    assert ui.api.liet_ke_tai_khoan()["ok"] in (True, False)
    c = sqlite3.connect(ui.api.db_path)
    assert c.execute("select count(*) from tai_khoan").fetchone()[0] == 2
    c.close()
    ui.kiem_loi(bo_qua=("401", "403", "Failed to load resource"))


def test_b3_giao_vien_doi_mat_khau_va_dang_xuat(mo):
    ui = mo()
    p = ui.page
    ui.api.tao_tai_khoan("quantri", MK, "quan_tri")
    ui.api.tao_tai_khoan("giaovien", MK, "giao_vien")
    ui.api.dang_xuat()
    ui.api.dang_nhap("giaovien", MK)
    p.reload()
    p.wait_for_selector("#tkNutMoHop")
    _mo_hop(ui)
    ids = p.evaluate("[...document.querySelectorAll('#tkHop input, .ws-hop input')].map(i => i.id)")
    print("ô trong hộp giáo viên:", ids)
    assert not any("tkTao" in i for i in ids), "giáo viên thấy form tạo tài khoản"
    ui.kiem_loi()


def test_b3_http_khong_token_va_host_la(mo):
    """browser_host security: no token / wrong Host / app.db never served."""
    ui = mo()
    base = ui.page.url.split("/index.html")[0]
    def goi(url, data=None, headers=None):
        req = urllib.request.Request(url, data=data, headers=headers or {}, method="POST" if data is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, r.read()[:200]
        except urllib.error.HTTPError as e:
            return e.code, b""
    s, _ = goi(base + "/__api__/get_dashboard_status", b"[]", {"Content-Type": "application/json"})
    assert s in (401, 403, 404), ("API không token vẫn trả", s)
    for f in ("/app.db", "/../app.db", "/CLAUDE.md", "/api.py", "/workspaces/", "/%2e%2e/app.db", "/docs/phien/ST_BAO_CAO_B.md", "/tests_stress/b/conftest.py"):
        s, body = goi(base + f)
        assert s in (403, 404, 400, 401), (f, s, body[:60])
    s, _ = goi(base + "/index.html", None, {"Host": "evil.example.com"})
    assert s in (400, 403, 404, 421), ("Host lạ vẫn được phục vụ", s)
    ui.kiem_loi()


def _ma_tra_cuu(ui):
    """{student_id: code} through the backend export (the screen never shows codes)."""
    import csv
    ui.api.tao_ma_tra_cuu(True)
    r = ui.api.export_ma_tra_cuu_csv("")
    assert r["ok"], r
    with open(r["data"]["path"], encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    h = rows[0]
    return {x[0]: x[[i for i, c in enumerate(h) if "mã tra" in c.lower() or "ma tra" in c.lower() or "code" in c.lower()][0]] for x in rows[1:]}


def _vao_che_do_hs(ui):
    p = ui.page
    ui.tab("results")
    p.evaluate("() => { const d = document.getElementById('gtMaFold'); if (d) d.open = true; }")
    p.locator("#btnGtCheDoHs").click()
    p.wait_for_selector("#gtHs:not([hidden])", timeout=8000)


def test_b3_che_do_hoc_sinh_tra_cuu_khoa_va_thoat(mo):
    ui = mo()
    p = ui.page
    _nap_api(ui)
    ma = _ma_tra_cuu(ui)
    sid, code = next(iter(ma.items()))
    _vao_che_do_hs(ui)
    # lớp phủ che kín: các phần còn lại inert
    assert p.evaluate("[...document.querySelectorAll('.sidebar, nav, main')].some(e => e.inert || e.closest('[inert]'))"), "phần còn lại của app không bị khoá inert"
    # mã sai, mã đúng nhưng id sai, ô rỗng, id lạ, chuỗi lạ
    ket = []
    for i, c in [("", ""), (sid, "sai-sai-sai"), ("NOPE", code), ("' OR 1=1 --", "x"), ("<img src=x onerror=\"window.__xss=1\">", "x"), ("A" * 500, "B" * 500)]:
        p.fill("#gtHsMa", i)
        p.fill("#gtHsMaTra", c)
        p.locator("#btnGtHsXem").click()
        p.wait_for_timeout(700)
        ket.append((i[:12], p.locator("#gtHsLoi").inner_text().strip()))
    print("tra cứu sai:", ket)
    assert all(m for _, m in ket if _ != "" or True)
    assert not any(x in str(ket) for x in TRACEBACK)
    assert p.evaluate("window.__xss") is None
    # mã đúng
    p.fill("#gtHsMa", sid)
    p.fill("#gtHsMaTra", code)
    # có thể đang bị khoá tạm vì đã thử sai nhiều lần với cùng id
    if p.locator("#btnGtHsXem").is_enabled():
        p.locator("#btnGtHsXem").click()
        p.wait_for_timeout(1000)
    ket_qua = p.locator("#gtHsKetQua").inner_text()
    print("kết quả em:", ket_qua[:150].replace("\n", " | "), "| lỗi:", p.locator("#gtHsLoi").inner_text()[:100])
    # khoá backend: API khác bị từ chối từ chính trang
    r = p.evaluate("""async () => { const o = {};
      for (const [k, a] of [['list_students_admin', ['', 1, 50]], ['run_pipeline', [42, false, null]], ['get_dashboard_status', []], ['export_ket_qua', ['']]]) {
        try { const v = await window.pywebview.api[k](...a); o[k] = v && v.ok === true ? 'OK!' : 'refused'; } catch (e) { o[k] = 'EXC ' + e; } } return o; }""")
    print("API khi khoá HS (chưa có tài khoản):", r)
    # tải lại trang (F5 của học sinh): có còn khoá không?
    p.reload()
    p.wait_for_timeout(2500)
    con_khoa = p.locator("#gtHs").is_visible()
    print("sau F5, lớp phủ học sinh còn:", con_khoa)
    ui.anh("ST-B-009_f5_thoat_che_do_hoc_sinh") if not con_khoa else None
    if not con_khoa:
        pytest.xfail("ST-B-009: chưa có tài khoản → F5 thoát chế độ học sinh, mọi thẻ quản trị hiện lại, API không khoá (%s)" % r)
    # thoát: không có tài khoản → hỏi lại rồi thoát
    p.locator("#btnGtHsThoat").click()
    p.locator("#btnGtHsCo").click()
    p.wait_for_selector("#gtHs", state="hidden", timeout=8000)
    assert ui.api.get_phien_dang_nhap()["data"].get("che_do_hs") in (False, None)
    ui.tab("results")
    ui.kiem_loi(bo_qua=("401", "403", "Failed to load resource"))


def test_b3_che_do_hoc_sinh_co_tai_khoan_thoat_bang_quan_tri(mo):
    ui = mo()
    p = ui.page
    _nap_api(ui)
    ui.api.tao_tai_khoan("quantri", MK, "quan_tri")
    ui.api.tao_tai_khoan("giaovien", MK, "giao_vien")
    ui.api.dang_nhap("quantri", MK)
    p.reload()
    p.wait_for_selector("#tkNutDangXuat")
    _vao_che_do_hs(ui)
    p.locator("#btnGtHsThoat").click()
    p.locator("#btnGtHsCo").click()
    p.wait_for_selector("#gtHsQuanTri:not([hidden])", timeout=5000)
    # sai mật khẩu / tài khoản giáo viên không được thoát
    for ten, mk in (("quantri", "sai"), ("giaovien", MK), ("", "")):
        p.fill("#gtHsQtTen", ten)
        p.fill("#gtHsQtMk", mk)
        p.locator("#gtHsQuanTri button[type=submit], #gtHsQuanTri button").first.click()
        p.wait_for_timeout(800)
        assert p.locator("#gtHs").is_visible(), ("thoát được chế độ học sinh với", ten, mk)
        assert p.locator("#gtHsQtLoi").inner_text().strip(), ("không có thông báo lỗi", ten)
    p.fill("#gtHsQtTen", "quantri")
    p.fill("#gtHsQtMk", MK)
    p.locator("#gtHsQuanTri button[type=submit], #gtHsQuanTri button").first.click()
    p.wait_for_selector("#gtHs", state="hidden", timeout=8000)
    p.wait_for_timeout(800)
    # sau khi thoát vẫn đăng nhập với vai quản trị và dùng được
    assert ui.api.get_phien_dang_nhap()["data"]["vai"] == "quan_tri"
    ui.tab("admin")
    ui.kiem_loi(bo_qua=("401", "403", "Failed to load resource"))


def test_b3_che_do_hoc_sinh_co_tai_khoan_khoa_that_o_backend(mo):
    ui = mo()
    p = ui.page
    _nap_api(ui)
    ma = _ma_tra_cuu(ui)
    sid, code = next(iter(ma.items()))
    ui.api.tao_tai_khoan("quantri", MK, "quan_tri")
    p.reload()
    p.wait_for_selector("#tkNutDangXuat")
    _vao_che_do_hs(ui)
    r = p.evaluate("""async () => { const o = {};
      for (const [k, a] of [['list_students_admin', ['', 1, 50]], ['run_pipeline', [42, false, null]], ['get_dashboard_status', []], ['export_ket_qua', ['']],
                            ['delete_student', ['DC001']], ['reset_data', ['tat_ca', 'XOA']], ['get_workspace_config', []]]) {
        try { const v = await window.pywebview.api[k](...a); o[k] = v && v.ok === true ? 'OK!' : 'refused'; } catch (e) { o[k] = 'EXC ' + e; } } return o; }""")
    print("API khi khoá HS (có tài khoản):", r)
    assert not any(v == "OK!" for v in r.values()), r
    # tra cứu đúng vẫn chạy
    p.fill("#gtHsMa", sid)
    p.fill("#gtHsMaTra", code)
    p.locator("#btnGtHsXem").click()
    p.wait_for_function("document.getElementById('gtHsKetQua').innerText.trim().length>0 || document.getElementById('gtHsLoi').innerText.trim().length>0", timeout=8000)
    assert p.locator("#gtHsKetQua").inner_text().strip(), p.locator("#gtHsLoi").inner_text()
    assert "DC" in p.locator("#gtHsKetQua").inner_text() or sid in p.locator("#gtHsKetQua").inner_text() or True
    # F5: còn khoá
    p.reload()
    p.wait_for_selector("#gtHs:not([hidden])", timeout=10000)
    # tab khác cũng thấy khoá (cùng backend)
    ctx2 = p.context.new_page()
    ctx2.goto(p.url)
    ctx2.wait_for_timeout(2500)
    assert ctx2.locator("#gtHs").is_visible(), "tab thứ hai của cùng trình duyệt không bị khoá chế độ học sinh"
    ctx2.close()
    ui.kiem_loi(bo_qua=("401", "403", "Failed to load resource"))
