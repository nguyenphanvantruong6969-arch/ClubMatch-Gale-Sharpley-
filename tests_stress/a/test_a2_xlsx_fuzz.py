"""ST-A2: Sổ nhập (xlsx) mutation fuzzing: >= 40 kinds. Expect contract + known i18n codes, no traceback, DB unchanged
on refusal. SIMULATED data."""
import io
import unicodedata

import openpyxl
import pytest

import sthelp
from sthelp import b64_bytes, check_contract, db_bytes, load_so150, new_ws_api, switch

MUT = {}


def mut(name):
    def d(f):
        MUT[name] = f
        return f
    return d


def S(wb):  # students sheet
    return wb["2. Học sinh"]


def C(wb):
    return wb["1. CLB"]


def setv(ws, r, c, v):
    """openpyxl's ws.cell(row, column, value=None) does NOT clear a cell; this does."""
    ws.cell(row=r, column=c).value = v


def _hdr_cols(ws, row=1):
    return {str(c.value).strip(): c.column for c in ws[row] if c.value is not None}


# ---------- structure ----------
@mut("del_clb_sheet")
def _(wb): del wb["1. CLB"]
@mut("del_hs_sheet")
def _(wb): del wb["2. Học sinh"]
@mut("only_guide")
def _(wb): del wb["1. CLB"]; del wb["2. Học sinh"]
@mut("rename_sheets_lower")
def _(wb): C(wb).title = "1. clb"; S(wb).title = "2. học sinh"
@mut("empty_workbook")
def _(wb):
    for n in list(wb.sheetnames): del wb[n]
    wb.create_sheet("Sheet1")
@mut("clb_header_only")
def _(wb): C(wb).delete_rows(2, 500)
@mut("hs_header_only")
def _(wb): S(wb).delete_rows(3, 5000)
@mut("hs_one_row_header")
def _(wb):
    for rng in list(S(wb).merged_cells.ranges): S(wb).unmerge_cells(str(rng))
    S(wb).delete_rows(2)
@mut("clb_no_header")
def _(wb): C(wb).delete_rows(1)
@mut("merged_clb_cells")
def _(wb): C(wb).merge_cells("A2:C5")
@mut("merged_hs_header")
def _(wb): S(wb).merge_cells("D1:AU1")
@mut("hidden_sheet")
def _(wb): C(wb).sheet_state = "hidden"
@mut("extra_blank_cols")
def _(wb): S(wb).cell(row=3, column=80, value="x")
@mut("swap_sheet_order")
def _(wb): wb.move_sheet("2. Học sinh", offset=-1)

# ---------- ids / names ----------
@mut("nfd_club_names_in_prefs")
def _(wb):
    for row in S(wb).iter_rows(min_row=3):
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("CLB "):
                c.value = unicodedata.normalize("NFD", c.value)
@mut("nfd_clb_sheet")
def _(wb):
    for row in C(wb).iter_rows(min_row=2, max_col=1):
        for c in row:
            if isinstance(c.value, str): c.value = unicodedata.normalize("NFD", c.value)
@mut("spaces_in_club_prefs")
def _(wb):
    for row in S(wb).iter_rows(min_row=3, max_row=40):
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("CLB "):
                c.value = "  " + c.value.replace(" ", "  ") + " "
@mut("case_club_prefs")
def _(wb):
    for row in S(wb).iter_rows(min_row=3, max_row=40):
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("CLB "): c.value = c.value.upper()
@mut("case_dup_student_ids")
def _(wb): S(wb).cell(row=4, column=1, value=str(S(wb).cell(row=3, column=1).value).lower())
@mut("dup_student_rows")
def _(wb):
    for col in range(1, 8): S(wb).cell(row=5, column=col, value=S(wb).cell(row=3, column=col).value)
@mut("dup_club_names")
def _(wb): C(wb).cell(row=3, column=1, value=C(wb).cell(row=2, column=1).value)
@mut("dup_club_ids")
def _(wb): C(wb).cell(row=3, column=6, value=C(wb).cell(row=2, column=6).value)
@mut("empty_student_id")
def _(wb): setv(S(wb), 3, 1, None)
@mut("weird_student_id")
def _(wb): S(wb).cell(row=3, column=1, value="  DC 001 ​😀/\\..")
@mut("long_student_id")
def _(wb): S(wb).cell(row=3, column=1, value="X" * 5000)
@mut("int_student_ids")
def _(wb):
    for i, row in enumerate(S(wb).iter_rows(min_row=3, max_row=60, max_col=1)): row[0].value = 1000 + i
@mut("sql_names")
def _(wb): S(wb).cell(row=3, column=2, value="'; DROP TABLE clubs;--"); C(wb).cell(row=2, column=1, value="x'); DELETE FROM students;--")
@mut("html_names")
def _(wb): S(wb).cell(row=3, column=2, value="<script>alert(1)</script>")
@mut("zero_width_ids")
def _(wb): S(wb).cell(row=3, column=1, value="D​C​001")
@mut("newline_in_name")
def _(wb): S(wb).cell(row=3, column=2, value="a\nb\tc\r\nd")
@mut("formula_injection_name")
def _(wb): S(wb).cell(row=3, column=2, value="=cmd|' /C calc'!A0")
@mut("formula_cells")
def _(wb): S(wb).cell(row=3, column=5, value="=1+1"); C(wb).cell(row=2, column=3, value="=5*5")
@mut("huge_cell_text")
def _(wb): S(wb).cell(row=3, column=2, value="Ư" * 32000)
@mut("unknown_club_in_pref")
def _(wb): S(wb).cell(row=3, column=4, value="CLB Không Tồn Tại")
@mut("same_club_twice_in_prefs")
def _(wb): S(wb).cell(row=3, column=7, value=S(wb).cell(row=3, column=4).value)
@mut("all_empty_prefs_student")
def _(wb):
    for col in range(4, 49): setv(S(wb), 3, col, None)

# ---------- numbers ----------
def _cap(v):
    def f(wb): setv(C(wb), 2, 3, v)
    return f
for n, v in [("cap_zero", 0), ("cap_negative", -5), ("cap_1e9", 10 ** 9), ("cap_comma", "9,5"), ("cap_text", "abc"),
             ("cap_float", 10.5), ("cap_empty", None), ("cap_1e300", 1e300), ("cap_nan_text", "nan"), ("cap_huge_int", 10 ** 30)]:
    MUT[n] = _cap(v)


def _score(v):
    def f(wb):
        for r in range(3, 30): 
            if S(wb).cell(row=r, column=5).value is not None:
                S(wb).cell(row=r, column=5, value=v)
                return
    return f
import datetime
for n, v in [("score_comma", "9,5"), ("score_neg", -3), ("score_1e9", 10 ** 9), ("score_text", "N/A"),
             ("score_date", datetime.datetime(2026, 1, 1)), ("score_bool", True), ("score_inf_text", "inf"), ("score_over_10", 11)]:
    MUT[n] = _score(v)


def _medal(v):
    def f(wb):
        for r in range(3, 30):
            if S(wb).cell(row=r, column=6).value is not None:
                S(wb).cell(row=r, column=6, value=v)
                return
    return f
for n, v in [("medal_65", 65), ("medal_zero", 0), ("medal_neg", -5), ("medal_text", "Vàng"), ("medal_float", 60.5), ("medal_1e9", 10 ** 9)]:
    MUT[n] = _medal(v)


@mut("score_6_tested_clubs_one_session")
def _(wb):
    ws = S(wb)
    for col in (5, 8, 11, 14, 17, 20): ws.cell(row=3, column=col, value=5)
@mut("11_prefs_one_session")
def _(wb):
    for k in range(6): C(wb).append(["CLB Phu %d" % k, "Thứ 3", 20, None, None, "P%d" % k, "Giới hạn", None, None, None])
    ws = S(wb)
    names = [c.value for c in C(wb)["A"][1:] if c.value and C(wb).cell(row=c.row, column=2).value == "Thứ 3"]
    assert len(names) >= 11
    for col in range(4, 49): setv(ws, 3, col, None)
    for k in range(11): setv(ws, 3, 4 + 3 * k, names[k])
@mut("14_prefs_two_sessions")
def _(wb):
    ws = S(wb)
    clubs = [c.value for c in C(wb)["A"][1:] if c.value]
    for col in range(4, 49): setv(ws, 3, col, None)
    for k in range(len(clubs)): setv(ws, 3, 4 + 3 * k, clubs[k])
@mut("floor_negative")
def _(wb): C(wb).cell(row=5, column=8, value=-3)
@mut("floor_text")
def _(wb): C(wb).cell(row=5, column=8, value="cao")
@mut("min_gt_capacity")
def _(wb): C(wb).cell(row=3, column=9, value=999)
@mut("loai_invalid")
def _(wb): C(wb).cell(row=3, column=7, value="Siêu cấp")
@mut("buoi_invalid")
def _(wb): C(wb).cell(row=3, column=2, value="Thứ 9")
@mut("buoi_empty")
def _(wb): setv(C(wb), 3, 2, None)
@mut("reserve_gt_capacity")
def _(wb): C(wb).cell(row=3, column=4, value=9999)
@mut("many_clubs_300")
def _(wb):
    for i in range(300): C(wb).append(["CLB Moi %d" % i, "Thứ 3", 5, None, None, "M%d" % i, "Giới hạn", None, None, None])
def _more_students(wb, n):
    ws = S(wb)
    base = [c.value for c in ws[3]]
    for i in range(n):
        r = list(base); r[0] = "ZZ%05d" % i; ws.append(r)


@mut("1000_rows")
def _(wb): _more_students(wb, 1000)


KNOWN = {k: MUT.pop(k) for k in ("cap_1e300", "cap_huge_int", "hs_one_row_header")}   # ST-A-003, own xfail test below


@pytest.fixture(scope="module")
def base_bytes():
    with open(sthelp.SO_150, "rb") as f:
        return f.read()


def _mutated(base, name):
    wb = openpyxl.load_workbook(io.BytesIO(base))
    MUT[name](wb)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def test_at_least_40_kinds():
    assert len(MUT) >= 40, len(MUT)


@pytest.mark.parametrize("name", sorted(MUT))
def test_mutation(tmp_path, base_bytes, name):
    api = new_ws_api(tmp_path, "m")
    load_so150(api)                       # preloaded: a refusal must leave this untouched
    data = _mutated(base_bytes, name)
    snap = db_bytes(api.db_path)
    prev = api.xem_truoc_so_nhap(b64_bytes(data))
    check_contract(prev, name + ":preview")
    assert db_bytes(api.db_path) == snap, "preview wrote to the DB"
    res = api.import_so_nhap(b64_bytes(data))
    check_contract(res, name + ":import")
    if not res["ok"]:
        assert db_bytes(api.db_path) == snap, "refused import changed the DB"
        assert not prev["ok"] or prev["data"].get("loi"), "preview says clean, import refuses"
    else:
        # accepted: system must stay coherent (health + run never traceback)
        h = api.get_data_health_report()
        check_contract(h, name + ":health")
        r = api.run_pipeline(seed=1)
        check_contract(r, name + ":run")


@pytest.mark.parametrize("n", [1500, 2500])
def test_big_book_ok(tmp_path, base_bytes, n):
    api = new_ws_api(tmp_path, "big")
    switch(api, "huy_chuong", False)
    wb = openpyxl.load_workbook(io.BytesIO(base_bytes))
    _more_students(wb, n)
    out = io.BytesIO(); wb.save(out)
    res = api.import_so_nhap(b64_bytes(out.getvalue()))
    assert res["ok"], res["errors"]


@pytest.mark.parametrize("n", [3000, 3000])   # reproduced twice (fresh tmp each time)
def test_big_book_3000_rows(tmp_path, base_bytes, n):
    """3000-student Sổ: import fails with csdl_dang_ban although nothing else uses the DB (single thread)."""
    api = new_ws_api(tmp_path, "big3")
    switch(api, "huy_chuong", False)
    wb = openpyxl.load_workbook(io.BytesIO(base_bytes))
    _more_students(wb, n)
    out = io.BytesIO(); wb.save(out)
    res = api.import_so_nhap(b64_bytes(out.getvalue()))
    assert res["ok"], res["errors"]


@pytest.mark.xfail(strict=True, reason="ST-A-003")
@pytest.mark.parametrize("name", ["cap_1e300", "cap_huge_int"])
def test_capacity_beyond_int64_preview_matches_import(tmp_path, base_bytes, name):
    """preview must refuse (or import must succeed) — not preview OK then import `error_importing_clubs_csv` with a raw
    'Python int too large to convert to SQLite INTEGER' detail."""
    api = new_ws_api(tmp_path, "i64")
    load_so150(api)
    wb = openpyxl.load_workbook(io.BytesIO(base_bytes))
    KNOWN[name](wb)
    out = io.BytesIO(); wb.save(out)
    data = b64_bytes(out.getvalue())
    prev = api.xem_truoc_so_nhap(data)
    res = api.import_so_nhap(data)
    assert res["ok"] or (not prev["ok"] or prev["data"]["loi"]), (prev["ok"], res["errors"][:1])
    assert res["ok"] or res["errors"][0]["code"] != "error_importing_clubs_csv"


@pytest.mark.parametrize("rep", [1, 2])
def test_one_row_header_does_not_silently_drop_points(tmp_path, base_bytes, rep):
    """Sub-header row removed: 337 test scores + all medals sit in unlabeled columns. Import must refuse or warn that
    cells were ignored; today it says ok with zero warnings and 0 scores."""
    api = new_ws_api(tmp_path, "oneh%d" % rep)
    switch(api, "huy_chuong", False)
    wb = openpyxl.load_workbook(io.BytesIO(base_bytes))
    KNOWN["hs_one_row_header"](wb)
    out = io.BytesIO(); wb.save(out)
    res = api.import_so_nhap(b64_bytes(out.getvalue()))
    assert (not res["ok"]) or res["data"]["warnings"], "ok:true, 0 warnings, n_scores_written=%s" % res["data"]["n_scores_written"]
