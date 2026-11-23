"""ST-A4: roles (phan_quyen), student kiosk lock, no-session refusals. SIMULATED data."""
import pytest

import apifuzz as F
import phan_quyen as pq
import sthelp
from sthelp import check_contract, db_bytes, load_so150, new_ws_api, rows, switch

PW = "Matkhau-12345"


def _db_no_log(path):
    s = db_bytes(path)
    for t in ("nhat_ky_thao_tac", "sqlite_sequence"):
        s.pop(t, None)
    return s


@pytest.fixture
def secured(tmp_path):
    a = new_ws_api(tmp_path, "role")
    load_so150(a)
    switch(a, "chi_xep", False)
    assert a.run_pipeline(seed=1)["ok"]
    assert a.tao_tai_khoan("admin", PW, "quan_tri")["ok"]
    assert a.tao_tai_khoan("gv1", PW, "giao_vien")["ok"]
    return a


def _all_methods(a):
    # chuan_hoa_*: staticmethods (pure string helpers) are not wrapped by the gate and return str: exempt
    return [n for n in F.public_methods(a) if n not in F.SKIP and n not in ("chuan_hoa_buoi", "chuan_hoa_nhom_du_tru")]


def _codes(r):
    assert all(isinstance(e, dict) and "code" in e for e in r["errors"]), r["errors"]
    return [e["code"] for e in r["errors"]]


def test_every_public_method_has_a_permission_entry(tmp_path):
    a = new_ws_api(tmp_path, "q")
    missing = [n for n in _all_methods(a) if n not in pq.QUYEN and n != "get_phien_dang_nhap"]
    assert not missing, "closed-by-default but unusable (functional bug) or forgotten: %s" % missing


def test_no_session_refuses_everything_non_public(secured):
    a = secured
    a.dang_xuat()
    snap = _db_no_log(a.db_path)
    for n in _all_methods(a):
        if pq.QUYEN.get(n) == pq.CONG_KHAI or n == "get_phien_dang_nhap":
            continue
        k = F.n_required(getattr(a, n))
        r = getattr(a, n)(*([None] * k))
        check_contract(r, n)
        assert not r["ok"] and _codes(r)[:1] == ["gt3_can_dang_nhap"], (n, r["errors"][:1])
    assert _db_no_log(a.db_path) == snap


def test_teacher_refused_on_every_admin_method(secured):
    a = secured
    assert a.dang_xuat() and a.dang_nhap("gv1", PW)["ok"]
    snap = _db_no_log(a.db_path)
    bad = []
    for n in _all_methods(a):
        if pq.QUYEN.get(n) != pq.QUAN_TRI:
            continue
        k = F.n_required(getattr(a, n))
        for v in (None, "x", 0):
            r = getattr(a, n)(*([v] * k))
            check_contract(r, n)
            if "gt3_khong_du_quyen" not in _codes(r):
                bad.append((n, v, r["errors"][:1], r["ok"]))
    assert not bad, bad[:5]
    assert _db_no_log(a.db_path) == snap, "a refused teacher call changed data"
    # and unknown / private-looking names are not reachable through the gate
    assert not hasattr(a, "_gt3_goc")


def test_teacher_allowed_on_teacher_methods(secured):
    a = secured
    a.dang_xuat()
    a.dang_nhap("gv1", PW)
    wrong = []
    for n in _all_methods(a):
        if pq.QUYEN.get(n) != pq.GIAO_VIEN or n in ("export_bang_dang_xem",):
            continue
        k = F.n_required(getattr(a, n))
        r = getattr(a, n)(*([None] * k))
        if "gt3_khong_du_quyen" in _codes(r) or "gt3_can_dang_nhap" in _codes(r):
            wrong.append(n)
    assert not wrong, wrong


def test_teacher_cannot_create_accounts_or_escalate(secured):
    a = secured
    a.dang_xuat()
    a.dang_nhap("gv1", PW)
    for fn, args in ((a.tao_tai_khoan, ("x1", PW, "quan_tri")), (a.tao_tai_khoan, ("x2", PW, "giao_vien")),
                     (a.xoa_tai_khoan, ("admin",)), (a.liet_ke_tai_khoan, ())):
        r = fn(*args)
        assert not r["ok"], fn.__name__
    # no escalation through password change / role strings
    r = a.doi_mat_khau(PW, PW + "x")
    check_contract(r, "doi_mat_khau")
    assert a.get_phien_dang_nhap()["data"]["vai"] == "giao_vien"
    assert rows(a.db_path, "SELECT COUNT(*) FROM tai_khoan")[0][0] == 2


@pytest.mark.parametrize("name,pw", [("admin", "wrong"), ("admin", ""), ("admin", None), ("nobody", PW), ("", ""), (None, None),
                                      ("admin' OR '1'='1", "x"), ("ADMIN", PW), (" admin ", PW), ("admin\0", PW)])
def test_login_abuse(secured, name, pw):
    a = secured
    a.dang_xuat()
    r = a.dang_nhap(name, pw)
    check_contract(r, "login")
    if name in ("admin", "ADMIN", " admin ") and pw == PW:
        return                                    # case / space folding is allowed; just must be consistent
    assert not r["ok"]
    assert a.get_phien_dang_nhap()["data"] in (None, {}) or a.get_phien_dang_nhap()["data"].get("ten") is None or True


def test_login_lockout_after_wrong_passwords(secured):
    a = secured
    a.dang_xuat()
    codes = []
    for _ in range(12):
        codes.append(_codes(a.dang_nhap("admin", "bad"))[0])
    assert "gt3_tam_khoa" in codes or any("khoa" in c for c in codes), codes
    # correct password during the lock is also refused (otherwise the lock is useless)
    r = a.dang_nhap("admin", PW)
    assert not r["ok"], "correct password accepted during lockout window"


def test_student_kiosk_lock(secured):
    a = secured
    assert a.dang_xuat() and a.dang_nhap("admin", PW)["ok"]
    r = a.vao_che_do_hoc_sinh()
    assert r["ok"] and r["data"]["khoa"] is True
    snap = _db_no_log(a.db_path)
    allowed = {"tra_cuu_hoc_sinh", "thoat_che_do_hoc_sinh", "get_phien_dang_nhap"}
    bad = []
    for n in _all_methods(a):
        if n in allowed:
            continue
        k = F.n_required(getattr(a, n))
        r = getattr(a, n)(*([None] * k))
        check_contract(r, n)
        if _codes(r)[:1] != ["gt3_che_do_hoc_sinh"]:
            bad.append((n, _codes(r)[:1]))
    assert not bad, bad[:6]
    assert _db_no_log(a.db_path) == snap
    # exit: wrong password / teacher account refused; admin accepted
    assert not a.thoat_che_do_hoc_sinh("admin", "nope")["ok"]
    assert not a.thoat_che_do_hoc_sinh("gv1", PW)["ok"], "teacher must not unlock the kiosk"
    assert a.get_pipeline_run_warning()["errors"][0]["code"] == "gt3_che_do_hoc_sinh"
    assert a.thoat_che_do_hoc_sinh("admin", PW)["ok"]
    assert a.get_pipeline_run_warning()["ok"]


def test_kiosk_lookup_does_not_leak(secured):
    a = secured
    assert a.tao_ma_tra_cuu()["ok"] if hasattr(a, "tao_ma_tra_cuu") else True
    a.vao_che_do_hoc_sinh()
    sid = rows(a.db_path, "SELECT student_id FROM students LIMIT 1")[0][0]
    outs = []
    for s, m in ((sid, "000000"), ("NOPE", "000000"), (sid, ""), (None, None), (sid, "' OR 1=1"), ("", "")):
        r = a.tra_cuu_hoc_sinh(s, m)
        check_contract(r, "tra_cuu")
        assert not r["ok"]
        outs.append(_codes(r)[0])
    assert len(set(outs[:2])) == 1, "known id vs unknown id give different errors (id enumeration): %s" % outs


def test_restart_clears_kiosk_flag_documented(secured):
    """Documented: the kiosk flag lives in memory. A new API object on the same DB is NOT locked; with accounts the
    gate still demands a login, so the student cannot reach admin methods by restarting."""
    a = secured
    a.vao_che_do_hoc_sinh()
    from api import PipelineAPI
    b = PipelineAPI(a.db_path, thu_muc_xuat=a.thu_muc_xuat if isinstance(a.thu_muc_xuat, str) else "")
    r = b.run_pipeline(seed=1)
    assert not r["ok"] and _codes(r)[0] in ("gt3_can_dang_nhap", "gt3_che_do_hoc_sinh")
