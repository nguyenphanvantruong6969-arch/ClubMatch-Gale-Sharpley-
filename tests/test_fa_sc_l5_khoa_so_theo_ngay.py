# -*- coding: utf-8 -*-
"""FA-SC-L5: khoá thứ tự bốc thăm THEO NGÀY ở lần chạy đầu (bảng `stb_buoi`).

VẤN ĐỀ (F15). Bộ số gốc đã khoá và em đến muộn được chèn đều (`chen_stb_cho_hoc_sinh_moi`), nhưng thứ tự TỪNG NGÀY
vốn là hoán vị VỊ TRÍ của bộ số gốc: thêm một em làm dịch vị trí cả dàn, nên ở mỗi ngày các em CŨ đổi chỗ cho nhau.
Đo trên bản cũ: d12 20/51 em cũ đổi CLB, d16 18/38.

LUẬT MỚI. Lần chạy đầu gọi đúng `sinh_stb_theo_buoi` rồi LƯU thứ tự từng ngày; các lần sau giữ em cũ và chèn đều em mới
vào TỪNG ngày. Tệp này canh bảy điều của `kiem_nhan`.
"""
import io
import os
import sqlite3

import pytest

import rbda_priority_pipeline as rb
from _wharton import tat_wharton  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUOI = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6"]


@pytest.fixture
def api(api):
    tat_wharton(api)
    return api


def _nap_nhieu_buoi(api):
    for i, ten in enumerate(["danh_sach_CLB", "chon_CLB_muon_thi", "xep_hang_nguyen_vong"], start=1):
        with io.open(os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi", "NHIEUBUOI_0%d_%s.csv" % (i, ten)),
                     encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]


def _sql(api, cau, tham=()):
    conn = sqlite3.connect(api.db_path)
    try:
        return conn.execute(cau, tham).fetchall()
    finally:
        conn.close()


def _luu(api):
    """{buoi: [mã theo thứ tự đã lưu]}"""
    ra = {}
    for b, s, so in _sql(api, "SELECT buoi, student_id, so FROM stb_buoi ORDER BY buoi, so, student_id"):
        ra.setdefault(b, []).append(s)
    return ra


def _them_em(api, ma):
    assert api.create_student_if_missing(ma, "Em " + ma)["ok"]


def _ket_qua(api):
    return _sql(api, "SELECT * FROM match_results ORDER BY student_id, buoi")


def _thu_tu(so):
    return sorted(so, key=lambda s: (so[s], s))


def _base(n=30):
    return {"HS%03d" % i: i for i in range(n)}


# ---------------------------------------------------------------- (1) lần đầu giống hệt cách cũ
@pytest.mark.parametrize("seed", range(20))
def test_lan_dau_giong_het_cach_cu(seed):
    base = _base()
    assert rb.stb_theo_buoi_da_khoa(base, BUOI, seed, "stb_ngay", None) == rb.sinh_stb_theo_buoi(
        base, BUOI, seed, "stb_ngay")
    assert rb.stb_theo_buoi_da_khoa(base, BUOI, seed, "stb_ngay", {}) == rb.sinh_stb_theo_buoi(
        base, BUOI, seed, "stb_ngay")


def test_mot_buoi_va_che_do_khac_khong_luu_va_khong_doi():
    base = _base()
    for che_do in ("stb_tuan", "stb_co_bu"):
        assert rb.stb_theo_buoi_da_khoa(base, BUOI, 3, che_do, {"thu_2": {"HS000": 0}}) == \
            rb.sinh_stb_theo_buoi(base, BUOI, 3, che_do)
    assert rb.stb_theo_buoi_da_khoa(base, ["thu_2"], 3, "stb_ngay", {"thu_2": {"HS000": 0}}) == \
        rb.sinh_stb_theo_buoi(base, ["thu_2"], 3, "stb_ngay")


# ---------------------------------------------------------------- (2) em cũ giữ thứ tự tương đối, mọi ngày
@pytest.mark.parametrize("seed", range(10))
@pytest.mark.parametrize("k", [1, 3, 8])
def test_them_k_em_thi_em_cu_giu_thu_tu_moi_ngay(seed, k):
    base = _base()
    lan1 = rb.sinh_stb_theo_buoi(base, BUOI, seed, "stb_ngay")
    khoa = {b: dict(v) for b, v in lan1.items()}
    base2 = dict(base)
    for i in range(k):
        base2["MOI%02d" % i] = 100 + i
    lan2 = rb.stb_theo_buoi_da_khoa(base2, BUOI, seed, "stb_ngay", khoa)
    for b in BUOI:
        cu_truoc = _thu_tu(lan1[b])
        cu_sau = [s for s in _thu_tu(lan2[b]) if s in base]
        assert cu_truoc == cu_sau
        assert sorted(lan2[b].values()) == list(range(len(base2)))      # vẫn là hoán vị 0..n+k-1
    lan3 = rb.stb_theo_buoi_da_khoa(base2, BUOI, seed, "stb_ngay", {b: dict(v) for b, v in lan2.items()})
    assert lan3 == lan2                                                  # chạy lại không đổi gì


# ---------------------------------------------------------------- (3) em mới rơi đều trong từng ngày
def test_vi_tri_em_moi_phan_bo_deu_theo_ngay():
    n_cu, so_seed = 9, 3000
    base = _base(n_cu)
    base["MOI"] = 99
    for buoi in ("thu_2", "thu_5"):
        dem = [0] * (n_cu + 1)
        for seed in range(so_seed):
            khoa = {b: {s: i for i, s in enumerate(sorted(base_cu))} for b, base_cu in
                    ((b, [x for x in base if x != "MOI"]) for b in BUOI)}
            so = rb.stb_theo_buoi_da_khoa(base, BUOI, seed, "stb_ngay", khoa)[buoi]
            dem[so["MOI"]] += 1
        ky_vong = so_seed / (n_cu + 1)
        chi2 = sum((d - ky_vong) ** 2 / ky_vong for d in dem)
        assert chi2 < 27.88, (buoi, dem, chi2)        # 9 bậc tự do, p = 0,001


# ---------------------------------------------------------------- (4) xoá một em, em còn lại giữ thứ tự
def test_xoa_mot_em_thu_tu_nguoi_con_lai_khong_doi():
    base = _base()
    lan1 = rb.sinh_stb_theo_buoi(base, BUOI, 7, "stb_ngay")
    base2 = {s: v for s, v in base.items() if s != "HS005"}
    lan2 = rb.stb_theo_buoi_da_khoa(base2, BUOI, 7, "stb_ngay", {b: dict(v) for b, v in lan1.items()})
    for b in BUOI:
        assert _thu_tu(lan2[b]) == [s for s in _thu_tu(lan1[b]) if s != "HS005"]
        assert "HS005" not in lan2[b]


def test_xoa_hoc_sinh_xoa_dong_stb_buoi_va_khong_danh_lai_so(api):
    _nap_nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    _them_em(api, "TAM01")
    assert api.run_pipeline(seed=42)["ok"]
    luu = _luu(api)
    assert all("TAM01" in v for v in luu.values())
    # em chưa có kết quả thì xoá được; `match_results` có dòng NULL cho em đó nên xoá dòng trước như quy trình thật
    _sql_ghi = sqlite3.connect(api.db_path)
    _sql_ghi.execute("DELETE FROM match_results WHERE student_id = 'TAM01'")
    _sql_ghi.commit()
    _sql_ghi.close()
    assert api.delete_student("TAM01")["ok"]
    assert all("TAM01" not in v for v in _luu(api).values())
    luu_sau = _luu(api)
    for b in luu:
        assert luu_sau[b] == [s for s in luu[b] if s != "TAM01"]


# ---------------------------------------------------------------- tích hợp: lần đầu lưu, lần sau giữ
def test_lan_chay_dau_luu_thu_tu_va_ket_qua_khong_doi(api):
    _nap_nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    luu = _luu(api)
    assert sorted(luu) == sorted({r[0] for r in _sql(api, "SELECT DISTINCT buoi FROM match_results")})
    n_hs = _sql(api, "SELECT COUNT(*) FROM students")[0][0]
    assert all(len(v) == n_hs for v in luu.values())
    # lưu đúng bằng cách tính cũ từ bộ số gốc
    goc = dict(_sql(api, "SELECT student_id, stb_number FROM students"))
    cu = rb.sinh_stb_theo_buoi(goc, sorted(luu), 42, "stb_ngay")
    for b in luu:
        assert luu[b] == _thu_tu(cu[b])
    truoc = _ket_qua(api)
    assert api.run_pipeline(seed=42)["ok"]            # chạy lại, không đổi gì
    assert _ket_qua(api) == truoc
    assert _luu(api) == luu


def test_them_em_muon_em_cu_giu_thu_tu_moi_ngay_trong_csdl(api):
    _nap_nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    luu1 = _luu(api)
    for i in range(4):
        _them_em(api, "MUON%d" % i)
    kq = api.run_pipeline(seed=42)
    assert kq["ok"], kq
    luu2 = _luu(api)
    for b, ds in luu1.items():
        assert [s for s in luu2[b] if s in ds] == ds, b
        assert len(luu2[b]) == len(ds) + 4


def test_bao_cao_boc_tham_dung_thu_tu_da_luu(api):
    _nap_nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    for i in range(4):
        _them_em(api, "MUON%d" % i)
    assert api.run_pipeline(seed=42)["ok"]
    luu = _luu(api)
    bc = api.get_so_boc_tham_theo_buoi()
    assert bc["ok"]
    hs = bc["data"]["hoc_sinh"]
    for b in luu:
        theo_bao_cao = [r["student_id"] for r in sorted(hs, key=lambda r: (r["so"][b], r["student_id"]))]
        assert theo_bao_cao == luu[b], b


# ---------------------------------------------------------------- (5) vẽ lại: xoá thứ tự cũ, để dấu vết
def test_ve_lai_xoa_thu_tu_cu_va_de_dau_vet(api):
    _nap_nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    for i in range(3):
        _them_em(api, "MUON%d" % i)
    assert api.run_pipeline(seed=42)["ok"]
    cu = _luu(api)
    kq = api.run_pipeline(seed=7, force_redraw_stb=True)
    assert kq["ok"], kq
    moi = _luu(api)
    goc = dict(_sql(api, "SELECT student_id, stb_number FROM students"))
    tinh = rb.sinh_stb_theo_buoi(goc, sorted(moi), 7, "stb_ngay")
    for b in moi:                                           # thứ tự mới = bốc lại từ đầu, không dính bản cũ
        assert moi[b] == _thu_tu(tinh[b])
    assert moi != cu
    buoc = [s for s in kq["data"]["steps"] if s["step"] == "stb_lottery"][-1]
    assert "stb_buoi_ve_lai" in [w["code"] for w in buoc["warnings"]]
    assert _sql(api, "SELECT stb_redrawn FROM run_history ORDER BY run_id DESC LIMIT 1")[0][0] == 1
    assert _sql(api, "SELECT COUNT(*) FROM run_history")[0][0] == 3          # bất biến 4: chỉ thêm dòng


# ---------------------------------------------------------------- (6) di trú, idempotent, có sao lưu; CSDL cũ
def test_di_tru_tao_bang_idempotent_co_sao_luu(api):
    _nap_nhieu_buoi(api)
    conn = sqlite3.connect(api.db_path)
    conn.execute("DROP TABLE stb_buoi")
    conn.commit()
    conn.close()
    dau = rb.di_tru_schema(api.db_path)
    assert "stb_buoi" in dau
    assert any(f.startswith(os.path.basename(api.db_path) + ".bak-") for f in os.listdir(os.path.dirname(api.db_path)))
    assert rb.di_tru_schema(api.db_path) == []
    assert _sql(api, "SELECT COUNT(*) FROM stb_buoi") == [(0,)]


def test_csdl_cu_da_khoa_chua_co_thu_tu_lan_dau_tinh_nhu_cu_roi_luu_va_noi_ro(api):
    _nap_nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    truoc = _ket_qua(api)
    _sql_ghi = sqlite3.connect(api.db_path)                  # giả lập CSDL tạo trước bản này
    _sql_ghi.execute("DELETE FROM stb_buoi")
    _sql_ghi.commit()
    _sql_ghi.close()
    kq = api.run_pipeline(seed=42)
    assert kq["ok"]
    assert _ket_qua(api) == truoc                            # không có gì dịch chuyển lặng lẽ
    assert _luu(api)                                         # và đã lưu
    buoc = [s for s in kq["data"]["steps"] if s["step"] == "stb_lottery"][-1]
    assert "stb_buoi_luu_lan_dau" in [w["code"] for w in buoc["warnings"]]
    kq2 = api.run_pipeline(seed=42)                          # lần sau không nói lại
    buoc2 = [s for s in kq2["data"]["steps"] if s["step"] == "stb_lottery"][-1]
    assert not buoc2.get("warnings")


def test_mot_buoi_khong_luu_gi(api):
    for i, ten in enumerate(["danh_sach_CLB", "chon_CLB_muon_thi", "xep_hang_nguyen_vong"], start=1):
        with io.open(os.path.join(GOC, "du_lieu_test", "vi_du_huong_dan", "VIDU_0%d_%s.csv" % (i, ten)),
                     encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]
    assert api.run_pipeline(seed=42)["ok"]
    assert _sql(api, "SELECT COUNT(*) FROM stb_buoi") == [(0,)]


# ---------------------------------------------------------------- (7) dấu vân tay
def test_dau_van_tay_khong_gom_thu_tu_theo_ngay(api):
    _nap_nhieu_buoi(api)
    assert api.run_pipeline(seed=42)["ok"]
    conn = sqlite3.connect(api.db_path)
    conn.row_factory = sqlite3.Row
    truoc = rb.dau_van_tay_du_lieu(conn.cursor())
    conn.execute("UPDATE stb_buoi SET so = so + 1000")
    conn.commit()
    sau = rb.dau_van_tay_du_lieu(conn.cursor())
    conn.close()
    assert truoc == sau          # đúng như số bốc thăm gốc: kết quả của lần chạy, không phải dữ liệu đầu vào
    assert "KHÔNG gồm: số bốc thăm" in rb.dau_van_tay_du_lieu.__doc__
