"""ST-A1: algorithm properties on random instances (>= 500 seeds). SIMULATED data."""
import itertools
import random
import zlib

import pytest

import rbda_priority_pipeline as rp
import sthelp

SEEDS = list(range(520))


def _run(inst, seed=7):
    return rp.run_rbda_nhieu_buoi(**inst, seed=seed)


@pytest.mark.parametrize("seed", SEEDS)
def test_properties_random(seed):
    inst = sthelp.gen_instance(seed)
    k = _run(inst)
    clubs, prefs = inst["clubs"], inst["preferences"]
    # stability (all sessions)
    vs = rp.verify_stability_tuan(k, clubs, prefs, inst["is_reserve_eligible_fn"])
    assert all(not v for v in vs.values()), vs
    by = rp.nhom_theo_buoi(clubs)
    for sid, per in k.assignment.items():
        # at most one club per student per session (dict shape) and club belongs to session; was ranked
        assert set(per) == set(by), (sid, per)
        for buoi, cid in per.items():
            if cid is not None:
                assert clubs[cid]["buoi"] == buoi
                assert cid in prefs[sid], "student placed in an unranked club"
    # capacity / reserve bounds
    cnt, res = {}, {}
    for buoi, kq in k.per_buoi.items():
        for sid, cid in kq.assignment.items():
            if cid is None:
                continue
            cnt[cid] = cnt.get(cid, 0) + 1
            if kq.matched_tier.get(sid) == "reserve":
                res[cid] = res.get(cid, 0) + 1
                assert inst["is_reserve_eligible_fn"](sid, cid)
    for cid, c in clubs.items():
        assert cnt.get(cid, 0) <= c["capacity"], cid
        assert res.get(cid, 0) <= c["reserve_capacity"], cid
    # unmatched student must have been rejected by every ranked club of that session (no empty-seat waste)
    for buoi, kq in k.per_buoi.items():
        for sid, cid in kq.assignment.items():
            if cid is None:
                for c in prefs[sid]:
                    if clubs[c]["buoi"] == buoi:
                        held = [s for s, x in kq.assignment.items() if x == c]
                        assert len(held) >= 1 or clubs[c]["capacity"] == 0, (sid, c)


@pytest.mark.parametrize("seed", SEEDS[:200])
def test_determinism_and_pref_permutation_invariance(seed):
    inst = sthelp.gen_instance(seed)
    a = _run(inst)
    b = _run(inst)
    assert a.assignment == b.assignment
    # invariant 2: shuffle the ORDER of students/applicants dicts and prefs insertion; base_rank must not move
    rng = random.Random(seed)
    inst2 = dict(inst)
    sids = list(inst["students"])
    rng.shuffle(sids)
    inst2["students"] = {s: inst["students"][s] for s in sids}
    inst2["applicants"] = {c: rng.sample(v, len(v)) for c, v in inst["applicants"].items()}
    c = _run(inst2)
    assert c.assignment == a.assignment
    for buoi in a.per_buoi:
        assert a.per_buoi[buoi].base_rank == c.per_buoi[buoi].base_rank


def _ch(c, held, inst, rankmap):
    clubs = inst["clubs"]
    el = inst["is_reserve_eligible_fn"]
    acc, _ = rp.club_choice_function(list(held), clubs[c]["capacity"], clubs[c]["reserve_capacity"],
                                     lambda s: el(s, c), rankmap[c])
    return set(acc)


def _stable_matchings(inst, buoi):
    clubs = {c: v for c, v in inst["clubs"].items() if v["buoi"] == buoi}
    prefs = {s: [c for c in l if c in clubs] for s, l in inst["preferences"].items()}
    sids = sorted(prefs)
    rankmap = {c: {s: i for i, s in enumerate(rp.compute_club_priority(
        c, inst["applicants"].get(c, []), inst["tested_scores"].get(c, {}), inst["stb_lottery"]))}
        for c in clubs}
    out = []
    for combo in itertools.product(*[[None] + prefs[s] for s in sids]):
        mu = dict(zip(sids, combo))
        held = {c: {s for s in sids if mu[s] == c} for c in clubs}
        if any(_ch(c, held[c], inst, rankmap) != held[c] for c in clubs):
            continue
        ok = True
        for s in sids:
            lst = prefs[s]
            better = lst if mu[s] is None else lst[:lst.index(mu[s])]
            for c in better:
                if s in _ch(c, held[c] | {s}, inst, rankmap):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            out.append((mu, prefs))
    return out


@pytest.mark.parametrize("seed", range(120))
def test_student_optimal_bruteforce(seed):
    rng = random.Random(seed)
    inst = sthelp.gen_instance(seed + 5000, n_students=rng.randint(2, 6), n_buoi=1, max_clubs=3)
    # restrict to <= 3 clubs
    stab = _stable_matchings(inst, "thu_2")
    assert stab, "no stable matching found by brute force"
    k = _run(inst)
    da = k.assignment
    for (mu, prefs) in stab:
        for s, c in mu.items():
            lst = prefs[s]
            got = da[s]["thu_2"]
            rg = lst.index(got) if got in lst else len(lst)
            rm = lst.index(c) if c in lst else len(lst)
            assert rg <= rm, (seed, s, "DA gives %s but stable matching gives %s" % (got, c))
    # DA outcome itself is among the stable matchings
    da1 = {s: da[s]["thu_2"] for s in da}
    assert any(mu == da1 for mu, _ in stab)


def test_large_800_students():
    inst = sthelp.gen_instance(99, n_students=800, n_buoi=2, max_clubs=10)
    k = _run(inst)
    vs = rp.verify_stability_tuan(k, inst["clubs"], inst["preferences"], inst["is_reserve_eligible_fn"])
    assert all(not v for v in vs.values())


# ---- invariant 3: STB ----
def test_stb_crc32_and_hashseed_independent():
    import subprocess, sys, os
    code = ("import sys;sys.path.insert(0,%r);import rbda_priority_pipeline as r;"
            "k=r.run_rbda_nhieu_buoi.__defaults__;print(sorted(r.sinh_stb_theo_buoi("
            "r.generate_stb_lottery(['a','b','c','d','e'],3),['thu_2','thu_3'],9,'stb_ngay').items()))"
            % sthelp.GOC)
    outs = set()
    for hs in ("0", "1", "12345"):
        env = dict(os.environ, PYTHONHASHSEED=hs)
        outs.add(subprocess.check_output([sys.executable, "-c", code], env=env, text=True))
    assert len(outs) == 1
    assert rp._seed_cua_buoi(5, "thu_3") == (5 + zlib.crc32(b"thu_3")) % (2 ** 31)


@pytest.mark.parametrize("seed", range(100))
def test_late_arrivals_keep_relative_order(seed):
    rng = random.Random(seed)
    n = rng.randint(0, 60)
    old = ["O%03d" % i for i in range(n)]
    lot = rp.generate_stb_lottery(old, seed) if n else {}
    thu_tu = sorted(old, key=lambda s: lot[s])
    new = ["N%03d" % i for i in range(rng.randint(0, 20))]
    out = rp.chen_stb_cho_hoc_sinh_moi(thu_tu, new, seed)
    assert sorted(out.values()) == list(range(n + len(new)))
    assert sorted(thu_tu, key=lambda s: out[s]) == thu_tu
    assert out == rp.chen_stb_cho_hoc_sinh_moi(thu_tu, new, seed)
    # input order of the newcomers must not matter
    assert out == rp.chen_stb_cho_hoc_sinh_moi(thu_tu, list(reversed(new)), seed)


def test_late_arrival_uniform_position():
    # each of 4 slots for 1 newcomer among 3 old: roughly uniform over 4000 seeds
    old = ["a", "b", "c"]
    cnt = [0] * 4
    for sd in range(4000):
        cnt[rp.chen_stb_cho_hoc_sinh_moi(old, ["z"], sd)["z"]] += 1
    assert min(cnt) > 800, cnt


@pytest.mark.parametrize("seed", range(40))
def test_chi_buoi_equals_full_week(seed):
    inst = sthelp.gen_instance(seed + 900, n_buoi=3)
    full = _run(inst, seed)
    for b in list(full.per_buoi):
        one = rp.run_rbda_nhieu_buoi(**inst, seed=seed, chi_buoi=[b])
        assert {s: v[b] for s, v in one.assignment.items()} == {s: v[b] for s, v in full.assignment.items()}
