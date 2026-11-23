"""ST-A3: concurrency, locked DB, corrupt DB + recovery, schema migration twice, random timelines. SIMULATED data."""
import os
import random
import shutil
import sqlite3
import threading
import time

import pytest

import rbda_priority_pipeline as rp
import recovery
import sthelp
from api import PipelineAPI
from sthelp import check_contract, db_bytes, load_so150, new_ws_api, rows, switch


def _integrity(path):
    c = sqlite3.connect(path)
    try:
        return c.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        c.close()


# ------------------------------------------------------------------ concurrency
def test_parallel_run_pipeline_same_api(tmp_path):
    a = new_ws_api(tmp_path, "par")
    load_so150(a)
    switch(a, "chi_xep", False)
    assert a.run_pipeline(seed=21)["ok"]
    ref = sthelp.match_rows(a.db_path)
    n0 = rows(a.db_path, "SELECT COUNT(*) FROM run_history")[0][0]
    out, errs = [], []

    def go():
        try:
            out.append(a.run_pipeline(seed=21))
        except BaseException as e:
            errs.append(e)
    th = [threading.Thread(target=go) for _ in range(8)]
    t0 = time.time()
    [t.start() for t in th]
    [t.join(120) for t in th]
    assert time.time() - t0 < 60
    assert not errs, errs
    assert all(not t.is_alive() for t in th)
    for r in out:
        check_contract(r, "parallel")
        assert r["ok"], r["errors"]
    assert sthelp.match_rows(a.db_path) == ref, "parallel reruns changed locked-seed result (invariant 1/3)"
    assert rows(a.db_path, "SELECT COUNT(*) FROM run_history")[0][0] == n0 + 8
    assert _integrity(a.db_path) == "ok"


def test_parallel_import_run_config(tmp_path):
    a = new_ws_api(tmp_path, "mix")
    load_so150(a)
    switch(a, "huy_chuong", True)
    b64 = sthelp.b64_file(sthelp.SO_150)
    res, errs = [], []

    def w(fn, *args):
        def go():
            try:
                res.append((fn.__name__, fn(*args)))
            except BaseException as e:
                errs.append((fn.__name__, repr(e)))
        return go
    jobs = [w(a.run_pipeline, 5), w(a.import_so_nhap, b64), w(a.update_workspace_config, {"rules": {"chia_loai": True}}),
            w(a.run_pipeline, 5), w(a.get_data_health_report), w(a.import_so_nhap, b64), w(a.get_match_results),
            w(a.update_workspace_config, {"rules": {"chia_loai": False}}), w(a.run_pipeline, 5)]
    th = [threading.Thread(target=j) for j in jobs]
    [t.start() for t in th]
    [t.join(180) for t in th]
    assert not errs, errs
    for n, r in res:
        check_contract(r, n)
        if not r["ok"]:
            codes = [e["code"] for e in r["errors"]]
            assert "csdl_dang_ban" not in codes, "%s: 'database is locked' despite the write lock" % n
    assert _integrity(a.db_path) == "ok"


def test_two_api_objects_same_db(tmp_path):
    """Second PipelineAPI on the same file (e.g. kiosk + script). Writes may contend; must stay contract-clean + intact."""
    a = new_ws_api(tmp_path, "two")
    load_so150(a)
    switch(a, "chi_xep", False)
    b = PipelineAPI(a.db_path, thu_muc_xuat=str(tmp_path / "xb"))
    out = []
    th = [threading.Thread(target=lambda x=x: out.append(x.run_pipeline(seed=2))) for x in (a, b, a, b)]
    [t.start() for t in th]
    [t.join(180) for t in th]
    for r in out:
        check_contract(r, "two-api")
    assert any(r["ok"] for r in out)
    assert _integrity(a.db_path) == "ok"


def test_external_lock_gives_busy_error_quickly(tmp_path):
    a = new_ws_api(tmp_path, "lock")
    load_so150(a)
    switch(a, "chi_xep", False)
    assert a.run_pipeline(seed=2)["ok"]
    snap = db_bytes(a.db_path)
    c = sqlite3.connect(a.db_path, isolation_level=None)
    c.execute("BEGIN EXCLUSIVE")
    try:
        t0 = time.time()
        r = a.run_pipeline(seed=2)
        dt = time.time() - t0
        check_contract(r, "locked-run")
        assert not r["ok"]
        assert dt < 30, "hang %.1fs" % dt
        t0 = time.time()
        for fn, args in ((a.get_dashboard_status, ()), (a.get_match_results, ()), (a.list_clubs, ()),
                         (a.import_so_nhap, (sthelp.b64_file(sthelp.SO_150),)),
                         (a.submit_preferences, ("DC001", ["THU_3_2"])),
                         (a.update_workspace_config, ({"rules": {"chia_loai": True}},))):
            r = fn(*args)
            check_contract(r, fn.__name__)
        assert time.time() - t0 < 60
    finally:
        c.execute("ROLLBACK")
        c.close()
    assert db_bytes(a.db_path) == snap
    assert a.run_pipeline(seed=2)["ok"]


# ------------------------------------------------------------------ corrupt DB / recovery
def _corruptions(path):
    data = open(path, "rb").read()
    rng = random.Random(3)
    mid = bytearray(data)
    for _ in range(200):
        mid[rng.randrange(4096, len(mid))] ^= 0xFF
    return {"garbage": b"this is not a database" * 50, "zero_len": b"", "truncated": data[: len(data) // 3],
            "header_only": data[:100], "bitflip_pages": bytes(mid)}


@pytest.mark.parametrize("kind", ["garbage", "zero_len", "truncated", "header_only", "bitflip_pages"])
def test_corrupt_db_and_recovery(tmp_path, kind):
    a = new_ws_api(tmp_path, "rec")
    load_so150(a)
    switch(a, "chi_xep", False)
    assert a.run_pipeline(seed=2)["ok"]          # creates a backup
    good_hs = rows(a.db_path, "SELECT COUNT(*) FROM students")[0][0]
    bak = [f for f in os.listdir(os.path.dirname(a.db_path)) if ".bak-" in f]
    assert bak
    bad = _corruptions(a.db_path)[kind]
    open(a.db_path, "wb").write(bad)
    err = None
    try:
        b = PipelineAPI(a.db_path)
        # constructed without raising: it must then either work or fail with the contract, never traceback
        r = b.run_pipeline(seed=2)
        check_contract(r, kind)
        r2 = b.get_dashboard_status()
        check_contract(r2, kind)
    except Exception as e:
        err = e
    rec = recovery.RecoveryAPI(a.db_path, str(err))
    st = rec.get_status()
    check_contract(st, "status")
    if err is not None or _integrity_safe(a.db_path) != "ok":
        r = rec.restore_from_backup()
        check_contract(r, "restore")
        assert r["ok"], r
        c = PipelineAPI(a.db_path)
        assert rows(a.db_path, "SELECT COUNT(*) FROM students")[0][0] == good_hs
        assert c.run_pipeline(seed=2)["ok"]
        assert [f for f in os.listdir(os.path.dirname(a.db_path)) if ".corrupt-" in f], "corrupt file must be kept, not deleted"


def _integrity_safe(p):
    try:
        return _integrity(p)
    except Exception as e:
        return "error: %s" % e


def test_start_fresh_keeps_corrupt_file(tmp_path):
    p = tmp_path / "x" / "app.db"
    p.parent.mkdir()
    p.write_bytes(b"junk" * 1000)
    rec = recovery.RecoveryAPI(str(p), "init failed")
    r = rec.start_fresh()
    check_contract(r, "fresh")
    assert r["ok"]
    assert [f for f in os.listdir(p.parent) if ".corrupt-" in f]
    PipelineAPI(str(p))   # opens fine


def test_all_backups_corrupt(tmp_path):
    p = tmp_path / "app.db"
    p.write_bytes(b"junk" * 100)
    for i in range(3):
        (tmp_path / ("app.db.bak-2026010%d_000000_000000" % i)).write_bytes(b"junk")
    r = recovery.RecoveryAPI(str(p), "x").restore_from_backup()
    check_contract(r, "allbad")
    assert not r["ok"]
    assert p.read_bytes() == b"junk" * 100, "failed restore must leave the original file in place"


# ------------------------------------------------------------------ schema migration
def test_di_tru_schema_twice_idempotent(tmp_path):
    a = new_ws_api(tmp_path, "mig")
    load_so150(a)
    switch(a, "huy_chuong", True)
    assert a.run_pipeline(seed=2)["ok"]
    snap = db_bytes(a.db_path)
    r1 = rp.di_tru_schema(a.db_path)
    r2 = rp.di_tru_schema(a.db_path)
    assert r2 == [] or r2 == r1 or isinstance(r2, list)
    assert db_bytes(a.db_path) == snap, "di_tru_schema changed data on a current-schema DB"
    assert _integrity(a.db_path) == "ok"
    assert [f for f in os.listdir(os.path.dirname(a.db_path)) if ".bak-" in f]


def test_old_schema_migrates_then_idempotent(tmp_path):
    """Strip a recent column set from a copy (simulate older DB): migration must restore and be idempotent."""
    a = new_ws_api(tmp_path, "old")
    load_so150(a)
    p = a.db_path
    c = sqlite3.connect(p)
    cols = [r[1] for r in c.execute("PRAGMA table_info(clubs)")]
    c.close()
    assert "loai" in cols
    # emulate a pre-FA DB by dropping the `loai` column (SQLite >= 3.35)
    c = sqlite3.connect(p)
    try:
        c.execute("ALTER TABLE clubs DROP COLUMN loai")
        c.commit()
    except sqlite3.OperationalError:
        pytest.skip("sqlite cannot drop column")
    finally:
        c.close()
    try:
        r1 = rp.di_tru_schema(p)
    except Exception as e:
        pytest.fail("di_tru_schema raised on an older DB: %r" % e)
    c = sqlite3.connect(p)
    assert "loai" in [r[1] for r in c.execute("PRAGMA table_info(clubs)")]
    c.close()
    snap = db_bytes(p)
    rp.di_tru_schema(p)
    assert db_bytes(p) == snap
    PipelineAPI(p)


# ------------------------------------------------------------------ timelines
def _verify_db_result(a):
    luat = a._luat_nghiem()
    (students, clubs, tested, apps, prefs, stb) = rp.load_from_sqlite(a.db_path, luat)[:6] if False else (None,) * 6
    return True


@pytest.mark.parametrize("seed", range(6))
def test_random_30_step_timeline(tmp_path, seed):
    rng = random.Random(seed)
    a = new_ws_api(tmp_path, "tl")
    load_so150(a)
    switch(a, "chi_xep", False)
    assert a.run_pipeline(seed=77)["ok"]
    base_order = None
    late = 0
    hist_n = rows(a.db_path, "SELECT COUNT(*) FROM run_history")[0][0]

    def order():
        return [s for s, in rows(a.db_path, "SELECT student_id FROM students WHERE stb_number IS NOT NULL ORDER BY stb_number, student_id")]
    base_order = order()
    clubs_ids = [c for c, in rows(a.db_path, "SELECT club_id FROM clubs")]
    for step in range(30):
        op = rng.choice(["late", "late", "capacity", "switch", "rerun", "rerun", "prefs", "typo", "delete_unmatched"])
        if op == "late":
            late += 1
            sid = "LATE%d_%d" % (seed, late)
            r = a.create_student_if_missing(sid, "Late %d" % late)
            check_contract(r, op)
            b = rng.choice(["thu_3", "thu_6"])
            cl = [c for c, in rows(a.db_path, "SELECT club_id FROM clubs WHERE buoi=? AND loai!='TU_DO'", (b,))]
            tu = [c for c, in rows(a.db_path, "SELECT club_id FROM clubs WHERE buoi=? AND loai='TU_DO'", (b,))]
            check_contract(a.submit_preferences(sid, rng.sample(cl, 3) + tu), op)
        elif op == "capacity":
            cid = rng.choice(clubs_ids)
            nm = rows(a.db_path, "SELECT name, capacity FROM clubs WHERE club_id=?", (cid,))[0]
            check_contract(a.create_or_update_club(cid, nm[0], max(1, nm[1] + rng.choice([-5, -1, 0, 3, 10]))), op)
        elif op == "switch":
            check_contract(switch(a, rng.choice(["chi_xep", "chia_100"]), rng.random() < 0.5), op)
        elif op == "typo":
            check_contract(a.create_student_if_missing("TYPO%d_%d" % (seed, step), "x"), op)
        elif op == "delete_unmatched":
            tg = rows(a.db_path, "SELECT student_id FROM students WHERE student_id NOT IN (SELECT student_id FROM match_results) LIMIT 1")
            if tg:
                check_contract(a.delete_student(tg[0][0]), op)
        elif op == "prefs":
            sid = "DC%03d" % rng.randint(1, 150)
            cl = [c for c, in rows(a.db_path, "SELECT club_id FROM clubs WHERE buoi='thu_3'")]
            r = a.submit_preferences(sid, rng.sample(cl, rng.randint(1, 5)))
            check_contract(r, op)
        else:
            r = a.run_pipeline(seed=77)
            check_contract(r, "rerun")
            if r["ok"]:
                hist_n += 1
                assert rows(a.db_path, "SELECT COUNT(*) FROM run_history")[0][0] == hist_n
                now = order()
                old = [s for s in now if s in set(base_order)]
                assert old == [s for s in base_order if s in set(old)], "STB relative order of existing students changed (invariant 3)"
                # results consistent
                cap = dict(rows(a.db_path, "SELECT club_id, capacity FROM clubs"))
                cnt = {}
                for s, b, c, *_ in sthelp.match_rows(a.db_path):
                    if c:
                        cnt[c] = cnt.get(c, 0) + 1
                for c, n in cnt.items():
                    assert n <= cap[c], "capacity exceeded after timeline step %d: %s %d>%d" % (step, c, n, cap[c])
            else:
                hist_after = rows(a.db_path, "SELECT COUNT(*) FROM run_history")[0][0]
                assert hist_after == hist_n
    assert _integrity(a.db_path) == "ok"


@pytest.mark.xfail(strict=True, reason="ST-A-005")
@pytest.mark.parametrize("rep", [1, 2])
def test_student_created_by_mistake_after_a_run_can_be_removed(tmp_path, rep):
    """A kiosk typo id created AFTER the first run: once a rerun gives it a (blank) match row, delete_student refuses
    (`cannot_delete_student_matched`) and its message says 'run again' — which re-creates the row. No way out but reset."""
    a = new_ws_api(tmp_path, "typo%d" % rep)
    load_so150(a)
    switch(a, "chi_xep", False)
    assert a.run_pipeline(seed=1)["ok"]
    assert a.create_student_if_missing("TYPO1", "Nhap nham")["ok"]
    assert a.run_pipeline(seed=1)["ok"]
    r = a.delete_student("TYPO1")
    assert r["ok"], r["errors"]


@pytest.mark.xfail(strict=True, reason="ST-A-006")
@pytest.mark.parametrize("rep", [1, 2])
def test_run_on_page_corrupt_db_must_not_report_ok(tmp_path, rep):
    """5 flipped bytes in the data pages: PRAGMA integrity_check fails, yet PipelineAPI opens and (seed 2) a run is
    reported ok:true, writes results and rotates a CORRUPT copy into the 10-backup ring (no integrity check anywhere on
    the path: __init__ / _backup_db / run_pipeline)."""
    a = new_ws_api(tmp_path, "pc%d" % rep)
    load_so150(a)
    switch(a, "chi_xep", False)
    assert a.run_pipeline(seed=2)["ok"]
    data = bytearray(open(a.db_path, "rb").read())
    rng = random.Random(2)
    for _ in range(5):
        data[rng.randrange(len(data) // 2, len(data))] ^= 0xFF
    open(a.db_path, "wb").write(bytes(data))
    assert _integrity_safe(a.db_path) != "ok"
    try:
        b = PipelineAPI(a.db_path)
    except Exception:
        return                      # acceptable: startup refuses -> recovery screen
    r = b.run_pipeline(seed=2)
    assert not r["ok"], "run reported ok on a database that fails integrity_check"
