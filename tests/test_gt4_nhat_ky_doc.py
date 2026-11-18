"""GT4-L6 — nhật ký đọc được: lọc theo ngày / chỉ bị từ chối ở phía máy chủ, danh sách hành động có mặt,
tệp CSV giữ NGUYÊN dạng thô. Dữ liệu MÔ PHỎNG, mật khẩu giả."""

import csv
import io
import json
import os
import shutil
import subprocess

import pytest

import nhat_ky as nk
import phan_quyen as pq

MK = "matkhau-gia-1"
GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def co_nk(api):
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK)["ok"]
    assert not api.run_thu({"priority": "tier"})["ok"]                  # một dòng bị từ chối quyền
    api.dang_xuat()
    assert api.dang_nhap("quantri", MK)["ok"]
    with api._ket_noi_ghi() as cur:                                     # dòng cũ có ngày xác định (INSERT được phép)
        cur.executemany(
            "INSERT INTO nhat_ky_thao_tac (luc, nguoi, vai, hanh_dong, ket_qua, chi_tiet) VALUES (?,?,?,?,?,?)",
            [("2026-01-02T10:00:00", "quantri", "quan_tri", "run_pipeline", "ok", "{}"),
             ("2026-01-02T11:30:00", "gv1", "giao_vien", "run_thu", "gt3_khong_du_quyen", "{}"),
             ("2026-01-03T09:00:00", "quantri", "quan_tri", "export_csv", "ok", "{}")])
    return api


def _dong(r):
    assert r["ok"], r
    return r["data"]["dong"]


def test_loc_theo_ngay_o_may_chu(co_nk):
    r = co_nk.get_nhat_ky_thao_tac(1, 50, None, None, False, "2026-01-02")
    assert sorted(d["hanh_dong"] for d in _dong(r)) == ["run_pipeline", "run_thu"]
    assert r["data"]["tong"] == 2
    r = co_nk.get_nhat_ky_thao_tac(1, 50, None, None, False, "2026-01-03")
    assert [d["hanh_dong"] for d in _dong(r)] == ["export_csv"]
    assert _dong(co_nk.get_nhat_ky_thao_tac(1, 50, None, None, False, "1999-01-01")) == []


def test_ngay_sai_dang_thi_bao_loi_ro(co_nk):
    for xau in ("02/01/2026", "2026-1-2", "abc", "2026-13-40"):
        r = co_nk.get_nhat_ky_thao_tac(1, 50, None, None, False, xau)
        assert not r["ok"] and r["errors"][0]["code"] == "gt4_ngay_sai", xau
    assert co_nk.get_nhat_ky_thao_tac(1, 50, None, None, False, "")["ok"]       # rỗng = không lọc


def test_chi_bi_tu_choi(co_nk):
    tat_ca = co_nk.get_nhat_ky_thao_tac(1, 500)["data"]["tong"]
    r = co_nk.get_nhat_ky_thao_tac(1, 500, None, None, True)
    d = _dong(r)
    assert d and all(x["ket_qua"] != "ok" for x in d) and r["data"]["tong"] < tat_ca
    assert {"run_thu"} <= {x["hanh_dong"] for x in d}


def test_danh_sach_hanh_dong_co_mat(co_nk):
    r = co_nk.get_nhat_ky_thao_tac(1, 5)
    ds = r["data"]["hanh_dong_co"]
    assert ds == sorted(set(ds)) and {"run_pipeline", "run_thu", "tao_tai_khoan", "dang_nhap"} <= set(ds)


def test_csv_van_la_dang_tho_va_loc_duoc(co_nk, tmp_path):
    r = co_nk.export_nhat_ky_thao_tac_csv(str(tmp_path / "tat_ca.csv"))
    assert r["ok"]
    noi_dung = (tmp_path / "tat_ca.csv").read_text(encoding="utf-8-sig")
    hang = list(csv.reader(io.StringIO(noi_dung)))
    assert hang[0] == list(nk.COT)
    assert any(h[4] == "tao_tai_khoan" for h in hang[1:]) and any(h[5] == "gt3_khong_du_quyen" for h in hang[1:])
    assert "Tạo tài khoản" not in noi_dung and "Bị từ chối" not in noi_dung     # không có nhãn tiếng Việt trong CSV
    r = co_nk.export_nhat_ky_thao_tac_csv(str(tmp_path / "loc.csv"), None, None, True, "2026-01-02")
    assert r["ok"] and r["data"]["n_rows"] == 1                                  # chỉ dòng bị từ chối của ngày 2/1
    hang = list(csv.reader(io.StringIO((tmp_path / "loc.csv").read_text(encoding="utf-8-sig"))))
    assert [h[4] for h in hang[1:]] == ["run_thu"]


def test_bang_quyen_nhat_ky_van_la_quan_tri(co_nk):
    assert pq.QUYEN["get_nhat_ky_thao_tac"] == pq.QUAN_TRI == pq.QUYEN["export_nhat_ky_thao_tac_csv"]


# ------------------------------------------------------------------------------- nhãn tiếng Việt / Anh
def _khoa_ui(ngon_ngu):
    node = shutil.which("node")
    if not node:
        pytest.skip("không có node")
    ma = ("const fs=require('fs');const src=fs.readFileSync(process.argv[1],'utf8');"
          "const s=src.indexOf('const UI_STRINGS = {');let b=src.indexOf('{',s),d=0,i=b;"
          "for(;i<src.length;i++){if(src[i]==='{')d++;else if(src[i]==='}'){d--;if(d===0){i++;break;}}}"
          "const o=eval('('+src.slice(b,i)+')');process.stdout.write(JSON.stringify(o['%s']));" % ngon_ngu)
    ra = subprocess.run([node, "-e", ma, "--", os.path.join(GOC, "i18n.js")], capture_output=True, encoding="utf-8",
                        check=True)
    return json.loads(ra.stdout)


@pytest.mark.parametrize("ngon_ngu", ["vi", "en"])
def test_moi_ham_co_ghi_nhat_ky_deu_co_nhan(ngon_ngu):
    bang = _khoa_ui(ngon_ngu)
    thieu = [k for k in pq.QUYEN if nk.nen_ghi(k) and "nkhd_" + k not in bang]
    assert not thieu, thieu
    for vai in ("quan_tri", "giao_vien"):
        assert "nkvai_" + vai in bang
    for kq in ("ok", "gt3_khong_du_quyen", "gt3_can_dang_nhap", "gt3_che_do_hoc_sinh", "gt3_tam_khoa", "loi_ngoai_le"):
        assert "nkkq_" + kq in bang, kq
    assert bang["nkhd_tra_cuu_hoc_sinh"] and "nk_hoc_sinh_tu_tra_cuu" in bang
    chu_cam = ("bạn", "các em", "Các em")
    for k, v in bang.items():
        if k.startswith("nk"):
            assert not any(c in v for c in chu_cam), (k, v)
