"""DG1-L2: bộ sinh dữ liệu mô phỏng (du_lieu_test/danh_gia/_sinh.py) — xác định theo seed, đúng mô hình α/ρ/κ,
và dữ liệu nạp qua phần mềm thật khớp dữ liệu trong bộ nhớ."""

import hashlib
import os
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "du_lieu_test", "danh_gia"))

import _sinh as sinh  # noqa: E402


def _dau_van_tay(duong):
    """Hash nội dung sổ, bỏ docProps (có dấu thời gian tạo)."""
    h = hashlib.sha256()
    with zipfile.ZipFile(duong) as z:
        for ten in sorted(z.namelist()):
            if ten.startswith("docProps/"):
                continue
            h.update(ten.encode())
            h.update(z.read(ten))
    return h.hexdigest()


def _tap_trung_nv1(truong):
    """Chỉ số Herfindahl của nguyện vọng 1: Σ (tỉ lệ em chọn CLB đó làm NV1)²."""
    dem = {}
    for ds in truong["preferences"].values():
        dem[ds[0]] = dem.get(ds[0], 0) + 1
    n = len(truong["preferences"])
    return sum((v / n) ** 2 for v in dem.values())


def test_cung_seed_cung_du_lieu_va_cung_so_nhap(tmp_path):
    a = sinh.sinh_truong(120, 10, seed=3)
    b = sinh.sinh_truong(120, 10, seed=3)
    assert a == b
    pa, pb = tmp_path / "a.xlsx", tmp_path / "b.xlsx"
    sinh.sinh_so_nhap(a, str(pa))
    sinh.sinh_so_nhap(b, str(pb))
    assert _dau_van_tay(str(pa)) == _dau_van_tay(str(pb))


def test_khac_seed_khac_du_lieu():
    assert sinh.sinh_truong(120, 10, seed=1)["preferences"] != sinh.sinh_truong(120, 10, seed=2)["preferences"]


def test_alpha_cao_don_nguyen_vong_1_vao_it_clb_hon():
    thap = _tap_trung_nv1(sinh.sinh_truong(300, 10, alpha=0.0, seed=5))
    cao = _tap_trung_nv1(sinh.sinh_truong(300, 10, alpha=0.9, seed=5))
    assert cao > thap + 0.05


def test_hinh_dang_mo_hinh():
    t = sinh.sinh_truong(800, 20, alpha=0.5, rho=0.7, kappa=1.1, seed=1)
    n = 800
    assert abs(t["tham_so"]["kappa_thuc"] - 1.1) < 0.05
    assert all(3 <= len(ds) <= 6 for ds in t["preferences"].values())
    assert all(len(set(ds)) == len(ds) for ds in t["preferences"].values())
    assert len(t["tuyen_chon"]) == 6
    # điểm chỉ ở CLB tuyển chọn, ≤ 5 CLB/em, 0..10 một chữ số thập phân
    for c, d in t["tested_scores"].items():
        assert (not d) or c in t["tuyen_chon"]
        assert all(0 <= v <= 10 and round(v, 1) == v for v in d.values())
    moi = {}
    for d in t["tested_scores"].values():
        for s in d:
            moi[s] = moi.get(s, 0) + 1
    assert max(moi.values()) <= 5
    nhom = {}
    for s in t["students"].values():
        nhom[s["reserve_group"]] = nhom.get(s["reserve_group"], 0) + 1
    assert nhom["chinh_sach"] == 120 and nhom["khoi_10"] == 48
    assert sum(1 for v in t["clubs"].values() if v["reserve_group"]) == 4
    assert all(v["capacity"] >= 2 for v in t["clubs"].values())
    assert n == len(t["students"])


def test_rho_cao_diem_tuong_quan_nang_luc():
    # ρ = 0.7: điểm cùng một em ở các CLB khác nhau gần nhau hơn ρ = 0 (so độ lệch chuẩn trong từng em).
    def sd_trong_em(rho):
        t = sinh.sinh_truong(800, 10, alpha=0.5, rho=rho, seed=4)
        theo = {}
        for d in t["tested_scores"].values():
            for s, v in d.items():
                theo.setdefault(s, []).append(v)
        gia_tri = [max(v) - min(v) for v in theo.values() if len(v) >= 2]
        return sum(gia_tri) / len(gia_tri)
    assert sd_trong_em(0.7) < sd_trong_em(0.0)


def test_nhieu_buoi_chia_clb_dung_buoi():
    t = sinh.sinh_truong(120, 12, so_buoi=3, seed=2)
    assert t["ds_buoi"] == ["thu_2", "thu_4", "thu_6"]
    buoi_clb = {c: v["buoi"] for c, v in t["clubs"].items()}
    assert sorted(set(buoi_clb.values())) == t["ds_buoi"]
    for ds in t["preferences"].values():
        assert len({buoi_clb[c] for c in ds}) == 3        # mỗi em khai đủ ba buổi


def test_nap_qua_phan_mem_khop_bo_nho(tmp_path):
    t = sinh.sinh_truong(120, 10, seed=7)
    x = tmp_path / "so.xlsx"
    sinh.sinh_so_nhap(t, str(x))
    _db, (students, clubs, scores, app, prefs, _stb) = sinh.doc_qua_phan_mem(str(x), str(tmp_path))
    assert {s: (v["reserve_group"] or "") for s, v in students.items()} == {s: v["reserve_group"] for s, v in t["students"].items()}
    assert {c: (v["capacity"], v["reserve_capacity"], v["reserve_group"] or "") for c, v in clubs.items()} == \
           {c: (v["capacity"], v["reserve_capacity"], v["reserve_group"]) for c, v in t["clubs"].items()}
    assert prefs == t["preferences"]
    assert {c: d for c, d in scores.items() if d} == {c: d for c, d in t["tested_scores"].items() if d}
    assert {c: sorted(v) for c, v in app.items()} == {c: sorted(v) for c, v in t["applicants"].items()}


def test_nhieu_buoi_kappa_tinh_moi_buoi():
    # Mỗi em cần một chỗ MỖI buổi: tổng chỉ tiêu ≈ κ × N × số buổi, nên κ thực (theo buổi) vẫn ≈ κ.
    t = sinh.sinh_truong(300, 12, kappa=1.1, so_buoi=3, seed=5)
    assert abs(t["tham_so"]["kappa_thuc"] - 1.1) < 0.05
    tong = sum(v["capacity"] for v in t["clubs"].values())
    assert abs(tong - 1.1 * 300 * 3) <= 12 * 2
