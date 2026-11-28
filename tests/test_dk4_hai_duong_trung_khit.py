"""DK4-L3: hai đường cho kết quả TRÙNG KHÍT từng dòng `match_results` (3 bộ dữ liệu MÔ PHỎNG x 20 seed).

Đường A: `dk_chot_va_xep` (dữ liệu đăng ký -> nhập -> xếp).
Đường B: đường cũ — `dk_xuat_so_nhap` ghi tệp, bật luật, `import_so_nhap`, `run_pipeline`."""
import base64
import random
import shutil
import sqlite3

import pytest

import cau_hinh_ws as ch
from api import PipelineAPI

SEEDS = range(20)
KICH_CO = {0: 14, 1: 22, 2: 30}      # số học sinh mỗi bộ


def ok(r):
    assert r["ok"], r
    return r["data"]


def _xay(thu_muc, ky):
    """Bộ dữ liệu mô phỏng `ky`: 2 buổi, mỗi buổi 1 Tự do + 1 Giới hạn + 1 Tuyển chọn, điểm ngẫu nhiên (cố định theo `ky`)."""
    rng = random.Random(1000 + ky)
    api = PipelineAPI(str(thu_muc / "app.db"))
    ok(api.dk_khoi_tao("matkhau", "TRUONG", ["T2", "T3"], [10, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for t in ("P1", "P2", "P3", "P4", "P5", "P6"):
        ok(api.dk_phong_luu(qt, t, 30))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    n_gv = 6
    pin = ok(api.dk_gv_tao_hang_loat(qt, "\n".join("GV%d" % i for i in range(n_gv))))["da_tao"]
    tok = [ok(api.dk_dang_nhap("giao_vien", x["ten"], x["pin"]))["token"] for x in pin]
    ids, i = {}, 0
    for b in ("T2", "T3"):
        for loai, ct, kw in (("Tự do", 20, {}), ("Giới hạn", 5, {}), ("Tuyển chọn", 5, {"diem_san": 5})):
            ten = "%s %s" % (loai, b)
            ids[ten] = ok(api.dk_clb_luu(tok[i], {"ten": ten, "buoi": b, "loai": loai, "phong_id": i + 1, "chi_tieu": ct,
                                                  "khoi_tu": 10, "khoi_den": 12, **kw}))["clb_id"]
            ok(api.dk_clb_duyet(qt, ids[ten], "duyet"))
            i += 1
    n = KICH_CO[ky]
    pins = ok(api.dk_hs_nap_danh_sach(qt, "\n".join("S%03d\tHS %d\t10A%d" % (k, k, k % 3) for k in range(n))))["pin"]
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    thi = []
    for p in pins:
        h = ok(api.dk_dang_nhap("hoc_sinh", p["ma"], p["pin"]))["token"]
        nv = []
        for b in ("T2", "T3"):
            ds = [ids["%s %s" % (l, b)] for l in ("Tự do", "Giới hạn", "Tuyển chọn")]
            rng.shuffle(ds)
            ds = ds[:rng.choice((2, 3))]
            if ids["Tự do " + b] not in ds:
                ds.append(ids["Tự do " + b])
            nv += [{"clb_id": c, "thi": c == ids["Tuyển chọn " + b] and rng.random() < 0.8} for c in ds]
        ok(api.dk_hs_luu(h, nv))
        thi += [(p["ma"], x["clb_id"]) for x in nv if x["thi"]]
    ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
    for ma_hs, c in thi:
        ok(api.dk_diem_dat(qt, ma_hs, c, str(rng.randint(3, 10))))
    return api


def _kq(api):
    c = sqlite3.connect(api.db_path)
    try:
        return c.execute("SELECT student_id, buoi, club_id, round_num, matched_tier, rank_in_student_pref "
                         "FROM match_results ORDER BY student_id, buoi").fetchall()
    finally:
        c.close()


@pytest.fixture(scope="module", params=[0, 1, 2], ids=["bo0", "bo1", "bo2"])
def bo(request, tmp_path_factory):
    g = tmp_path_factory.mktemp("goc%d" % request.param)
    _xay(g, request.param).db_path    # noqa: B018  (dựng xong là có app.db)
    return g, request.param


@pytest.mark.parametrize("seed", SEEDS)
def test_hai_duong_trung_khit(bo, tmp_path, seed):
    goc, ky = bo
    da, db = tmp_path / "a", tmp_path / "b"
    da.mkdir(), db.mkdir()
    shutil.copy(goc / "app.db", da / "app.db")
    shutil.copy(goc / "app.db", db / "app.db")
    a, b = PipelineAPI(str(da / "app.db")), PipelineAPI(str(db / "app.db"))
    qa = ok(a.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    qb = ok(b.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    ok(a.dk_chot_va_xep(qa, seed))
    ok(b.dk_xuat_so_nhap(qb, str(db / "so.xlsx")))
    ch.ghi_cau_hinh(b.db_path, {"rules": {"fa_daa": True, "wharton": True}})
    with open(db / "so.xlsx", "rb") as f:
        r = b.import_so_nhap(base64.b64encode(f.read()).decode("ascii"))
    assert r["ok"] and r["errors"] == [], r
    assert b.run_pipeline(seed=seed)["ok"]
    ka, kb = _kq(a), _kq(b)
    assert len(ka) >= KICH_CO[ky] and ka == kb
