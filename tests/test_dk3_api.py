"""DK3-L2: api_dang_ky — luồng đầy đủ quản trị → giáo viên → duyệt → học sinh → điểm."""
import datetime
import sqlite3

import pytest


def ok(r):
    assert r["ok"], r
    return r["data"]


def ma(r):
    assert not r["ok"], r
    return r["errors"][0]["code"]


@pytest.fixture
def cd(api):
    """CSDL đã khởi tạo, 2 phòng, 2 giáo viên, 4 học sinh; trả (api, token quản trị)."""
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    for t, sc in (("P1", 40), ("P2", 30), ("P3", 20)):
        ok(api.dk_phong_luu(qt, t, sc))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    return api, qt


def _clb(**kw):
    d = {"ten": "Cờ vua", "buoi": "T2", "loai": "Giới hạn", "phong_id": 1, "chi_tieu": 20, "khoi_tu": 10, "khoi_den": 12}
    d.update(kw)
    return d


def _dung_san(api, qt):
    """Một CLB mỗi loại ở T2 (đã duyệt) + 3 học sinh; mở cho học sinh."""
    pin = ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nThầy Bình\nCô Chi"))["da_tao"]
    tok = {x["ten"]: ok(api.dk_dang_nhap("giao_vien", x["ten"], x["pin"]))["token"] for x in pin}
    ids = {}
    for gv, ten, loai, ph, kw in (("Cô An", "Tự do 1", "Tự do", 1, {}), ("Thầy Bình", "Cờ vua", "Giới hạn", 2, {"chi_tieu": 10}),
                                  ("Cô Chi", "Robot", "Tuyển chọn", 3, {"chi_tieu": 10, "diem_san": 6})):
        ids[ten] = ok(api.dk_clb_luu(tok[gv], _clb(ten=ten, loai=loai, phong_id=ph, **kw)))["clb_id"]
        ok(api.dk_clb_duyet(qt, ids[ten], "duyet"))
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1\nH2\tBình\t10A1\nH3\tChi\t6A2"))
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    return ids


def test_khoi_tao_mot_lan_va_dang_nhap_khong_lo(api):
    assert ma(api.dk_dang_nhap("quan_tri", "", "x")) == "dk_chua_khoi_tao"
    ok(api.dk_khoi_tao("matkhau", "T"))
    assert ma(api.dk_khoi_tao("matkhau", "T")) == "dk_da_khoi_tao"
    assert ma(api.dk_dang_nhap("quan_tri", "", "sai")) == "dk_sai_dang_nhap"
    assert ma(api.dk_dang_nhap("giao_vien", "ai-do", "1234")) == "dk_sai_dang_nhap"
    c = sqlite3.connect(api.db_path)
    luu = " ".join(str(v) for r in c.execute("SELECT * FROM dk_cai_dat") for v in r)
    c.close()
    assert "matkhau" not in luu


def test_gv_tu_dang_ky_dung_ma_truong_va_dung_giai_doan(cd):
    api, qt = cd
    assert ma(api.dk_gv_tu_dang_ky("SAI", "Cô X", "1234")) == "dk_ma_truong_sai"
    assert ma(api.dk_gv_tu_dang_ky("TRUONG1", "Cô X", "12")) == "dk_pin_sai_dang"
    ok(api.dk_gv_tu_dang_ky("TRUONG1", "Cô X", "1234"))
    assert ma(api.dk_gv_tu_dang_ky("TRUONG1", "Cô X", "1234")) == "dk_gv_trung"
    gv = ok(api.dk_gv_danh_sach(qt))
    assert gv[0]["cach_tao"] == "tu_dang_ky"
    assert "pin" not in str(gv)


def test_luat_clb_d14_d15(cd):
    api, qt = cd
    gt = ok(api.dk_gv_tao_hang_loat(qt, "Cô An\nCô Bê"))["da_tao"]
    t = {x["ten"]: ok(api.dk_dang_nhap("giao_vien", x["ten"], x["pin"]))["token"] for x in gt}
    ok(api.dk_clb_luu(t["Cô An"], _clb()))
    assert ma(api.dk_clb_luu(t["Cô An"], _clb(ten="Khác", phong_id=2))) == "dk_gv_hai_clb_mot_buoi"   # D14
    assert ma(api.dk_clb_luu(t["Cô Bê"], _clb(ten="Khác"))) == "dk_phong_ban"                          # phòng bận
    assert ma(api.dk_clb_luu(t["Cô Bê"], _clb(ten="Cờ vua", phong_id=2))) == "dk_clb_ten_trung"
    assert ma(api.dk_clb_luu(t["Cô Bê"], _clb(ten="K", phong_id=3, chi_tieu=99))) == "dk_chi_tieu_qua_phong"
    assert ma(api.dk_clb_luu(t["Cô Bê"], _clb(ten="K", phong_id=3, loai="Tuyển chọn"))) == "dk_diem_san_sai"
    assert ma(api.dk_clb_luu(t["Cô Bê"], _clb(ten="K", phong_id=3, khoi_tu=5))) == "dk_khoi_sai"
    d = ok(api.dk_clb_luu(t["Cô Bê"], _clb(ten="Tự do", phong_id=3, loai="Tự do", chi_tieu=None)))
    assert d["clb_id"]
    assert len(ok(api.dk_clb_danh_sach(t["Cô An"]))) == 1                  # giáo viên chỉ thấy CLB của mình
    assert ma(api.dk_clb_danh_sach("sai")) == "dk_can_dang_nhap"
    assert ma(api.dk_gv_danh_sach(t["Cô An"])) == "dk_khong_du_quyen"


def test_mo_cho_hoc_sinh_can_clb_tu_do_moi_buoi_d2(cd):
    api, qt = cd
    pin = ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))["da_tao"][0]
    t = ok(api.dk_dang_nhap("giao_vien", "Cô An", pin["pin"]))["token"]
    cid = ok(api.dk_clb_luu(t, _clb()))["clb_id"]
    assert ma(api.dk_chuyen_giai_doan(qt, "hs_dang_ky")) == "dk_thieu_clb_tu_do"       # VG1-L4: chặn SỚM, ngay khi đi ngang «duyet»
    pin2 = ok(api.dk_gv_tao_hang_loat(qt, "Thầy Bình"))["da_tao"][0]
    t2 = ok(api.dk_dang_nhap("giao_vien", "Thầy Bình", pin2["pin"]))["token"]            # mỗi giáo viên một CLB mỗi buổi
    td = ok(api.dk_clb_luu(t2, _clb(ten="Tự do", loai="Tự do", phong_id=2, chi_tieu=None)))["clb_id"]
    assert ma(api.dk_chuyen_giai_doan(qt, "hs_dang_ky")) == "dk_con_clb_cho_duyet"     # đủ CLB Tự do nhưng còn CLB chờ duyệt
    ok(api.dk_clb_duyet(qt, cid, "duyet"))
    assert ma(api.dk_chuyen_giai_doan(qt, "hs_dang_ky")) == "dk_con_clb_cho_duyet"
    ok(api.dk_clb_duyet(qt, td, "duyet"))
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))


def test_giao_vien_het_gio_khong_luu_duoc_va_tu_dong_dong(cd, monkeypatch):
    api, qt = cd
    han = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat(timespec="minutes")
    ok(api.dk_dat_han(qt, "gv_dang_ky", han))
    assert ok(api.dk_trang_thai())["giai_doan"] == "gv_dang_ky"
    monkeypatch.setattr(api, "_dk_bay_gio", lambda: datetime.datetime.now() + datetime.timedelta(hours=2))
    assert ok(api.dk_trang_thai())["giai_doan"] == "duyet"          # GV đóng -> Duyệt, không bao giờ sang học sinh


def test_hoc_sinh_luu_huy_chuong_mac_dinh_va_ghi_de(cd):
    api, qt = cd
    ids = _dung_san(api, qt)
    pin = ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]
    assert ma(api.dk_dang_nhap("hoc_sinh", "H9", pin)) == "dk_sai_dang_nhap"            # D9
    h = ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]
    hop_le = {c["ten"] for c in ok(api.dk_hs_clb_hop_le(h))}
    assert hop_le == {"Tự do 1", "Cờ vua", "Robot"}                                        # khối 10 đủ cả ba
    nv = [{"clb_id": ids["Robot"], "thi": True}, {"clb_id": ids["Cờ vua"]}, {"clb_id": ids["Tự do 1"]}]
    d = ok(api.dk_hs_luu(h, nv))
    assert d["canh_bao"] == []
    luu = ok(api.dk_hs_nguyen_vong(h))["nguyen_vong"]
    assert [(x["hang"], x["huy_chuong"]) for x in luu] == [(1, "Vàng"), (2, "Bạc"), (3, None)]   # Tự do không huy chương
    # ghi đè tay: đổi Vàng <-> Bạc
    nv2 = [{"clb_id": ids["Robot"], "thi": True, "huy_chuong": "Bạc"}, {"clb_id": ids["Cờ vua"], "huy_chuong": "Vàng"},
           {"clb_id": ids["Tự do 1"]}]
    ok(api.dk_hs_luu(h, nv2, buoi_tay=["T2"]))
    assert [x["huy_chuong"] for x in ok(api.dk_hs_nguyen_vong(h))["nguyen_vong"]] == ["Bạc", "Vàng", None]
    assert ma(api.dk_hs_luu(h, [{"clb_id": ids["Tự do 1"], "huy_chuong": "Vàng"}], buoi_tay=["T2"])) == "dk_huy_chuong_tu_do"
    assert ma(api.dk_hs_luu(h, [{"clb_id": ids["Cờ vua"], "huy_chuong": "Vàng"},
                                {"clb_id": ids["Robot"], "huy_chuong": "Vàng"}], buoi_tay=["T2"])) == "dk_huy_chuong_trung"
    assert ma(api.dk_hs_luu(h, [{"clb_id": ids["Cờ vua"], "thi": True}])) == "dk_thi_sai_loai"
    ra = ok(api.dk_hs_luu(h, [{"clb_id": ids["Cờ vua"]}]))
    assert ra["canh_bao"][0]["code"] == "dk_khong_co_tu_do"


def test_hoc_sinh_chi_thay_clb_dung_khoi_va_phai_mo(cd):
    api, qt = cd
    ids = _dung_san(api, qt)
    pin = ok(api.dk_hs_dat_lai_pin(qt, "H3"))["pin"]
    h = ok(api.dk_dang_nhap("hoc_sinh", "H3", pin))["token"]                                 # khối 6
    assert ok(api.dk_hs_clb_hop_le(h)) == []
    assert ma(api.dk_hs_luu(h, [{"clb_id": ids["Cờ vua"]}])) == "dk_clb_khong_hop_le"
    ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
    assert ma(api.dk_hs_luu(h, [])) == "dk_hs_chua_mo"


def test_diem_nhap_tay_va_dan(cd):
    api, qt = cd
    ids = _dung_san(api, qt)
    pin = ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]
    h = ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]
    ok(api.dk_hs_luu(h, [{"clb_id": ids["Robot"], "thi": True}, {"clb_id": ids["Tự do 1"]}]))
    assert [x["ma"] for x in ok(api.dk_diem_thieu(qt))] == ["H1"]
    assert ma(api.dk_chuyen_giai_doan(qt, "xuat")) == "dk_thieu_diem"
    assert ma(api.dk_diem_dat(qt, "H1", ids["Robot"], "11")) == "dk_diem_sai"
    ok(api.dk_diem_dat(qt, "H1", ids["Robot"], "8,5"))
    assert ok(api.dk_diem_thieu(qt)) == []
    r = ok(api.dk_diem_dan(qt, ids["Robot"], "H1\t7,0\nH2\t5\nH1\tabc"))
    assert r["da_luu"] == 1 and len(r["loi"]) == 2
    ok(api.dk_chuyen_giai_doan(qt, "xuat"))


def test_toi_da_5_bai_thi_moi_buoi_d44(cd):
    api, qt = cd
    for i in range(4, 10):
        ok(api.dk_phong_luu(qt, "Q%d" % i, 30))
    ids = []
    td = ok(api.dk_clb_luu(qt, _clb(ten="TD", loai="Tự do", phong_id=1, chi_tieu=None)))["clb_id"]   # VG1-L4: CLB Tự do có trước khi duyệt CLB khác
    ok(api.dk_clb_duyet(qt, td, "duyet"))
    for i in range(6):
        ids.append(ok(api.dk_clb_luu(qt, _clb(ten="TC%d" % i, loai="Tuyển chọn", phong_id=4 + i, chi_tieu=10, diem_san=5)))["clb_id"])
        ok(api.dk_clb_duyet(qt, ids[-1], "duyet"))
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    h = ok(api.dk_dang_nhap("hoc_sinh", "H1", ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]))["token"]
    assert ma(api.dk_hs_luu(h, [{"clb_id": c, "thi": True} for c in ids])) == "dk_qua_bai_thi"
    ok(api.dk_hs_luu(h, [{"clb_id": c, "thi": True} for c in ids[:5]]))


def test_sua_sau_khi_mo_bao_so_em_bi_anh_huong(cd):
    api, qt = cd
    ids = _dung_san(api, qt)
    pin = ok(api.dk_hs_dat_lai_pin(qt, "H1"))["pin"]
    h = ok(api.dk_dang_nhap("hoc_sinh", "H1", pin))["token"]
    ok(api.dk_hs_luu(h, [{"clb_id": ids["Cờ vua"]}, {"clb_id": ids["Tự do 1"]}]))
    assert ok(api.dk_clb_sua_sau_mo(qt, ids["Cờ vua"], chi_tieu=15))["anh_huong"] == 0          # tăng chỉ tiêu: tự do
    assert ma(api.dk_clb_sua_sau_mo(qt, ids["Cờ vua"], chi_tieu=5)) == "dk_chi_tieu_sai"        # chỉ được tăng
    r = ok(api.dk_clb_sua_sau_mo(qt, ids["Cờ vua"], xoa=True))
    assert r == {"can_xac_nhan": True, "anh_huong": 1}
    assert ok(api.dk_clb_sua_sau_mo(qt, ids["Cờ vua"], xoa=True, xac_nhan=True))["anh_huong"] == 1
    assert [x["hanh_dong"] for x in ok(api.dk_nhat_ky(qt))][0] == "xoa_clb_sau_mo"


def test_ds_hoc_sinh_che_do_them_va_thay(cd):
    api, qt = cd
    r = ok(api.dk_hs_nap_danh_sach(qt, "A1\tAn\t10A1\nbad\nA2,Bình,11B2\nA3 Lê Văn Cường 9C1"))
    assert (r["moi"], len(r["loi"])) == (3, 1) and len(r["pin"]) == 3
    r2 = ok(api.dk_hs_nap_danh_sach(qt, "A1\tAn Mới\t10A1"))
    assert (r2["moi"], r2["da_co"], r2["pin"]) == (0, 1, [])                                  # giữ PIN
    assert ma(api.dk_hs_nap_danh_sach(qt, "A1\tAn\t10A1\nbad", "thay")) == "dk_danh_sach_co_loi"
    ok(api.dk_hs_nap_danh_sach(qt, "Z1\tZ\t12A1", "thay"))
    assert [h["ma"] for h in ok(api.dk_hs_danh_sach(qt))] == ["Z1"]


def test_pin_va_mat_khau_chi_luu_bam(cd):
    api, qt = cd
    pin = ok(api.dk_hs_nap_danh_sach(qt, "Q1\tQ\t10A1"))["pin"][0]["pin"]
    c = sqlite3.connect(api.db_path)
    raw = c.execute("SELECT pin_bam, pin_muoi FROM dk_hoc_sinh").fetchone()
    c.close()
    assert pin.encode() not in bytes(raw[0]) and len(raw[1]) == 16


def test_xuat_so_nhap_nhap_0_loi_va_xep_duoc(cd, tmp_path):
    """L4: dữ liệu đăng ký thật -> Sổ nhập -> phần mềm nhập 0 lỗi (chế độ FA) -> xếp chạy được."""
    import base64

    import cau_hinh_ws as ch
    api, qt = cd
    ids = _dung_san(api, qt)
    for ma_hs, nv in (("H1", [{"clb_id": ids["Robot"], "thi": True}, {"clb_id": ids["Cờ vua"]}, {"clb_id": ids["Tự do 1"]}]),
                      ("H2", [{"clb_id": ids["Tự do 1"]}, {"clb_id": ids["Cờ vua"]}])):
        h = ok(api.dk_dang_nhap("hoc_sinh", ma_hs, ok(api.dk_hs_dat_lai_pin(qt, ma_hs))["pin"]))["token"]
        ok(api.dk_hs_luu(h, nv))
    assert ma(api.dk_xuat_so_nhap(qt)) == "dk_sai_giai_doan"
    ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
    assert ma(api.dk_xuat_so_nhap(qt)) == "dk_thieu_diem"
    ok(api.dk_diem_dat(qt, "H1", ids["Robot"], "8"))
    d = ok(api.dk_xuat_ban_mau(qt))
    assert d["dinhDang"] == 1 and len(d["clb"]) == 3 and len(d["hocSinh"]) == 3
    assert [x["huyChuong"] for x in d["hocSinh"][0]["nv"]] == ["Vàng", "Bạc", None]
    p = str(tmp_path / "so.xlsx")
    assert ok(api.dk_xuat_so_nhap(qt, p))["so_hs"] == 3
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "wharton": True}})
    with open(p, "rb") as f:
        ra = api.import_so_nhap(base64.b64encode(f.read()).decode("ascii"))
    assert ra["ok"] and ra["errors"] == [], ra
    assert api.run_pipeline(seed=5)["ok"]
    assert ma(api.dk_xuat_so_nhap("sai")) == "dk_can_dang_nhap"
