"""ST-A4: exports open + round-trip; timing at 800x20 and 3000x60. SIMULATED data."""
import csv
import io
import os
import time

import openpyxl
import pytest

import rbda_priority_pipeline as rp
import sthelp
from api import PipelineAPI
from sthelp import check_contract, load_so150, new_ws_api, rows, switch

TIMES = []


def _ready(tmp_path, mode="huy_chuong", cl=True):
    a = new_ws_api(tmp_path, "ex")
    load_so150(a)
    switch(a, mode, cl)
    assert a.run_pipeline(seed=1)["ok"]
    return a


def _check_file(path):
    assert os.path.isfile(path) and os.path.getsize(path) > 0, path
    low = path.lower()
    if low.endswith(".xlsx"):
        wb = openpyxl.load_workbook(path)
        assert wb.sheetnames
        wb.close()
    elif low.endswith(".csv"):
        txt = open(path, encoding="utf-8-sig").read()
        assert list(csv.reader(io.StringIO(txt)))
    elif low.endswith(".pdf"):
        b = open(path, "rb").read()
        assert b.startswith(b"%PDF") and b.rstrip().endswith(b"%%EOF"), path
    elif low.endswith(".zip"):
        import zipfile
        assert zipfile.ZipFile(path).testzip() is None


@pytest.mark.parametrize("mode,cl", [("chi_xep", False), ("chia_100", False), ("huy_chuong", True)])
def test_exports_open(tmp_path, mode, cl):
    a = _ready(tmp_path, mode, cl)
    out = tmp_path / "out"
    out.mkdir()
    slug = os.listdir(os.path.join(a._goc_ws, "workspaces"))[0]
    calls = [("export_theo_lop", (str(out / "tl.xlsx"),)), ("export_danh_sach_pdf", (str(out / "ds.pdf"),)),
             ("export_danh_sach_pdf", (str(out / "dl.pdf"), "lop")),
             ("export_du_lieu_dau_vao", (str(out / "dv.xlsx"),)), ("tao_so_nhap_mau", (str(out / "mau.xlsx"),)),
             ("export_hoc_sinh_csv", (["DC001", "DC002"], str(out / "hs.csv"))), ("export_ket_qua", (str(out / "kq.xlsx"), True)),
             ("export_csv", (str(out / "r.csv"),)),
             ("export_phieu_giai_trinh_pdf", (str(out / "pgt.pdf"),)), ("export_bao_cao_tong_hop_pdf", (str(out / "bc.pdf"),)),
             ("export_workspace", (slug, str(out / "ws.zip")))]
    if mode == "huy_chuong":      # reasons exist only with FA-DAA (`fa_chua_co_ly_do` otherwise: by design)
        calls.append(("export_ly_do_csv", (str(out / "ld.csv"),)))
    for n, args in calls:
        r = getattr(a, n)(*args)
        check_contract(r, n)
        assert r["ok"], (n, r["errors"][:2])
    for f in os.listdir(out):
        p = os.path.join(out, f)
        if os.path.isfile(p):
            _check_file(p)
    for root, _, files in os.walk(out):
        for f in files:
            _check_file(os.path.join(root, f))


@pytest.mark.parametrize("mode,cl", [("chi_xep", False), ("huy_chuong", True)])
def test_input_export_reimport_roundtrip(tmp_path, mode, cl):
    a = _ready(tmp_path, mode, cl)
    p = str(tmp_path / "dv.xlsx")
    r = a.export_du_lieu_dau_vao(p)
    assert r["ok"], r
    b = new_ws_api(tmp_path, "rt")
    switch(b, mode, cl)
    res = b.import_so_nhap(sthelp.b64_file(p))
    check_contract(res, "reimport")
    assert res["ok"], res["errors"][:2]

    def snap(x):
        cols = "club_id, name, capacity, buoi, loai, diem_san" if cl or mode == "huy_chuong" else "club_id, name, capacity, buoi"
        return (rows(x.db_path, "SELECT %s FROM clubs ORDER BY 1" % cols),
                rows(x.db_path, "SELECT student_id, club_id, rank FROM preferences ORDER BY 1,3"),
                rows(x.db_path, "SELECT student_id, club_id, score FROM club_scores ORDER BY 1,2"))
    sa, sb = snap(a), snap(b)
    for i, nm in enumerate(("clubs", "prefs", "scores")):
        assert sa[i] == sb[i], "round trip changed %s (%d vs %d rows)" % (nm, len(sa[i]), len(sb[i]))
    b.run_pipeline(seed=1)
    a.run_pipeline(seed=1)
    assert sthelp.match_rows(a.db_path) == sthelp.match_rows(b.db_path), "re-imported book gives a different allocation"


def _big(tmp_path, n, m, name):
    p = tmp_path / (name + ".db")
    cap = max(2, int(n * 1.1 / m))
    defs = [("c%03d" % i, cap, 0, None) for i in range(m)]
    rp.seed_sample_data(str(p), n_students=n, club_defs=defs, seed=5)
    import cau_hinh_ws as ch
    ch.ghi_cau_hinh(str(p), {"rules": {"wharton": False}})      # seed data has no points: Chỉ xếp mode
    return PipelineAPI(str(p), thu_muc_xuat=str(tmp_path / ("x" + name)))


@pytest.mark.parametrize("n,m", [(800, 20), (3000, 60)])
def test_timing(tmp_path, n, m):
    a = _big(tmp_path, n, m, "big%d" % n)
    out = {}

    def t(label, fn, *args):
        t0 = time.time()
        r = fn(*args)
        out[label] = round(time.time() - t0, 2)
        check_contract(r, label)
        return r
    r = t("run_pipeline", a.run_pipeline, 1)
    assert r["ok"], r["errors"][:2]
    t("rerun", a.run_pipeline, 1)
    t("get_match_results", a.get_match_results)
    t("get_data_health_report", a.get_data_health_report)
    t("get_dashboard_status", a.get_dashboard_status)
    t("list_students_admin", a.list_students_admin)
    t("export_ket_qua", a.export_ket_qua, str(tmp_path / "kq.xlsx"), True)
    t("export_csv", a.export_csv, str(tmp_path / "r.csv"))
    t("export_danh_sach_pdf", a.export_danh_sach_pdf, str(tmp_path / "ds.pdf"))
    t("export_bao_cao_tong_hop_pdf", a.export_bao_cao_tong_hop_pdf, str(tmp_path / "bc.pdf"))
    line = "%dx%d %s" % (n, m, out)
    print(line)
    with open(os.path.join(sthelp.GOC, "docs", "phien", "ST_A_TIMING.txt"), "a") as f:
        f.write(line + "\n")
    slow = {k: v for k, v in out.items() if v > 30}
    assert not slow, "S2: > 30 s: %s" % slow


def _scaled_book(tmp_path, n):
    """Shared-Sổ generator scaled to n students (module constants patched in memory; capacities scaled ~n/150)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_so", os.path.join(sthelp.GOC, "du_lieu_test", "tao_so_nhap_doi_che_do.py"))
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    f = n / 150.0
    g.N_HOC_SINH = n
    for b, lst in g.CLB_MOI_BUOI.items():
        g.CLB_MOI_BUOI[b] = [(nm, lo, n if lo == g.so_nhap.TU_DO else max(2, int(cap * f)), san) for nm, lo, cap, san in lst]
    p = str(tmp_path / ("so_%d.xlsx" % n))
    g.ghi(p)
    return p


@pytest.mark.parametrize("n", [800, 3000])
@pytest.mark.parametrize("mode,cl", [("huy_chuong", True), ("chia_100", False)])
def test_timing_scaled_book(tmp_path, n, mode, cl):
    """Whole workflow on the scaled shared Sổ: import, switch, run, export. > 30 s on any step = S2."""
    p = _scaled_book(tmp_path, n)
    a = new_ws_api(tmp_path, "sc")
    switch(a, "huy_chuong", False)
    out = {}

    def t(label, fn, *args):
        t0 = time.time()
        r = fn(*args)
        out[label] = round(time.time() - t0, 2)
        check_contract(r, label)
        return r
    r = t("import_so_nhap", a.import_so_nhap, sthelp.b64_file(p))
    if not r["ok"]:
        pytest.xfail("ST-A-002: %s" % r["errors"][:1])
    switch(a, mode, cl)
    r = t("run_pipeline", a.run_pipeline, 1)
    assert r["ok"], r["errors"][:2]
    t("get_data_health_report", a.get_data_health_report)
    t("export_ket_qua", a.export_ket_qua, str(tmp_path / "kq.xlsx"), True)
    t("export_phieu_giai_trinh_pdf", a.export_phieu_giai_trinh_pdf, str(tmp_path / "pgt.pdf"))
    line = "book %d %s/%s %s" % (n, mode, cl, out)
    print(line)
    with open(os.path.join(sthelp.GOC, "docs", "phien", "ST_A_TIMING.txt"), "a") as f:
        f.write(line + "\n")
    slow = {k: v for k, v in out.items() if v > 30}
    assert not slow, out
