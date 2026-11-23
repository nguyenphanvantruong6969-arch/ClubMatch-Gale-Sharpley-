"""ST-B lot B2 (part 1): import via the real UI — good + bad files. SIMULATED data."""
import pytest

from ho_tro import (chon_cach, nap_so_150, dat_tep, nap_tep, dem_db, khoa_tho)
from ho_tro_tep import CAC_TEP, goc

TU_CHOI = ["rong_0_byte", "van_ban_doi_duoi_xlsx", "xlsx_cat_cut", "xlsx_doi_duoi_xls", "duoi_pdf", "thieu_sheet_clb",
           "thieu_sheet_hoc_sinh", "chi_tieu_0", "chi_tieu_am", "chi_tieu_chu", "trung_ma_hs", "ten_clb_trung",
           "diem_am_va_1e9", "diem_la_ngay", "clb_khong_ton_tai", "loai_sai", "csv_utf16", "csv_cp1258", "csv_rong",
           "csv_bom_chi_tieu_de", "zip_hong", "sheet_clb_rong"]
TRACEBACK = ("Traceback", "File \"", "sqlite3.", "KeyError", "TypeError", "AttributeError", "ValueError", "IndexError",
             "openpyxl", "zipfile", "BadZipFile", "OperationalError")


def test_b2_nhap_tep_xau_thong_bao_sach_va_db_khong_doi(mo):
    ui = mo()
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    loi = []
    for k in TU_CHOI:
        mk, ten = CAC_TEP[k]
        nd = mk() if callable(mk) else mk
        truoc = dem_db(ui)
        txt, _nap = dat_tep(ui, ten, nd), None
        can_nap = ui.page.locator("#btnImportAll").is_visible()
        if can_nap:
            loi.append((k, "tệp xấu mà giao diện vẫn cho nạp", txt[:160]))
            continue
        if not txt.strip():
            loi.append((k, "không có thông báo nào"))
        if any(x in txt for x in TRACEBACK):
            loi.append((k, "lộ chi tiết kỹ thuật/traceback", [x for x in TRACEBACK if x in txt]))
        if khoa_tho(ui, "#importQueue"):
            loi.append((k, "khoá i18n thô", khoa_tho(ui, "#importQueue")))
        if dem_db(ui) != truoc:
            loi.append((k, "CSDL đổi dù bị từ chối", truoc, dem_db(ui)))
    assert not loi, loi
    ui.kiem_loi()


def test_b2_hai_tep_mot_lan_tot_va_xau(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    ui.tab("pipeline")
    import base64
    tep = [("tot.xlsx", goc()), ("hong.xlsx", b"not a zip")]
    p.evaluate("""async (ds) => {
        const dt = new DataTransfer();
        ds.forEach(([n, b]) => dt.items.add(new File([Uint8Array.from(atob(b), c => c.charCodeAt(0))], n)));
        const z = document.getElementById('dropZone');
        z.dispatchEvent(new DragEvent('dragover', {dataTransfer: dt, bubbles: true, cancelable: true}));
        z.dispatchEvent(new DragEvent('drop', {dataTransfer: dt, bubbles: true, cancelable: true}));
    }""", [[n, base64.b64encode(b).decode()] for n, b in tep])
    p.wait_for_timeout(3000)
    txt = p.locator("#importQueue").inner_text()
    ui.anh("ST-B-005_tha_hai_tep")
    assert "hong.xlsx" in txt or "một" in txt.lower() or "1 tệp" in txt.lower(), "thả 2 tệp: tệp thứ hai bị bỏ lặng lẽ, không có lời nào: %r" % txt[:200]
    assert not any(x in txt for x in TRACEBACK)
    if p.locator("#btnImportAll").is_visible():
        p.locator("#btnImportAll").click()
        p.wait_for_timeout(3000)
    assert dem_db(ui)[0] in (0, 150)
    ui.kiem_loi()


def test_b2_nap_lai_cung_tep_hai_lan_khong_nhan_doi(mo):
    ui = mo()
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    a = dem_db(ui)
    nap_tep(ui, "so.xlsx", goc())
    nap_tep(ui, "so.xlsx", goc())
    assert dem_db(ui) == a, (a, dem_db(ui))
    ui.kiem_loi()


def test_b2_nap_lai_so_khong_co_diem_xoa_diem_cu_khong_canh_bao(mo):
    """Re-import of a Sổ with no test marks deletes every stored tick + score; preview must at least warn."""
    ui = mo()
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    truoc = dem_db(ui, "club_test_selection", "club_scores")
    assert truoc == (337, 337), truoc
    mk, ten = CAC_TEP["mot_dong_tieu_de"]
    txt, _ = nap_tep(ui, ten, mk())
    sau = dem_db(ui, "club_test_selection", "club_scores")
    ui.anh("ST-B-003_xem_truoc_khong_canh_bao_xoa_diem")
    assert sau == truoc or "xoá" in txt.lower() or "337" in txt, (
        "điểm/ô thi cũ bị xoá %s -> %s, xem trước chỉ nói: %r" % (truoc, sau, txt[:200]))


def test_b2_ma_hoc_sinh_khac_hoa_thuong_thanh_hoc_sinh_moi(mo):
    ui = mo()
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    n0 = dem_db(ui, "students")[0]
    mk, ten = CAC_TEP["ma_hoa_thuong"]
    txt, _ = nap_tep(ui, ten, mk())
    n1 = dem_db(ui, "students")[0]
    ui.anh("ST-B-004_ma_hoa_thuong")
    assert n1 == n0 or "dc001" in txt.lower() and ("trùng" in txt.lower() or "đã có" in txt.lower()), (
        "mã 'dc001' (chỉ khác hoa/thường so với DC001) tạo thêm học sinh: %d -> %d, xem trước: %r" % (n0, n1, txt[:200]))


def test_b2_xss_ten_clb_va_hoc_sinh(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    nap_so_150(ui)
    mk, ten = CAC_TEP["xss"]
    txt, nap = nap_tep(ui, ten, mk())
    assert nap, txt[:400]
    for t in ("pipeline", "results", "others", "fallback", "scoring", "admin"):
        ui.tab(t)
        p.wait_for_timeout(500)
        if t == "admin":
            p.locator("#qlTabHs").click()
            p.wait_for_timeout(600)
            p.locator("#qlTabClb").click()
            p.wait_for_timeout(600)
        p.mouse.move(300, 300)
        # hover every element whose text contains the payload
        for el in p.locator("text=CLB XSS").all()[:5]:
            try:
                el.hover(timeout=500)
            except Exception:
                pass
    assert p.evaluate("window.__xss") is None, "đoạn mã trong tên CLB/học sinh đã CHẠY"
    assert p.evaluate("document.querySelectorAll('img[onerror], b[onmouseover]').length") == 0
    ui.kiem_loi()


def test_b2_cong_thuc_hien_nguyen_van(mo):
    ui = mo()
    p = ui.page
    chon_cach(ui, "huy_chuong")
    mk, ten = CAC_TEP["cong_thuc"]
    txt, nap = nap_tep(ui, ten, mk())
    ui.tab("admin")
    p.locator("#qlTabHs").click()
    p.wait_for_timeout(1000)
    corpus = p.locator("#adminStudentTableBody").inner_text()
    if nap:
        assert "=1+1" in corpus or "2" not in corpus.split("DC001")[1][:40] if "DC001" in corpus else True
    ui.kiem_loi()


def test_b2_nap_3000_hoc_sinh_qua_giao_dien(mo):
    """ST-A-002 cross-check: 3 150 students through the real UI + browser_host."""
    import time
    ui = mo()
    chon_cach(ui, "huy_chuong")
    mk, ten = CAC_TEP["3000_dong_them"]
    t0 = time.time()
    txt, nap = nap_tep(ui, ten, mk(), cho=500)
    ui.page.wait_for_function("document.querySelector('#statStudents').textContent!=='—'", timeout=60000)
    ui.page.wait_for_timeout(2500)
    n = dem_db(ui, "students")[0]
    giay = time.time() - t0
    print("3150 hs: nạp=%s, hs trong DB=%d, %.1fs" % (nap, n, giay))
    assert nap and n == 3150, (nap, n, txt[:300])
    ui.kiem_loi()
