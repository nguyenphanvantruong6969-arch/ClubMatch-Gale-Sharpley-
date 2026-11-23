"""ST-A4: every public PipelineAPI method with None / wrong type / huge / SQL-ish / path strings -> contract; workspace
path traversal with sentinels. SIMULATED data."""
import os
import shutil

import pytest

import apifuzz as F
import sthelp
from sthelp import check_contract, load_so150, new_ws_api, rows, switch

NON_CONTRACT = {"chuan_hoa_buoi", "chuan_hoa_nhom_du_tru"}   # pure string helpers (return str), not API calls
FLAKY_IMPORT = {"ai_chua_dang_ky", "chuyen_tep_forms", "doi_chieu_hai_lan"}   # ST-A-007 (imports before precondition)


@pytest.fixture(scope="module")
def prepared(tmp_path_factory):
    d = tmp_path_factory.mktemp("prep")
    a = new_ws_api(d, "p")
    load_so150(a)
    switch(a, "chi_xep", False)
    assert a.run_pipeline(seed=1)["ok"]
    keep = d / "prep.db"
    shutil.copy(a.db_path, keep)
    return a, str(keep)


def _names():
    import tempfile, pathlib
    d = pathlib.Path(tempfile.mkdtemp())
    a = new_ws_api(d, "n")
    return [n for n in F.public_methods(a) if n not in F.SKIP]


@pytest.mark.parametrize("name", _names())
def test_method_contract_on_bad_args(prepared, tmp_path, monkeypatch, name):
    if name in NON_CONTRACT:
        pytest.skip("string helper")
    monkeypatch.chdir(tmp_path)           # relative output paths land in tmp
    a, prep = prepared
    shutil.copy(prep, a.db_path)
    f = getattr(a, name)
    k = F.n_required(f)
    bad = []
    for vn, v in F.VALUES.items():
        try:
            r = F.call_limited(f, [v] * k, 45)
            check_contract(r, "%s(%s)" % (name, vn))
        except BaseException as e:
            bad.append("%s: %s %s" % (vn, type(e).__name__, str(e)[:90]))
    if name in FLAKY_IMPORT and bad:
        pytest.xfail("ST-A-007: " + bad[0])
    assert not bad, bad[:3]
    c = __import__("sqlite3").connect(a.db_path)
    try:
        assert c.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        c.close()


@pytest.mark.parametrize("name", ["export_csv", "export_ket_qua", "export_theo_lop", "export_du_lieu_dau_vao", "export_hoc_sinh_csv",
                                  "export_phieu_giai_trinh", "export_danh_sach_pdf", "tao_so_nhap_mau", "export_workspace"])
@pytest.mark.parametrize("path", ["", "/", ".", "..", "/nonexistent_dir_xyz/a.xlsx", "a\0b.xlsx", "x" * 400 + ".xlsx", "CON", "a/b/c/d.xlsx",
                                  "../../escape.xlsx", "~/x.xlsx", "C:\\Windows\\x.xlsx", "\\\\server\\share\\x.xlsx"])
def test_export_path_strings(prepared, tmp_path, monkeypatch, name, path):
    monkeypatch.chdir(tmp_path)
    a, prep = prepared
    shutil.copy(prep, a.db_path)
    slug = os.listdir(os.path.join(a._goc_ws, "workspaces"))[0]
    args = {"export_hoc_sinh_csv": (["DC001"], path), "export_workspace": (slug, path)}.get(name, (path,))
    r = F.call_limited(getattr(a, name), args, 60)
    check_contract(r, "%s(%r)" % (name, path))
    assert not os.path.exists("/escape.xlsx") and not os.path.exists(os.path.join(os.path.dirname(str(tmp_path)), "escape.xlsx"))


def test_workspace_traversal_sentinels(tmp_path):
    a = new_ws_api(tmp_path, "tr")
    root = a._goc_ws
    sentinel = os.path.join(os.path.dirname(root), "SENTINEL")
    os.makedirs(sentinel)
    open(os.path.join(sentinel, "keep.txt"), "w").write("x")
    other = os.path.join(root, "workspaces")
    slugs = ["../SENTINEL", "..\\SENTINEL", "../../SENTINEL", "/" + sentinel, sentinel, "x/../../SENTINEL", "..", ".", "",
             "workspaces/../../SENTINEL", "%2e%2e/SENTINEL", "a\0/../SENTINEL"]
    for s in slugs:
        for name, args in (("delete_workspace", (s,)), ("rename_workspace", (s, "pwned")), ("duplicate_workspace", (s,)),
                           ("open_workspace", (s,)), ("export_workspace", (s, str(tmp_path / "o.zip"))),
                           ("save_as_template", (s, "tpl"))):
            try:
                r = getattr(a, name)(*args)
            except Exception as e:
                pytest.fail("%s(%r) raised %s" % (name, s, e))
            check_contract(r, "%s(%r)" % (name, s))
    assert os.path.isdir(sentinel) and os.path.exists(os.path.join(sentinel, "keep.txt")), "workspace op escaped the root"
    for nm in ("../x", "..\\x", "a/b", "../../etc", "n\0m", "con", "x" * 500, "<>:\"|?*"):
        r = a.create_workspace(nm)
        check_contract(r, "create(%r)" % nm)
        if r["ok"]:
            slug = r["data"]["slug"]
            assert os.path.realpath(os.path.join(root, "workspaces", slug)).startswith(os.path.realpath(root)), slug


def test_mo_tep_mo_thu_muc_never_launch(tmp_path, monkeypatch):
    """mo_tep / mo_thu_muc launch OS programs: with hostile paths they must refuse, not exec shell metacharacters."""
    import subprocess
    launched = []
    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: launched.append(a) or (_ for _ in ()).throw(OSError("blocked")))
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: launched.append(a) or (_ for _ in ()).throw(OSError("blocked")))
    monkeypatch.setattr(os, "startfile", lambda *a, **k: launched.append(a), raising=False)
    a = new_ws_api(tmp_path, "mo")
    for fn in (a.mo_tep, a.mo_thu_muc):
        for p in ["", None, "/etc/passwd", "x; rm -rf /", "$(id)", "../../x", "a\0b", "/nonexistent", "-rf", "--help", "http://evil.example/x"]:
            try:
                r = fn(p)
            except Exception as e:
                pytest.fail("%s(%r) raised %r" % (fn.__name__, p, e))
            check_contract(r, "%s(%r)" % (fn.__name__, p))
    bad = [x for x in launched if any(str(t) in ("x; rm -rf /", "$(id)", "http://evil.example/x", "-rf", "--help") for t in (x[0] if x and isinstance(x[0], (list, tuple)) else x))]
    assert not bad, bad
