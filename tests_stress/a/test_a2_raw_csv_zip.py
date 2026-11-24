"""ST-A2: raw-bytes xlsx abuse, CSV imports (3 kinds + auto), workspace zip. SIMULATED data."""
import io
import os
import random
import signal
import zipfile

import pytest

import sthelp
from sthelp import b64_bytes, check_contract, db_bytes, load_so150, new_ws_api, switch


@pytest.fixture(scope="module")
def base_bytes():
    return open(sthelp.SO_150, "rb").read()


def _limit(sec):
    class L:
        def __enter__(self):
            signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TimeoutError("hang > %ds" % sec)))
            signal.alarm(sec)
        def __exit__(self, *a):
            signal.alarm(0)
    return L()


def _raw_cases(base):
    rng = random.Random(1)
    z = io.BytesIO()
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
        f.writestr("[Content_Types].xml", "<x/>")
        f.writestr("xl/worksheets/sheet1.xml", b"\0" * (150 * 1024 * 1024))   # inflates 150 MB
    flipped = bytearray(base)
    for _ in range(40):
        flipped[rng.randrange(len(flipped))] ^= 0xFF
    return {
        "empty": b"",
        "random_1k": bytes(rng.randrange(256) for _ in range(1024)),
        "truncated": base[: len(base) // 2],
        "flipped_bytes": bytes(flipped),
        "ole_xls_header": bytes.fromhex("D0CF11E0A1B11AE1") + b"\0" * 600,
        "csv_text": "a,b,c\n1,2,3\n".encode(),
        "html_renamed": b"<html><body>hello</body></html>",
        "zip_bomb_150mb": z.getvalue(),
        "zip_empty": zipfile.ZipFile(io.BytesIO(), "w").fp.getvalue() if False else b"PK\x05\x06" + b"\0" * 18,
        "png": bytes.fromhex("89504E470D0A1A0A") + b"\0" * 100,
        "30mb_noise": b"\x00" * (30 * 1024 * 1024),
    }


@pytest.mark.parametrize("case", ["empty", "random_1k", "truncated", "flipped_bytes", "ole_xls_header", "csv_text",
                                  "html_renamed", "zip_bomb_150mb", "zip_empty", "png", "30mb_noise"])
def test_raw_bytes(tmp_path, base_bytes, case):
    api = new_ws_api(tmp_path, "raw")
    load_so150(api)
    snap = db_bytes(api.db_path)
    data = _raw_cases(base_bytes)[case]
    with _limit(60):
        for fn in (api.xem_truoc_so_nhap, api.import_so_nhap):
            res = fn(b64_bytes(data))
            check_contract(res, case)
            if case != "flipped_bytes":     # flipped may by luck still parse; others must refuse
                assert not res["ok"], (case, fn.__name__)
    assert db_bytes(api.db_path) == snap


@pytest.mark.parametrize("arg", [None, 5, 3.5, [], {}, b"abc", "not base64!!", "====", "A" * 7, "é" * 10])
def test_bad_base64_args(tmp_path, arg):
    api = new_ws_api(tmp_path, "b64")
    switch(api, "huy_chuong", False)
    snap = db_bytes(api.db_path)
    for fn in (api.xem_truoc_so_nhap, api.import_so_nhap, api.xlsx_to_csv_text):
        res = fn(arg)
        check_contract(res, "%s(%r)" % (fn.__name__, arg))
        assert not res["ok"]
    assert db_bytes(api.db_path) == snap


# ------------------------------------------------------------------ CSV
CLB_OK = "club_id,name,capacity\nA,CLB A,5\nB,CLB B,3\n"
PREF_OK = ("student_id,pref_1,pref_2\nS1,A,B\nS2,B,A\n")
SEL_OK = "club_id,student_id\nA,S1\n"


def _csv_variants(good):
    lines = good.split("\n")
    return {
        "bom": "﻿" + good,
        "crlf": good.replace("\n", "\r\n"),
        "cr_only": good.replace("\n", "\r"),
        "semicolon": good.replace(",", ";"),
        "tab": good.replace(",", "\t"),
        "empty": "",
        "only_ws": "  \n\n  ",
        "header_only": lines[0] + "\n",
        "no_header": "\n".join(lines[1:]),
        "mojibake": good.replace("CLB", "CLB Ã¢m").replace("S1", "Ã\x90"),
        "nul": good.replace("A", "A\x00", 1),
        "quote_unbalanced": good.replace("CLB A", '"CLB A'),
        "quoted_newline": good.replace("CLB A", '"CLB\nA"'),
        "dup_header": lines[0] + "," + lines[0].split(",")[0] + "\n" + "\n".join(lines[1:]),
        "ragged": good + "x,y,z,w,v,u\n",
        "huge_field": good.replace("CLB A", "Ư" * 200000),
        "sql": good.replace("CLB A", "'; DROP TABLE clubs;--"),
        "formula": good.replace("CLB A", "=cmd|' /C calc'!A0"),
        "neg_numbers": good.replace("5", "-5"),
        "big_numbers": good.replace("5", "9" * 40),
        "comma_decimal": good.replace("5", '"9,5"'),
        "trailing_blank_rows": good + "\n" * 50,
        "unicode_nfd": __import__("unicodedata").normalize("NFD", good.replace("CLB", "Câu lạc bộ")),
        "100k_rows": lines[0] + "\n" + "\n".join("C%d,CLB %d,5" % (i, i) for i in range(100000)) if "capacity" in good else good,
    }


@pytest.mark.parametrize("kind,good,fn", [("clubs", CLB_OK, "import_clubs_csv"),
                                           ("prefs", PREF_OK, "import_preferences_csv"),
                                           ("sel", SEL_OK, "import_test_selection_csv")])
def test_csv_variants_contract(tmp_path, kind, good, fn):
    for name, text in _csv_variants(good).items():
        api = new_ws_api(tmp_path, "c_%s_%s" % (kind, name))
        switch(api, "chi_xep", False)
        if kind != "clubs":
            api.import_clubs_csv(CLB_OK)
        db_bytes(api.db_path)
        with _limit(60):
            for call in (getattr(api, fn), lambda t, a=api: a.import_csv_auto(t), lambda t, a=api: a.detect_csv_kind(t),
                         lambda t, a=api, k=kind: a.preview_import_csv(t, {"clubs": "clubs", "prefs": "preferences",
                                                                          "sel": "test_selection"}[k])):
                res = call(text)
                check_contract(res, "%s/%s" % (kind, name))
        # a refused import (any) leaves everything untouched only if ok was False for the last mutating call
        res = getattr(api, fn)(text)
        check_contract(res, "%s/%s:again" % (kind, name))


def test_csv_refusal_leaves_db_unchanged(tmp_path):
    api = new_ws_api(tmp_path, "unch")
    switch(api, "chi_xep", False)
    api.import_clubs_csv(CLB_OK)
    api.import_preferences_csv(PREF_OK)
    snap = db_bytes(api.db_path)
    for text in ("", "garbage", "club_id,name,capacity\nA,CLB A,-1\n", "club_id,name,capacity\nA,CLB A,abc\n",
                 "club_id,name,capacity\n,CLB A,5\n", "club_id,name,capacity\nA,,5\n"):
        res = api.import_clubs_csv(text)
        check_contract(res, repr(text))
        if not res["ok"]:
            assert db_bytes(api.db_path) == snap, repr(text)


# ------------------------------------------------------------------ workspace zip
def _zip(entries, compress=zipfile.ZIP_DEFLATED):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", compress) as z:
        for name, data in entries:
            z.writestr(name, data)
    return b.getvalue()


def test_workspace_zip_abuse(tmp_path, base_bytes):
    api = new_ws_api(tmp_path, "zipapi")
    load_so150(api)
    ex = api.export_workspace(api.list_workspaces()["data"]["workspaces"][0]["slug"] if "workspaces" in api.list_workspaces()["data"] else "", str(tmp_path / "good.zip"))
    good = open(ex["data"]["path"], "rb").read() if ex["ok"] else None
    db = open(api.db_path, "rb").read()
    cases = {
        "empty_zip": _zip([]),
        "no_db": _zip([("x.txt", "hi")]),
        "db_garbage": _zip([("app.db", b"not sqlite" * 100)]),
        "traversal": _zip([("app.db", db), ("../evil.txt", "x")]),
        "abs_path": _zip([("app.db", db), ("/etc/evil.txt", "x")]),
        "backslash_traversal": _zip([("app.db", db), ("..\\evil.txt", "x")]),
        "dup_names": _zip([("app.db", db), ("APP.DB", db)]),
        "nul_name": _zip([("app.db", db), ("a\0.txt", "x")]),
        "nested_db": _zip([("sub/app.db", db)]),
        "journal_sidecar": _zip([("app.db", db), ("app.db-journal", b"zz")]),
        "bomb": _zip([("app.db", db), ("pad.bin", b"\0" * (400 * 1024 * 1024))]),
        "many_files": _zip([("app.db", db)] + [("f%d.txt" % i, "x") for i in range(3000)]),
        "not_zip": b"hello",
        "truncated": (good or _zip([("app.db", db)]))[:100],
    }
    set(os.listdir(api._goc_ws))
    for name, data in cases.items():
        with _limit(90):
            try:
                res = api.import_workspace(b64_bytes(data), name + ".zip")
            except Exception as e:     # contract violation: must be {ok,data,errors}
                pytest.fail("%s: raised %s: %s" % (name, type(e).__name__, str(e)[:120]))
        check_contract(res, name)
    # no evil file anywhere outside workspace root
    for root in (str(tmp_path), os.path.dirname(str(tmp_path))):
        assert not os.path.exists(os.path.join(root, "evil.txt"))
    assert not os.path.exists("/etc/evil.txt")
    assert not [x for x in os.listdir(api._goc_ws) if x.startswith("_nhap-")], "temp import dirs leaked"
