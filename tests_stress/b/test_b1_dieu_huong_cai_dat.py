"""ST-B lot B1: navigation + Cài đặt (mode cards, chia_loai, double-click, reload during run, back/forward).
Chromium thật qua browser_host. SIMULATED data. Mỗi test kết thúc bằng ui.kiem_loi()."""
import random

import pytest

from conftest import SO_150
from ho_tro import chon_cach, rules, nap_so_150, chay_ui, so_dong_run, ket_qua_db, ket_qua_ui, khoa_tho, _doc_bang, clic_tab_ql


def test_b1_moi_tab_va_tab_con(mo):
    ui = mo()
    p = ui.page
    tabs = p.evaluate("[...document.querySelectorAll('.nav-item[data-tab]')].filter(b=>!b.hidden).map(b=>b.dataset.tab)")
    assert {"pipeline", "fallback", "scoring", "results", "others", "admin"} <= set(tabs), tabs
    for _ in range(2):
        for t in tabs:
            ui.tab(t)
            p.wait_for_timeout(150)
    ui.tab("admin")
    subs = p.evaluate("[...document.querySelectorAll('#qlTabs [data-ql-tab]')].filter(b=>!b.hidden).map(b=>b.id)")
    assert len(subs) >= 3
    for s in subs * 2:
        clic_tab_ql(p, "#" + s)
        p.wait_for_timeout(120)
        assert p.locator("#" + s).get_attribute("aria-selected") == "true"
    # nhóm thanh bên (nút nhóm): bấm không được làm hỏng điều hướng
    for n in p.locator(".nav-nhom-nut").all():
        n.click()
        p.wait_for_timeout(100)
    ui.tab("pipeline")
    ui.kiem_loi()


def test_b1_tab_khi_chua_co_du_lieu_va_co_du_lieu(mo):
    ui = mo()
    p = ui.page
    for t in ("results", "others", "fallback", "scoring", "admin"):
        ui.tab(t)
        txt = p.locator("#view-" + t).inner_text()
        assert "undefined" not in txt and "[object" not in txt and "NaN" not in txt, (t, txt[:200])
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    for t in ("results", "others", "fallback", "scoring", "admin", "pipeline"):
        ui.tab(t)
        txt = p.locator("#view-" + t).inner_text()
        assert "undefined" not in txt and "[object" not in txt and "NaN" not in txt, (t, txt[:200])
    ui.kiem_loi()


@pytest.mark.parametrize("hat", [20261123])
def test_b1_doi_che_do_50_lan(mo, hat):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    rng = random.Random(hat)
    vet = []
    for i in range(50):
        ma = rng.choice(["chi_xep", "chia_100", "huy_chuong"])
        chon_cach(ui, ma)
        r = rules(ui)
        assert not khoa_tho(ui), (i, ma, "khoá i18n thô/undefined ở Cài đặt", khoa_tho(ui))
        assert (r["wharton"], r["fa_daa"]) == {"chi_xep": (False, False), "chia_100": (True, False), "huy_chuong": (True, True)}[ma], (i, ma, r)
        if ma != "huy_chuong" and rng.random() < 0.5:
            ui.tab("admin")
            p.locator("#qlTabClb").click()
            p.wait_for_selector("#mt2CongTac", state="attached")
            cb = p.locator("#mt2CongTac")
            if cb.is_visible() and cb.is_enabled():
                cb.click()
                p.wait_for_timeout(500)
                assert rules(ui)["chia_loai"] == cb.is_checked(), (i, "chia_loai UI/backend lệch")
        kq, them = chay_ui(ui)
        vet.append((i, ma, rules(ui).get("chia_loai"), kq, them))
        assert them == (1 if kq == "ok" else 0), vet[-1]
        assert kq == "ok", ("run lỗi sau đổi chế độ", vet[-1], p.locator("#logBox").inner_text()[:400])
        db = ket_qua_db(ui)
        giao = ket_qua_ui(ui, db)
        assert db == giao, ("Kết quả UI lệch backend", vet[-1], [k for k in db if db[k] != giao.get(k)][:5])
        ui.tab("pipeline")
        assert not khoa_tho(ui), (i, ma, "khoá thô ở trang Xếp CLB", khoa_tho(ui))
        stat = int(p.locator("#statMatched").inner_text())
        assert stat == sum(1 for v in db.values() if v), (vet[-1], stat)
    print("BANG_CU_ROI_LANH(s):", getattr(ui, "cu_roi_lanh", []))
    ui.kiem_loi()


def test_b1_bam_dup_nut_chinh(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    ui.tab("pipeline")
    # Chạy lần đầu: bấm đúp = đúng MỘT lần chạy
    p.locator("#btnRun").dblclick()
    p.wait_for_selector("#runXong:not([hidden])", timeout=60000)
    assert so_dong_run(ui) == 1
    # Chạy lần hai (có kết quả cũ): bấm đúp nút Chạy rồi bấm đúp nút xác nhận
    p.locator("#btnRun").dblclick()
    p.wait_for_selector("#runConfirmBar")
    p.locator("#runConfirmBar .btn-primary").dblclick()
    p.wait_for_function("!document.getElementById('btnRun').disabled", timeout=60000)
    p.wait_for_timeout(500)
    assert so_dong_run(ui) == 2, so_dong_run(ui)
    # Thẻ chế độ: bấm đúp
    ui.tab("admin")
    for ma in ("chia_100", "chi_xep", "huy_chuong"):
        p.locator("#" + {"chia_100": "ux1aChia100", "chi_xep": "ux1aChiXep", "huy_chuong": "ux1aHuyChuong"}[ma]).dblclick()
        p.wait_for_timeout(700)
        assert rules(ui)["fa_daa"] == (ma == "huy_chuong")
    # Các nút khác ở trang Xếp CLB
    ui.tab("pipeline")
    for sel in ("#btnValidate", "#btnToggleHistory", "#btnTaiSoMau"):
        if p.locator(sel).is_visible():
            p.locator(sel).dblclick()
            p.wait_for_timeout(500)
    if p.locator("#viecTiepTheoNut").is_visible():
        p.locator("#viecTiepTheoNut").dblclick()
        p.wait_for_timeout(500)
    assert so_dong_run(ui) == 2
    ui.kiem_loi()


def test_b1_tai_lai_trong_luc_chay(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    import time
    goc = ui.api.run_pipeline

    def cham(*a, **k):
        time.sleep(2.5)
        return goc(*a, **k)
    ui.api.run_pipeline = cham
    ui.tab("pipeline")
    p.locator("#btnRun").click()
    p.wait_for_timeout(400)
    p.reload()
    p.wait_for_selector("#dropZone", state="attached")
    time.sleep(4)
    p.wait_for_timeout(500)
    # backend: đúng một dòng lịch sử, kết quả đầy đủ, không khoá treo
    assert so_dong_run(ui) == 1
    assert len(ket_qua_db(ui)) == 150
    # UI dùng lại được sau khi tải lại
    ui.api.run_pipeline = goc
    ui.tab("pipeline")
    assert p.locator("#btnRun").is_enabled()
    kq, them = chay_ui(ui)
    assert kq == "ok" and them == 1
    assert ket_qua_db(ui) == ket_qua_ui(ui)
    ui.kiem_loi(bo_qua=("net::ERR", "Failed to fetch", "NetworkError", "Load failed"))


def test_b1_lui_tien_trinh_duyet(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    ui.tab("results")
    ui.tab("others")
    p.go_back()
    p.go_forward()
    p.wait_for_selector("#dropZone", state="attached")
    ui.tab("results")
    assert p.evaluate("document.querySelectorAll('#kqThan tr').length") in (0, 150)
    # back to blank and forward again must restore a working app
    p.goto("about:blank")
    p.go_back()
    p.wait_for_selector("#dropZone", state="attached", timeout=20000)
    ui.tab("admin")
    ui.kiem_loi(bo_qua=("net::ERR",))


def test_b1_bang_ket_qua_cu_hien_khi_tai_cham(mo):
    """Results tab keeps showing the PREVIOUS run's rows (no loading frame, no stale banner) until the reload ends."""
    import time
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    chay_ui(ui)
    ui.tab("results")
    p.wait_for_function("document.querySelectorAll('#kqThan tr').length==150")
    chon_cach(ui, "chi_xep")
    chay_ui(ui)
    goc = ui.api.get_club_fill_stats
    ui.api.get_club_fill_stats = lambda *a: (time.sleep(1.5), goc(*a))[1]
    db = ket_qua_db(ui)
    p.locator('.nav-item[data-tab="results"]').click()
    p.wait_for_timeout(300)
    ui.anh("ST-B-001_bang_ket_qua_cu")
    dang_hien = _doc_bang(ui)
    ui.api.get_club_fill_stats = goc
    assert dang_hien == db, "bảng Kết quả vẫn hiện kết quả của lần chạy TRƯỚC (300 ms sau khi bấm tab, backend trả chậm 1,5 s)"


def test_b1_hoan_tac_doi_che_do_va_viec_tiep_theo(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    for sau in ("chi_xep", "chia_100", "chi_xep", "chia_100"):
        truoc = {k: rules(ui)[k] for k in ("wharton", "fa_daa", "chia_loai")}
        chon_cach(ui, sau)
        nut = p.locator("#toastStack button", has_text="Hoàn tác")
        nut.last.wait_for(timeout=5000)
        nut.last.click()
        p.wait_for_timeout(800)
        sau_ht = {k: rules(ui)[k] for k in ("wharton", "fa_daa", "chia_loai")}
        assert sau_ht == truoc, ("Hoàn tác không trả về cấu hình cũ", sau, truoc, sau_ht)
        # thẻ trên màn hình phải khớp cấu hình thật
        dang_chon = p.evaluate("document.querySelector('.ux1a-the[aria-checked=true]').dataset.cach")
        mong = "huy_chuong" if truoc["fa_daa"] else ("chia_100" if truoc["wharton"] else "chi_xep")
        assert dang_chon == mong, ("Thẻ chọn lệch cấu hình sau Hoàn tác", dang_chon, mong)
        assert not khoa_tho(ui)
        ui.tab("pipeline")
        if p.locator("#viecTiepTheo").is_visible():
            assert not khoa_tho(ui, "#viecTiepTheo"), p.locator("#viecTiepTheo").inner_text()
    ui.kiem_loi()


def test_b1_bam_nhanh_nhieu_the_che_do(mo):
    """Click 2-3 different mode cards back to back (no wait): UI checked card must equal the saved config, run must work."""
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    ui.tab("admin")
    rng = random.Random(7)
    ids = {"chi_xep": "#ux1aChiXep", "chia_100": "#ux1aChia100", "huy_chuong": "#ux1aHuyChuong"}
    for i in range(12):
        chuoi = [rng.choice(list(ids)) for _ in range(rng.choice([2, 3]))]
        for ma in chuoi:
            p.locator(ids[ma]).click(no_wait_after=True, force=True, timeout=3000)
        p.wait_for_timeout(1800)
        r = rules(ui)
        be = "huy_chuong" if r["fa_daa"] else ("chia_100" if r["wharton"] else "chi_xep")
        ui_the = p.evaluate("(document.querySelector('.ux1a-the[aria-checked=true]')||{dataset:{}}).dataset.cach")
        assert ui_the == be, (i, chuoi, "thẻ trên màn hình", ui_the, "cấu hình thật", be)
    kq, them = chay_ui(ui)
    assert kq == "ok", p.locator("#logBox").inner_text()[:300]
    ui.kiem_loi()


def test_b1_chia_loai_bam_nhanh(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    chon_cach(ui, "chia_100")
    ui.tab("admin")
    p.locator("#qlTabClb").click()
    p.wait_for_selector("#mt2CongTac", state="attached")
    cb = p.locator("#mt2CongTac")
    for _ in range(9):
        cb.click(force=True, no_wait_after=True, timeout=2000)
        p.wait_for_timeout(60)
    p.wait_for_timeout(1800)
    assert cb.is_checked() == rules(ui)["chia_loai"], "công tắc Chia CLB theo loại lệch cấu hình thật"
    kq, them = chay_ui(ui)
    assert kq == "ok", p.locator("#logBox").inner_text()[:300]
    ui.kiem_loi()


@pytest.mark.parametrize("tu,sang", [("chia_100", "huy_chuong"), ("huy_chuong", "chia_100")])
def test_b1_cong_tac_chia_loai_cu_sau_khi_doi_che_do(mo, tu, sang):
    """After clicking a mode card, the 'Chia CLB theo loại' switch just below (Quản lý > CLB) keeps the OLD state
    (enabled/disabled + note) until the tab is re-entered."""
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    chon_cach(ui, tu)
    ui.tab("admin")
    p.locator("#qlTabClb").click()
    p.wait_for_selector("#mt2CongTac", state="visible")
    p.wait_for_timeout(600)
    chon_cach(ui, sang)
    p.wait_for_timeout(2500)
    cb = p.locator("#mt2CongTac")
    ui.anh("ST-B-002_cong_tac_chia_loai_cu_%s_sang_%s" % (tu, sang))
    assert cb.is_disabled() == (sang == "huy_chuong"), (
        "công tắc Chia CLB theo loại còn trạng thái cũ sau khi đổi sang %s: disabled=%s, checked=%s, rules=%s"
        % (sang, cb.is_disabled(), cb.is_checked(), rules(ui)["chia_loai"]))


def test_b1_nhap_o_chia_100_roi_doi_sang_huy_chuong_ui_co_bao(mo):
    """Protocol question (S3?): import in Chia 100 drops Loại; later switching to Huy chương — does the UI say so?"""
    ui = mo()
    p = ui.page
    chon_cach(ui, "chia_100")
    ui.tab("pipeline")
    p.set_input_files("#fileAny", SO_150)
    p.wait_for_selector("#btnImportAll", state="visible")
    canh_bao_nap = p.locator("#importWarnings").inner_text()
    p.locator("#btnImportAll").click()
    p.wait_for_function("document.querySelector('#statStudents').textContent==='150'", timeout=30000)
    p.wait_for_timeout(600)
    canh_bao_sau = p.locator("#importWarnings").inner_text() + p.locator("#feedbackImportAll").inner_text()
    chon_cach(ui, "huy_chuong")
    p.wait_for_timeout(1200)
    san_sang = p.locator("#ux1aSanSang")
    hien = san_sang.is_visible()
    chu = san_sang.inner_text() if hien else ""
    ui.anh("ST-B-002_doi_sang_huy_chuong_sau_nhap_chia_100")
    print("IMPORT WARNING:", canh_bao_nap[:200].replace("\n", " | "))
    print("AFTER IMPORT:", canh_bao_sau[:200].replace("\n", " | "))
    print("READINESS PANEL VISIBLE:", hien, chu[:300].replace("\n", " | "))
    assert hien and chu.strip(), "đổi sang Huy chương sau khi nhập ở Chia 100: giao diện không nói gì về Loại đã bị bỏ"
    ui.kiem_loi()
