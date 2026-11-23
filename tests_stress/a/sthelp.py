"""Shared helpers for ST-A tests. All data SIMULATED (random.Random(seed))."""
import base64
import os
import random
import sqlite3

import cau_hinh_ws as ch
import rbda_priority_pipeline as rp
from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SO_150 = os.path.join(GOC, "du_lieu_test", "SO_NHAP_DOI_CHE_DO_150HS.xlsx")

MODES = {
    "chi_xep": {"wharton": False, "fa_daa": False},
    "chia_100": {"wharton": True, "fa_daa": False},
    "huy_chuong": {"wharton": True, "fa_daa": True},
}


def b64_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def b64_bytes(b):
    return base64.b64encode(b).decode()


def new_api(tmp_path, name="a", **rules):
    api = PipelineAPI(str(tmp_path / (name + ".db")), thu_muc_xuat=str(tmp_path / ("xuat_" + name)))
    if rules:
        ch.ghi_cau_hinh(api.db_path, {"rules": rules})
    return api


def set_rules(api, **rules):
    return api.update_workspace_config({"rules": rules})


def rows(db_path, sql, args=()):
    c = sqlite3.connect(db_path)
    try:
        return c.execute(sql, args).fetchall()
    finally:
        c.close()


def match_rows(db_path):
    return rows(db_path, "SELECT * FROM match_results ORDER BY 1,2,3")


def db_bytes(db_path):
    """Content snapshot of ALL tables (order-independent) to prove a refusal wrote nothing."""
    c = sqlite3.connect(db_path)
    try:
        out = {}
        for (t,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall():
            out[t] = sorted(map(repr, c.execute('SELECT * FROM "%s"' % t).fetchall()))
        return out
    finally:
        c.close()


def check_contract(res, where=""):
    """Contract {ok,data,errors}; every code known in i18n_errors (vi+en) and renderable."""
    from i18n_errors import MESSAGES, format_message
    assert isinstance(res, dict), (where, type(res))
    assert {"ok", "data", "errors"} <= set(res), (where, list(res))
    assert isinstance(res["errors"], list), where
    entries = list(res["errors"])
    d = res.get("data")
    if isinstance(d, dict):
        for k in ("warnings", "canh_bao", "loi"):
            v = d.get(k)
            if isinstance(v, list):
                entries += [e for e in v if isinstance(e, dict) and "code" in e]
    if not res["ok"]:
        assert entries, (where, "ok:false without errors")
    for e in entries:
        assert isinstance(e, dict) and "code" in e and "params" in e, (where, e)
        assert e["code"] in MESSAGES, (where, "unknown code %r" % e["code"])
        assert MESSAGES[e["code"]].get("vi") and MESSAGES[e["code"]].get("en"), (where, e["code"])
        for lang in ("vi", "en"):
            txt = format_message(e["code"], e["params"], lang)
            assert isinstance(txt, str) and txt, (where, e)
            assert "{" not in txt or "}" not in txt, (where, "unfilled placeholder in %s: %r" % (lang, txt))
    return entries


def gen_instance(seed, n_students=None, n_buoi=None, max_clubs=6, tested_frac=0.4):
    """Random instance for run_rbda_nhieu_buoi. Returns dict of args."""
    rng = random.Random(seed)
    n = n_students if n_students is not None else rng.choice([3, 4, 5, 6, 8, 12, 20, 30, 50, 80])
    nb = n_buoi if n_buoi is not None else rng.randint(1, 4)
    students = {}
    for i in range(n):
        students["S%04d" % i] = {"stb": None,
                                 "reserve_group": rng.choice([None, None, "A", "B"])}
    sids = sorted(students)
    stb = rp.generate_stb_lottery(sids, rng.randint(0, 10 ** 6))
    for s in sids:
        students[s]["stb"] = stb[s]
    clubs = {}
    for b in range(nb):
        buoi = "thu_%d" % (b + 2)
        for k in range(rng.randint(1, max_clubs)):
            cap = rng.choice([1, 1, 2, 3, 5, 8, max(1, n // 3), n])
            res = rng.randint(0, cap) if rng.random() < 0.5 else 0
            clubs["C%d_%d" % (b, k)] = {"capacity": cap, "reserve_capacity": res,
                                        "reserve_group": rng.choice([None, "A", "B"]), "buoi": buoi}
    by = rp.nhom_theo_buoi(clubs)
    prefs = {}
    for s in sids:
        lst = []
        for buoi, cl in by.items():
            if rng.random() < 0.9:
                k = rng.randint(1, min(len(cl), 10))
                lst += rng.sample(cl, k)
        rng.shuffle(lst)  # order across sessions irrelevant (filtered per session)
        prefs[s] = lst[:10]
    dang_ky = {c: [] for c in clubs}
    scores = {c: {} for c in clubs}
    for s in sids:
        for c in prefs[s]:
            if rng.random() < tested_frac:
                dang_ky[c].append(s)
                scores[c][s] = round(rng.choice([0, 3, 5, 5, 7.5, 8, 10, rng.uniform(0, 10)]), 1)
    applicants = rp.hop_ung_vien(dang_ky, prefs)
    return dict(students=students, clubs=clubs, tested_scores=scores, applicants=applicants,
                preferences=prefs, stb_lottery=stb,
                is_reserve_eligible_fn=rp.default_reserve_eligible_fn(students, clubs))


def new_ws_api(tmp_path, name="ws", cfg=None):
    """Workspace-mode API, as the app uses it (update_workspace_config works only here)."""
    import workspace as ws
    goc = tmp_path / ("goc_" + name)
    goc.mkdir()
    slug = ws.tao(str(goc), name, cfg)
    return PipelineAPI(ws.duong_dan_db(str(goc), slug), thu_muc_xuat=str(tmp_path / ("x_" + name)),
                       thu_muc_goc_ws=str(goc), ws_da_chon=True)


def switch(api, mode, chia_loai):
    r = api.update_workspace_config({"rules": dict(MODES[mode], chia_loai=chia_loai)})
    return r


def load_so150(api):
    """Import the shared Sổ in Huy chương mode (protocol), then return to the requested state."""
    r = switch(api, "huy_chuong", False)
    assert r["ok"], r
    r = api.import_so_nhap(b64_file(SO_150))
    assert r["ok"], r
    return r
