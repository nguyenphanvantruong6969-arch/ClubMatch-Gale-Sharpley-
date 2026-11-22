"""MT2-R1: với `chia_loai` BẬT và `fa_daa` TẮT, cột Loại / Điểm sàn (và Tối thiểu, Sức chứa phòng) của Sổ nhập / CSV CLB phải được NẠP
(không bị bỏ qua như khi tắt), xem trước chỉ kiểm loại (không kiểm huy chương), và Sổ xuất ra mang đủ cột để nạp lại.
Tắt hoặc `fa_daa` cũ: y như trước (cảnh báo `fa_cot_bo_qua`, `huy_chuong_che_do_tat`). Dữ liệu MÔ PHỎNG."""

import base64

import openpyxl

import cau_hinh_ws as ch
from api import PipelineAPI
from test_mt1_dong_bo_loai_clb import SO_FA, _loai, _nap

CSV_CLB = ("club_id,name,capacity,loai,diem_san\n"
           "T1,CLB T1,5,TU_DO,\n"
           "S1,CLB S1,3,TUYEN_CHON,6\n"
           "G1,CLB G1,2,GIOI_HAN,\n")


def _ws(tmp_path, ten="a", **luat):
    api = PipelineAPI(str(tmp_path / (ten + ".db")), thu_muc_xuat=str(tmp_path / ("xuat_" + ten)))
    ch.ghi_cau_hinh(api.db_path, {"rules": luat})
    return api


def _b64(tep):
    with open(tep, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _ma(r):
    return [w["code"] for w in r["data"]["warnings"]]


def test_so_nhap_fa_mau_chia_loai_bat_nap_du_loai_khong_canh_bao_bo_qua(tmp_path):
    api = _ws(tmp_path, wharton=False, chia_loai=True)
    r = _nap(api, SO_FA)
    assert "fa_cot_bo_qua" not in _ma(r)
    loai = _loai(api)
    assert len(loai) == 8 and all(v[0] is not None for v in loai.values())
    # tham chiếu: cùng sổ vào workspace Huy chương cho cùng loại / điểm sàn
    ref = _ws(tmp_path, "ref", fa_daa=True)
    _nap(ref, SO_FA)
    assert loai == _loai(ref)


def test_csv_clb_chia_loai_bat_nap_loai_va_diem_san(tmp_path):
    api = _ws(tmp_path, wharton=False, chia_loai=True)
    r = api.import_clubs_csv(CSV_CLB)
    assert r["ok"], r
    assert "fa_cot_bo_qua" not in _ma(r)
    assert _loai(api) == {"T1": ("TU_DO", None), "S1": ("TUYEN_CHON", 6), "G1": ("GIOI_HAN", None)}


def test_tat_va_fa_cu_giu_hanh_vi_cu(tmp_path):
    tat = _ws(tmp_path, "tat", wharton=False)
    r = tat.import_clubs_csv(CSV_CLB)
    assert "fa_cot_bo_qua" in _ma(r)                     # TẮT: cột bị bỏ qua, có cảnh báo như trước
    assert all(v == (None, None) for v in _loai(tat).values())
    xem = tat.xem_truoc_so_nhap(_b64(SO_FA))
    assert "so_nhap_canh_bao_huy_chuong_che_do_tat" in [w["code"] for w in xem["data"]["canh_bao"]]   # TẮT: vẫn nhắc như trước
    fa = _ws(tmp_path, "fa", fa_daa=True)
    assert "fa_cot_bo_qua" not in _ma(fa.import_clubs_csv(CSV_CLB))
    assert _loai(fa)["S1"] == ("TUYEN_CHON", 6)


def test_xem_truoc_chia_loai_khong_kiem_huy_chuong_va_khong_bao_che_do_tat_vi_loai(tmp_path):
    api = _ws(tmp_path, wharton=False, chia_loai=True)
    xem = api.xem_truoc_so_nhap(_b64(SO_FA))
    assert xem["ok"], xem
    ma = [w["code"] for w in xem["data"]["canh_bao"]]
    assert not any(c.startswith("fa_huy_chuong_") for c in ma)            # không kiểm hồ sơ huy chương
    # sổ FA mẫu có cột Huy chương: vẫn được nhắc (chế độ huy chương tắt); nhưng cột Loại một mình không gây nhắc
    csv_so = _ws(tmp_path, "x", wharton=False, chia_loai=True)
    assert csv_so.import_clubs_csv(CSV_CLB)["ok"]


def test_xuat_so_nhap_chia_loai_bat_mang_cot_va_nap_lai_duoc(tmp_path):
    a = _ws(tmp_path, "a", wharton=False, chia_loai=True)
    _nap(a, SO_FA)
    truoc = _loai(a)
    r = a.export_du_lieu_dau_vao()
    assert r["ok"], r
    hd = [c.value for c in openpyxl.load_workbook(r["data"]["path"]).worksheets[0][1]]
    assert all(c in hd for c in ("Loại", "Điểm sàn"))
    b = _ws(tmp_path, "b", wharton=False, chia_loai=True)
    with open(r["data"]["path"], "rb") as f:
        assert b.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    assert _loai(b) == truoc


def test_loi_chay_sau_nap_chia_loai_khong_con_thieu_loai(tmp_path):
    api = _ws(tmp_path, wharton=False, chia_loai=True)
    _nap(api, SO_FA)
    codes = [e["code"] for e in (api.run_pipeline(seed=3).get("errors") or [])]
    assert "fa_clb_thieu_loai" not in codes and "fa_thieu_clb_tu_do" not in codes
