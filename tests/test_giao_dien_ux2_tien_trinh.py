"""UX2-L5 (Playwright + Chromium): 4 pha tiến trình, chỉ hiển thị. Dữ liệu MÔ PHỎNG."""
import json
import os
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_giao_dien_chay as base  # noqa: E402
from test_giao_dien_chay import _cham  # noqa: E402

api = base.api
mo_trang = base.mo_trang

TT = "() => Array.from(document.querySelectorAll('#ux2Pha li')).map((l) => l.dataset.trangThai)"
B = lambda s, st, **k: dict({"step": s, "status": st}, **k)  # noqa: E731


def _tinh(page, steps, ok):
    return page.evaluate("([s, ok]) => { const r = ux2TinhPha(s, ok); return [r.pha.map((p) => p.tt), r.hoanTac]; }", [steps, ok])


def test_tinh_pha_cac_tinh_huong_that_cua_run_pipeline(api, mo_trang):
    page, loi = mo_trang()
    xong = [B("backup", "done"), B("validate", "done"), B("stb_lottery", "done"), B("rbda_cascade", "done"),
            B("write_results", "done"), B("export", "done")]
    assert _tinh(page, xong, True) == [["xong"] * 4, False]
    # kiểm tra dữ liệu hỏng: pha 1 lỗi, 2-4 "chưa tới", chưa hoàn tác
    assert _tinh(page, [B("backup", "done"), B("validate", "running"), B("validate", "error", detail=[])], False) == \
        [["loi", "chua_den", "chua_den", "chua_den"], False]
    # lỗi ở bước xếp rồi hoàn tác: pha Xếp lỗi, Ghi KHÔNG hiện "xong" dù có bước rollback done
    s = [B("backup", "done"), B("validate", "done"), B("stb_lottery", "done"), B("rbda_cascade", "running"),
         B("rbda_cascade", "error"), B("rollback", "done")]
    assert _tinh(page, s, False) == [["xong", "loi", "chua_den", "chua_den"], True]
    # lỗi lạ giữa lúc ghi: write_results đang chạy -> unknown -> rollback: pha Ghi lỗi, Xuất chưa tới
    s = [B("backup", "done"), B("validate", "done"), B("stb_lottery", "done"), B("rbda_cascade", "done"),
         B("write_results", "running"), B("rollback", "done"), B("unknown", "error")]
    assert _tinh(page, s, False) == [["xong", "xong", "loi", "chua_den"], True]
    # lỗi lạ ngay đầu, không có bước nào: pha đầu lỗi, không im lặng
    assert _tinh(page, [], False) == [["loi", "chua_den", "chua_den", "chua_den"], False]
    assert _tinh(page, [B("backup", "done"), B("unknown", "error")], False)[0] == ["loi", "chua_den", "chua_den", "chua_den"]
    # xuất hỏng nhưng kết quả đã ghi (ok): chỉ pha Xuất lỗi, các pha trước vẫn xong
    s = xong[:-1] + [B("export", "error")]
    assert _tinh(page, s, True) == [["xong", "xong", "xong", "loi"], False]
    # sao lưu hỏng nhưng vẫn chạy (ok): pha Kiểm tra CẢNH BÁO, các pha sau vẫn xong
    s = [B("backup", "error"), B("validate", "done")] + xong[2:]
    assert _tinh(page, s, True) == [["canh_bao", "xong", "xong", "xong"], False]            # ok + sao lưu hỏng = CẢNH BÁO, không phải lỗi
    # CSDL bị giữ: sao lưu hỏng và chạy dừng ngay (ok = false) -> vẫn là LỖI
    assert _tinh(page, [B("backup", "error")], False)[0] == ["loi", "chua_den", "chua_den", "chua_den"]
    assert loi == [], loi


def test_dang_chay_ca_bon_pha_dang_roi_xong_va_stepper_van_thu_gon(api, mo_trang):
    api.run_pipeline = _cham(api.run_pipeline, 1.5)
    page, loi = mo_trang()
    assert page.evaluate(TT) == ["cho"] * 4
    page.click("#btnRun")
    page.wait_for_function("document.querySelector('#ux2Pha').getAttribute('aria-busy') === 'true'")
    assert page.evaluate(TT) == ["dang"] * 4
    assert page.eval_on_selector_all("#ux2Pha li[aria-current=step]", "l => l.length") == 4
    assert all(x.strip() == "Đang chạy…" for x in page.eval_on_selector_all("#ux2Pha .ux2-pha-tt", "l => l.map(e => e.textContent)"))
    assert page.eval_on_selector("#btnRun", "b => b.getAttribute('aria-busy')") == "true"           # dùng chung khoá btnRun (L1)
    page.wait_for_function("!document.querySelector('#runXong').hidden", timeout=20000)
    assert page.evaluate(TT) == ["xong"] * 4
    assert page.eval_on_selector_all("#ux2Pha li[aria-current]", "l => l.length") == 0
    assert page.eval_on_selector("#stepper", "s => s.hidden") is True                              # T3-06 thu gọn vẫn đúng
    page.click("#btnChiTietBuoc")
    assert page.eval_on_selector("#stepper", "s => s.hidden") is False
    assert page.eval_on_selector("#ux2Pha", "h => h.getAttribute('aria-busy')") == "false"
    assert loi == [], loi


def test_loi_kiem_tra_that_pha_1_loi_2_den_4_chua_toi_va_stepper_giu_nguyen(api, mo_trang):
    page, loi = mo_trang()
    steps = [B("backup", "done"), B("validate", "running"), B("validate", "error", detail={"code": "no_students", "params": {}})]
    page.evaluate("""(steps) => { const g = window.pywebview.api; window.pywebview = { api: new Proxy({}, { has: () => true,
        get: (_t, n) => (n === 'run_pipeline' ? () => Promise.resolve({ ok: false, errors: [{ code: 'no_students', params: {} }], data: { steps } }) : g[n]) }) }; }""", steps)
    page.click("#btnRun")
    page.wait_for_function("document.querySelector('#ux2Pha').getAttribute('aria-busy') === 'false' && document.querySelector('#ux2Pha li').dataset.trangThai === 'loi'", timeout=15000)
    assert page.evaluate(TT) == ["loi", "chua_den", "chua_den", "chua_den"]
    assert page.eval_on_selector("#stepper", "s => s.hidden") is False                            # lỗi: giữ danh sách bước
    assert page.eval_on_selector('#stepper [data-step="validate"]', "l => l.dataset.status") == "error"
    assert page.eval_on_selector("#ux2PhaGhiChu", "p => p.hidden") is True
    # rollback: dòng ghi chú "đã hoàn tác" (cùng câu pipeline_rolled_back), pha Ghi KHÔNG xong
    s2 = [B("backup", "done"), B("validate", "done"), B("stb_lottery", "done"), B("rbda_cascade", "running"),
          B("rbda_cascade", "error", detail={"code": "x", "params": {}}), B("rollback", "done", detail={"code": "pipeline_rolled_back", "params": {}})]
    page.evaluate("(s) => ux2DatPha('xong', s, false)", s2)
    assert page.evaluate(TT) == ["xong", "loi", "chua_den", "chua_den"]
    assert page.eval_on_selector("#ux2PhaGhiChu", "p => !p.hidden && p.textContent.length > 5") is True
    assert loi == [], loi


def test_doi_ngon_ngu_chu_pha_va_trang_thai_theo_ngon_ngu_moi(api, mo_trang):
    page, loi = mo_trang()
    page.evaluate("(s) => ux2DatPha('xong', s, false)", [B("backup", "done"), B("validate", "error")])
    vi = page.eval_on_selector_all("#ux2Pha li", "l => l.map(e => e.textContent.replace(/\\s+/g, ' ').trim())")
    page.evaluate("() => window.I18N.setLang('en')")
    en = page.eval_on_selector_all("#ux2Pha li", "l => l.map(e => e.textContent.replace(/\\s+/g, ' ').trim())")
    assert vi[0].endswith("Lỗi") and en[0] == "Check Error" and en[1] == "Allocate Not reached"
    assert page.evaluate(TT) == ["loi", "chua_den", "chua_den", "chua_den"]             # trạng thái giữ nguyên, chỉ chữ đổi
    assert json.dumps(vi) != json.dumps(en)
    assert loi == [], loi


def test_pha_khong_dung_chuyen_dong_de_mang_nghia(api, mo_trang):
    """Nghĩa nằm ở chữ + aria-current: tắt hiệu ứng thì chấm đứng yên nhưng chữ "Đang chạy…" vẫn có."""
    page, _ = mo_trang()
    page.evaluate("() => { document.documentElement.classList.add('tat-hieu-ung'); ux2DatPha('dang'); }")
    assert page.eval_on_selector('#ux2Pha li[data-pha="xep"] .ux2-pha-dot', "e => getComputedStyle(e).animationName") == "none"
    assert page.eval_on_selector('#ux2Pha li[data-pha="xep"] .ux2-pha-tt', "e => e.textContent.trim()") == "Đang chạy…"


def test_sao_luu_hong_nhung_chay_van_thanh_cong_hien_canh_bao_va_chi_tiet(api, mo_trang):
    page, loi = mo_trang()
    steps = [B("backup", "error", detail={"code": "db_backup_failed", "params": {"detail": "dia day"}}), B("validate", "done"),
             B("stb_lottery", "done"), B("rbda_cascade", "done"), B("write_results", "done"), B("export", "done")]
    page.evaluate("(s) => ux2DatPha('xong', s, true)", steps)
    assert page.evaluate(TT) == ["canh_bao", "xong", "xong", "xong"]
    assert page.eval_on_selector('#ux2Pha li[data-pha="kiem_tra"] .ux2-pha-tt', "e => e.textContent.trim()") == "Cảnh báo"
    chu = page.eval_on_selector("#ux2PhaGhiChu", "p => (p.hidden ? '' : p.textContent)")
    assert "dia day" in chu or len(chu) > 5                                                  # chi tiết bước sao lưu hiện ở dòng ghi chú
    mau = page.eval_on_selector('#ux2Pha li[data-pha="kiem_tra"]', "l => getComputedStyle(l).borderTopColor")
    mau_loi = page.evaluate("() => { ux2DatPha('xong', [B1], false); return getComputedStyle(document.querySelector('#ux2Pha li[data-pha=kiem_tra]')).borderTopColor; }".replace("B1", '{step: "backup", status: "error"}'))
    assert mau != mau_loi                                                                    # khác màu với lỗi (không đỏ)
    page.evaluate("() => window.I18N.setLang('en')")
    assert page.eval_on_selector('#ux2Pha li[data-pha="kiem_tra"] .ux2-pha-tt', "e => e.textContent.trim()") == "Error"   # (đang ở trạng thái lỗi vừa dựng)
    page.evaluate("(s) => ux2DatPha('xong', s, true)", steps)
    assert page.eval_on_selector('#ux2Pha li[data-pha="kiem_tra"] .ux2-pha-tt', "e => e.textContent.trim()") == "Warning"
    assert loi == [], loi


def test_xung_nhip_khong_chay_khi_tat_hieu_ung_va_khi_giam_chuyen_dong(api, mo_trang):
    page, _ = mo_trang()
    page.evaluate("() => ux2DatPha('dang')")
    sel = '#ux2Pha li[data-pha="xep"] .ux2-pha-dot'
    assert page.eval_on_selector(sel, "e => getComputedStyle(e).animationName") == "ux2PhaNhap"
    page.evaluate("() => document.documentElement.classList.add('tat-hieu-ung')")
    assert page.eval_on_selector(sel, "e => getComputedStyle(e).animationName") == "none"


def test_xung_nhip_khong_chay_khi_reduced_motion(api):
    from playwright.sync_api import sync_playwright
    import browser_host
    from _trinh_duyet import CHROMIUM
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, base.GOC, "index.html", open_browser=False)
        page = br.new_page(bypass_csp=True, reduced_motion="reduce")
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        page.evaluate("() => ux2DatPha('dang')")
        assert page.eval_on_selector('#ux2Pha li[data-pha="xep"] .ux2-pha-dot', "e => getComputedStyle(e).animationName") == "none"
        assert page.eval_on_selector('#ux2Pha li[data-pha="xep"] .ux2-pha-tt', "e => e.textContent.trim()") == "Đang chạy…"
        br.close()


def test_giao_vien_khong_thay_the_van_hanh_nen_khong_co_pha_va_nut_chay(api):
    """Thẻ Vận hành (có 4 pha + nút Chạy) là việc của quản trị: giao_vien không thấy cả hai (khớp data-quyen của nav-item)."""
    from playwright.sync_api import sync_playwright
    import browser_host
    from _trinh_duyet import CHROMIUM
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    assert api.tao_tai_khoan("quantri", "matkhau-gia-1", "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", "matkhau-gia-1", "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("gv1", "matkhau-gia-1")["ok"]
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        url = browser_host.serve(api, base.GOC, "index.html", open_browser=False)
        page = br.new_page(bypass_csp=True)
        page.goto(url)
        page.wait_for_selector("#dropZone", state="attached")
        page.wait_for_function("document.body.dataset.vai === 'giao_vien'")
        assert page.is_visible('.nav-item[data-tab="pipeline"]') is False
        assert page.is_visible("#ux2Pha") is False and page.is_visible("#btnRun") is False
        br.close()
