"""ST-A3: fault injection into every pipeline stage -> full rollback, backup exists, run_history append-only. SIMULATED data."""
import glob
import os
import sqlite3

import pytest

import api as api_mod
import fa_daa
import sthelp
from sthelp import check_contract, db_bytes, load_so150, new_ws_api, rows, switch


class Boom(Exception):
    pass


def _fresh(tmp_path, mode="chi_xep", cl=False, run_first=True):
    a = new_ws_api(tmp_path, "f")
    load_so150(a)
    switch(a, mode, cl)
    if run_first:
        assert a.run_pipeline(seed=11)["ok"]
    return a


def _backups(a):
    return glob.glob(os.path.join(os.path.dirname(a.db_path), "*.db.bak-*"))


def _n_hist(a):
    return rows(a.db_path, "SELECT COUNT(*) FROM run_history")[0][0]


def _raise(*a, **k):
    raise Boom("injected")


def _raise_os(*a, **k):
    raise OSError(28, "No space left on device")


STAGES = {
    "validate": (api_mod, "validate_data_integrity", _raise),
    "lock_generate": (api_mod, "generate_stb_lottery", _raise),
    "lock_insert_new": (api_mod, "chen_stb_cho_hoc_sinh_moi", _raise),
    "solve": (api_mod, "run_rbda_nhieu_buoi", _raise),
    "solve_fa": (fa_daa, "chay_fa_daa", _raise),
    "verify_sanity": (api_mod, "sanity_check_result", _raise),
    "verify_stability": (api_mod, "verify_stability", _raise),
    "write_rows": (api_mod, "cac_dong_match_results", _raise),
    "write_rows_diskfull": (api_mod, "cac_dong_match_results", _raise_os),
    "write_meta": (api_mod, "luat_xep_de_ghi", _raise),
}


@pytest.mark.parametrize("stage", sorted(STAGES))
@pytest.mark.parametrize("first", [False, True])
def test_fault_rolls_back_everything(tmp_path, monkeypatch, stage, first):
    mode = "huy_chuong" if stage == "solve_fa" else "chi_xep"
    a = _fresh(tmp_path, mode, False, run_first=first)
    if first:
        # change data so the stage under test is actually reached (new student -> STB supplement)
        assert a.create_student_if_missing("LATE1", "Late One")["ok"]
        assert a.submit_preferences("LATE1", [r[0] for r in rows(a.db_path, "SELECT club_id FROM clubs WHERE buoi='thu_3' LIMIT 3")])["ok"]
    snap = db_bytes(a.db_path)
    n0 = _n_hist(a)
    mod, name, fn = STAGES[stage]
    monkeypatch.setattr(mod, name, fn)
    res = a.run_pipeline(seed=11, force_redraw_stb=False)
    monkeypatch.undo()
    check_contract(res, stage)
    # stages that MUST be reached in this scenario -> the injected fault must fail the run
    must = {"validate", "solve", "verify_sanity", "verify_stability", "write_rows", "write_rows_diskfull", "write_meta"}
    must |= {"lock_generate"} if (not first) else set()
    must |= {"lock_insert_new"} if first else set()
    must |= {"solve_fa"}
    if stage in must:
        assert not res["ok"], "fault in %s was swallowed: run reported ok" % stage
    if not res["ok"]:
        assert db_bytes(a.db_path) == snap, "stage %s: DB changed although run failed" % stage
        assert _n_hist(a) == n0
        assert _backups(a), "no backup file after a failed run (backup happens first)"
        steps = [s.get("step") for s in (res["data"] or {}).get("steps", [])] if isinstance(res.get("data"), dict) else []
    # a following clean run works and appends exactly one run_history row
    n1 = _n_hist(a)
    assert n1 == n0 + (1 if res["ok"] else 0)
    ok = a.run_pipeline(seed=11)
    assert ok["ok"], ok["errors"]
    assert _n_hist(a) == n1 + 1


def test_stage_not_reached_is_reported(tmp_path, monkeypatch):
    """Sanity: injected faults really reach the pipeline (the fault on a stage that the run uses must give ok:false)."""
    a = _fresh(tmp_path, "chi_xep", False, run_first=False)
    monkeypatch.setattr(api_mod, "run_rbda_nhieu_buoi", _raise)
    res = a.run_pipeline(seed=1)
    assert not res["ok"]
    monkeypatch.undo()
    # fresh DB + failed first run: no orphan STB lock, no results
    assert rows(a.db_path, "SELECT COUNT(*) FROM match_results")[0][0] == 0
    st = a.get_stb_lock_status()
    assert st["ok"] and not st["data"].get("locked"), st


def test_backup_failure_does_not_block(tmp_path, monkeypatch):
    a = _fresh(tmp_path, run_first=False)
    monkeypatch.setattr(api_mod.PipelineAPI, "_backup_db", _raise_os)
    res = a.run_pipeline(seed=1)
    check_contract(res, "backup")
    assert res["ok"], res["errors"]        # documented: backup is a safety net, not a precondition
    steps = {s["step"]: s["status"] for s in res["data"]["steps"]}
    assert steps.get("backup") == "error"


def test_export_failure_keeps_committed_results(tmp_path, monkeypatch):
    a = _fresh(tmp_path, run_first=False)
    monkeypatch.setattr(api_mod.PipelineAPI, "_xuat_match_results_csv", _raise_os)
    res = a.run_pipeline(seed=1)
    check_contract(res, "export")
    assert rows(a.db_path, "SELECT COUNT(*) FROM match_results")[0][0] == 300
    assert _n_hist(a) == 1
    steps = {s["step"]: s["status"] for s in res["data"]["steps"]} if res["ok"] else {}
    assert (not res["ok"]) or steps.get("export") == "error"


@pytest.mark.parametrize("exc", [KeyboardInterrupt, SystemExit, MemoryError, RecursionError])
def test_baseexception_rolls_back(tmp_path, monkeypatch, exc):
    a = _fresh(tmp_path, run_first=True)
    snap = db_bytes(a.db_path)

    def f(*x, **k):
        raise exc()
    monkeypatch.setattr(api_mod, "cac_dong_match_results", f)
    try:
        a.run_pipeline(seed=11)
    except BaseException:
        pass
    monkeypatch.undo()
    assert db_bytes(a.db_path) == snap
    assert a.run_pipeline(seed=11)["ok"]     # lock released: next run is not stuck
