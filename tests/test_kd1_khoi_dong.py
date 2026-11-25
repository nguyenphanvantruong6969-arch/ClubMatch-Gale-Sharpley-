"""KD1: Windows thieu WebView2 -> pywebview lang le dung MSHTML (IE11) -> giao dien khong chay.

Moi test dung module `webview` GIA; khong bao gio mo cua so that."""
import sys
import types

import pytest

import main


class _Api:
    pass


@pytest.fixture
def gia(monkeypatch, tmp_path):
    """Dung webview gia + ghi lai loi goi. `renderer` / `loi_nhap` chinh duoc tu test."""
    goi = {"start": 0, "serve": 0, "log": []}
    webview = types.ModuleType("webview")
    webview.create_window = lambda *a, **k: object()

    def start(*a, **k):
        goi["start"] += 1
    webview.start = start
    platforms = types.ModuleType("webview.platforms")
    winforms = types.ModuleType("webview.platforms.winforms")
    webview.platforms = platforms
    platforms.winforms = winforms
    monkeypatch.setitem(sys.modules, "webview", webview)
    monkeypatch.setitem(sys.modules, "webview.platforms", platforms)
    monkeypatch.setitem(sys.modules, "webview.platforms.winforms", winforms)

    def serve(*a, **k):
        goi["serve"] += 1
    monkeypatch.setattr(main.browser_host, "serve", serve)
    monkeypatch.setattr(main, "BASE_DIR", str(tmp_path))
    monkeypatch.setattr(main.chan_doan, "ghi",
                        lambda base, *dong, **k: goi["log"].extend(dong))
    monkeypatch.setattr(main.chan_doan, "ghi_ngoai_le", lambda *a, **k: None)
    goi["winforms"] = winforms
    goi["monkeypatch"] = monkeypatch
    return goi


def _chay():
    main._show_ui("t", "index.html", _Api(), 100, 100, (10, 10))


def test_mshtml_tren_win32_chuyen_sang_trinh_duyet(gia):
    gia["monkeypatch"].setattr(sys, "platform", "win32")
    gia["winforms"].renderer = "mshtml"
    _chay()
    assert gia["serve"] == 1 and gia["start"] == 0
    dong = [d for d in gia["log"] if "MSHTML" in d.upper()]
    assert len(dong) == 1 and "WebView2" in dong[0] and "Traceback" not in dong[0]


def test_edgechromium_van_dung_cua_so_goc(gia):
    gia["monkeypatch"].setattr(sys, "platform", "win32")
    gia["winforms"].renderer = "edgechromium"
    _chay()
    assert gia["start"] == 1 and gia["serve"] == 0


def test_nhap_winforms_loi_roi_ve_du_phong(gia):
    gia["monkeypatch"].setattr(sys, "platform", "win32")
    gia["monkeypatch"].setitem(sys.modules, "webview.platforms.winforms", None)  # import -> ImportError
    _chay()
    assert gia["serve"] == 1 and gia["start"] == 0


def test_khong_phai_windows_khong_nhap_winforms(gia):
    gia["monkeypatch"].setattr(sys, "platform", "linux")
    gia["monkeypatch"].setitem(sys.modules, "webview.platforms.winforms", None)  # neu nhap -> loi -> serve
    _chay()
    assert gia["start"] == 1 and gia["serve"] == 0
