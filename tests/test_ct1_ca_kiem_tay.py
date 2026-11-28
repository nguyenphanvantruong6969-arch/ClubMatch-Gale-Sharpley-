"""CT1-L4 — ba ca kiểm BẰNG TAY trên kịch bản 8 học sinh / 3 CLB của `du_lieu_test/NHAP_TAY.md` (DỮ LIỆU MÔ PHỎNG).

Người dùng tự tính được: mỗi ca đổi chỉ tiêu bằng một bước "chuyển 1 chỗ" rồi đối chiếu danh sách em đổi chỗ.
Chạy bằng chính API (`get_xem_xet_chi_tieu` với `buoc_tu_chon`), 5 seed; kết quả phải GIỐNG HỆT ở mọi seed
(kịch bản không có hai em bằng điểm trong cùng CLB nên bốc thăm không được dùng tới).

  A  Nấu ăn −1 → Cờ vua +1     : chỉ HS08 đổi (chưa có → Cờ vua)
  B  Nấu ăn −1 → Nhiếp ảnh +1  : HS03 Cờ vua → Nhiếp ảnh (NV2 → NV1) VÀ HS08 chưa có → Cờ vua (1 chỗ, 2 em)
  C  Nhiếp ảnh −1 → Nấu ăn +1  : chỉ HS02 Nhiếp ảnh → Nấu ăn (xuống NV1 → NV2)
Quy tắc đề xuất không cho bước nào trên bộ nhỏ này (kẹp ±20 % và quy mô tối thiểu), nên ba ca đi qua bước tự chọn.
"""

import pytest

from _wharton import tat_wharton
from test_kich_ban_nhap_tay import _dung_kich_ban

SEEDS = (1, 7, 42, 999, 12345)

CA = {
    "A": ([{"tu": "clb_nauan", "den": "clb_covua", "k": 1}],
          [("HS08", None, "clb_covua", None, 1, "vao")]),
    "B": ([{"tu": "clb_nauan", "den": "clb_nhiepanh", "k": 1}],
          [("HS03", "clb_covua", "clb_nhiepanh", 2, 1, "len"), ("HS08", None, "clb_covua", None, 1, "vao")]),
    "C": ([{"tu": "clb_nhiepanh", "den": "clb_nauan", "k": 1}],
          [("HS02", "clb_nhiepanh", "clb_nauan", 1, 2, "xuong")]),
}


def _mo(api, seed):
    tat_wharton(api)
    _dung_kich_ban(api, co_diem_quyet_tam=False)
    assert api.run_pipeline(seed=seed)["ok"]


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("ca", sorted(CA))
def test_ca_kiem_tay(api, ca, seed):
    buoc, mong = CA[ca]
    _mo(api, seed)
    r = api.get_xem_xet_chi_tieu(buoc)
    assert r["ok"], r
    d = r["data"]
    assert d["loi_giai"] is None and d["canh_bao"] == []
    doi = [(e["student_id"], e["tu"], e["den"], e["nv_truoc"], e["nv_sau"], e["huong"]) for e in d["buoc"][0]["doi"]]
    assert sorted(doi) == sorted(mong)
    assert d["buoc"][0]["so_doi"] == len(mong)


def test_quy_tac_de_xuat_khong_cho_buoc_nao_tren_bo_nho(api):
    _mo(api, 42)
    d = api.get_xem_xet_chi_tieu()["data"]
    assert d["che_do"] == "de_xuat" and d["buoc"] == [] and d["khuyen_nghi"]["so_cho_chuyen"] == 0
    assert d["so_hoc_sinh"] == 8 and d["tong_cho"] == 7
    assert d["truoc"] == d["sau"] and d["truoc"]["chua_co"] == 2


def test_tai_lieu_nhap_tay_noi_dung_ba_ca():
    import os
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(goc, "du_lieu_test", "NHAP_TAY.md"), encoding="utf-8") as f:
        tl = " ".join(f.read().split())
    for dong in ("| A | Nấu ăn −1 → Cờ vua +1 |", "| B | Nấu ăn −1 → Nhiếp ảnh +1 |", "| C | Nhiếp ảnh −1 → Nấu ăn +1 |"):
        assert dong in tl, dong
