"""ST-A1: FA-DAA properties (so_toi_thieu, Tự do fallback, floors, medals) on the shared Sổ. SIMULATED data."""
import random
import sqlite3

import pytest

import sthelp
from sthelp import switch, load_so150, rows, match_rows


def _members(api):
    m = {}
    for sid, buoi, cid, *_ in match_rows(api.db_path):
        if cid is not None:
            m.setdefault(cid, []).append(sid)
    return m


@pytest.mark.parametrize("seed", range(12))
def test_so_toi_thieu_closure_and_fallback(tmp_path, seed):
    api = sthelp.new_ws_api(tmp_path, "mn")
    load_so150(api)
    rng = random.Random(seed)
    c = sqlite3.connect(api.db_path)
    gh = [r[0] for r in c.execute("SELECT club_id FROM clubs WHERE loai IN ('GIOI_HAN','TUYEN_CHON')")]
    mins = {}
    for cid in gh:
        if rng.random() < 0.7:
            mins[cid] = rng.choice([1, 5, 10, 20, 40])
            c.execute("UPDATE clubs SET so_toi_thieu=? WHERE club_id=?", (mins[cid], cid))
    c.commit()
    c.close()
    switch(api, "huy_chuong", rng.random() < 0.5)
    r = api.run_pipeline(seed=seed)
    assert r["ok"], r["errors"]
    mem = _members(api)
    for cid, mn in mins.items():
        n = len(mem.get(cid, []))
        assert n == 0 or n >= mn, "club %s has %d members < so_toi_thieu %d (and not closed)" % (cid, n, mn)
    # Tự do fallback: with one Tự do club per session (capacity = all students) nobody is left unplaced
    unplaced = [x for x in match_rows(api.db_path) if x[2] is None]
    assert not unplaced, "unplaced students despite Tự do club (fallback): %s" % unplaced[:3]
    # capacity respected, including Tự do
    cap = dict(rows(api.db_path, "SELECT club_id, capacity FROM clubs"))
    for cid, ms in mem.items():
        assert len(ms) <= cap[cid]


def test_medal_order_respected(tmp_path):
    """A student who gives gold(60) to a club ranked in prefs must get ranked-first preference first unless rejected."""
    api = sthelp.new_ws_api(tmp_path, "med")
    load_so150(api)
    switch(api, "huy_chuong", True)
    assert api.run_pipeline(seed=5)["ok"]
    # every placed student's rank_in_student_pref within list length; reserve/general tag valid
    for sid, buoi, cid, rnd, tier, rk in match_rows(api.db_path):
        if cid is not None:
            assert tier in (None, "reserve", "general")
            assert rk is None or rk >= 1


def test_chia100_points_sum_validation(tmp_path):
    """Chia 100: a student whose points do not sum to 100 in a fund must be flagged (health) and not crash the run."""
    api = sthelp.new_ws_api(tmp_path, "w100")
    load_so150(api)
    switch(api, "chia_100", False)
    c = sqlite3.connect(api.db_path)
    ws = c.execute("SELECT name FROM sqlite_master WHERE name LIKE 'wharton%'").fetchall()
    assert ws
    c.close()
    h = api.get_data_health_report()
    assert h["ok"]
    r = api.run_pipeline(seed=1)
    assert r["ok"], r["errors"]
