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


# ---------------------------------------------------------------- L2: moc thoi gian khoi dong
import re  # noqa: E402


def _ms(dong):
    m = re.search(r"\+(\d+) ms", dong)
    return int(m.group(1)) if m else None


def test_log_co_ten_renderer_va_moc_truoc_webview_start(gia):
    gia["monkeypatch"].setattr(sys, "platform", "win32")
    gia["winforms"].renderer = "edgechromium"
    _chay()
    log = "\n".join(gia["log"])
    assert "renderer edgechromium" in log
    moc = [d for d in gia["log"] if "truoc webview.start" in d]
    assert len(moc) == 1 and _ms(moc[0]) is not None


def test_log_moc_truoc_browser_host_khi_mshtml(gia):
    gia["monkeypatch"].setattr(sys, "platform", "win32")
    gia["winforms"].renderer = "mshtml"
    _chay()
    moc = [d for d in gia["log"] if "truoc browser_host.serve" in d]
    assert len(moc) == 1 and _ms(moc[0]) is not None


def test_main_ghi_moc_bat_dau_va_workspace_da_mo(gia):
    mp = gia["monkeypatch"]
    mp.setattr(main, "resolve_db_path", lambda: "x.db")
    mp.setattr(main, "khoi_dong_workspace", lambda: ("x.db", "goc", True))
    mp.setattr(main, "PipelineAPI", lambda *a, **k: _Api())
    mp.setattr(main, "tieu_de_cua_so", lambda *a: "t")
    mp.setattr(main, "_show_ui", lambda *a, **k: None)
    main.main()
    moc = [d for d in gia["log"] if "moc main bat dau" in d or "moc workspace da mo" in d]
    assert len(moc) == 2 and all(_ms(d) is not None for d in moc)
    assert _ms(moc[0]) <= _ms(moc[1])


def test_ghi_moc_khong_nem_loi_khi_khong_ghi_duoc_tep(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "BASE_DIR", str(tmp_path / "khong_co_thu_muc" / "sau"))
    main._ghi_moc("x")  # chan_doan.ghi nuot loi; khong duoc nem
