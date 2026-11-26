"""DK9-L1: nạp Excel cho cổng đăng ký — `dk_excel_mau`, `dk_excel_xem_truoc`, `dk_excel_nap` (backend).

Dữ liệu mẫu đều là DỮ LIỆU GIẢ LẬP. Một tệp .xlsx ba trang tính: «Học sinh» (Mã HS | Họ tên | Lớp), «Giáo viên» (Họ tên),
«Phòng» (Tên phòng | Sức chứa)."""
import base64
import io
import sqlite3

import openpyxl
import pytest


def ok(r):
    assert r["ok"], r
    return r["data"]


def ma(r):
    assert not r["ok"], r
    return r["errors"][0]["code"]


def b64(sheets):
    """sheets: {tên trang tính: [hàng, ...]} (hàng đầu là tiêu đề) -> base64 của tệp .xlsx."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for ten, hang in sheets.items():
        ws = wb.create_sheet(ten)
        for h in hang:
            ws.append(list(h))
    bo = io.BytesIO()
    wb.save(bo)
    return base64.b64encode(bo.getvalue()).decode()


HS_TD = ["Mã HS", "Họ tên", "Lớp"]
GV_TD = ["Họ tên"]
PH_TD = ["Tên phòng", "Sức chứa"]


def tep_tot():
    return b64({
        "Học sinh": [HS_TD, ["H1", "Nguyễn An", "10A1"], ["H2", "Trần Bình", "11B2"], [10001.0, "Lê Chi", "6A2"]],
        "Giáo viên": [GV_TD, ["Cô Hoa"], ["Thầy Nam"]],
        "Phòng": [PH_TD, ["P101", 40], ["P102", 30.0]],
    })


@pytest.fixture
def cd(api):
    ok(api.dk_khoi_tao("matkhau", "TRUONG1", ["T2", "T3"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", "matkhau"))["token"]
    return api, qt


def dem(api):
    c = sqlite3.connect(api.db_path)
    try:
        return {t: c.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
                for t in ("dk_hoc_sinh", "dk_giao_vien", "dk_phong", "dk_nhat_ky")}
    finally:
        c.close()


# ---------------------------------------------------------------- (a) tệp mẫu
def test_tep_mau_xem_truoc_khong_dong_nao_khong_loi(cd):
    api, qt = cd
    m = ok(api.dk_excel_mau(qt))
    assert m["ten_tep"].endswith(".xlsx")
    wb = openpyxl.load_workbook(io.BytesIO(base64.b64decode(m["file_base64"])))
    assert wb.sheetnames[:3] == ["Học sinh", "Giáo viên", "Phòng"] and len(wb.sheetnames) == 4      # trang thứ tư = hướng dẫn
    assert [c.value for c in wb["Học sinh"][1]] == HS_TD
    assert wb["Học sinh"].max_row == 1 and wb["Giáo viên"].max_row == 1 and wb["Phòng"].max_row == 1   # chỉ hàng tiêu đề
    xt = ok(api.dk_excel_xem_truoc(qt, m["file_base64"]))
    for k in ("hoc_sinh", "giao_vien", "phong"):
        assert xt[k]["co"] is True and xt[k]["tong"] == 0 and xt[k]["moi"] == 0 and xt[k]["loi"] == []
    assert xt["thieu_sheet"] == [] and xt["so_hop_le"] == 0 and xt["co_the_nap"] is False


def test_tep_mau_khong_nap_gi_ca(cd):
    api, qt = cd
    t0 = dem(api)
    m = ok(api.dk_excel_mau(qt))
    assert ma(api.dk_excel_nap(qt, m["file_base64"])) == "dk_excel_khong_co_dong"
    assert dem(api) == t0


# ---------------------------------------------------------------- (b) tệp đúng
def test_nap_tep_dung_dung_so_dong_va_pin_tra_mot_lan(cd):
    api, qt = cd
    r = ok(api.dk_excel_nap(qt, tep_tot()))
    assert (r["hoc_sinh"]["moi"], r["hoc_sinh"]["da_co"]) == (3, 0)
    assert sorted(x["ma"] for x in r["hoc_sinh"]["pin"]) == ["10001", "H1", "H2"]            # 10001.0 -> "10001"
    assert all(len(x["pin"]) == 4 and x["pin"].isdigit() for x in r["hoc_sinh"]["pin"])
    assert {x["ma"]: (x["ten"], x["lop"]) for x in r["hoc_sinh"]["pin"]}["H1"] == ("Nguyễn An", "10A1")
    assert (r["giao_vien"]["moi"], len(r["giao_vien"]["pin"])) == (2, 2)
    assert sorted(x["ten"] for x in r["giao_vien"]["pin"]) == ["Cô Hoa", "Thầy Nam"]
    assert (r["phong"]["moi"], r["phong"]["da_co"]) == (2, 0) and r["loi"] == []
    hs = {x["ma"]: x for x in ok(api.dk_hs_danh_sach(qt))}
    assert hs["H2"]["khoi"] == 11 and hs["10001"]["khoi"] == 6 and hs["H1"]["lop"] == "10A1"      # khối suy từ lớp
    assert [(p["ten"], p["suc_chua"]) for p in ok(api.dk_phong_danh_sach(qt))] == [("P101", 40), ("P102", 30)]
    assert len(ok(api.dk_gv_danh_sach(qt))) == 2
    # PIN dùng được ngay; trong CSDL chỉ có băm (không có PIN thô)
    p = {x["ma"]: x["pin"] for x in r["hoc_sinh"]["pin"]}
    assert ok(api.dk_dang_nhap("hoc_sinh", "H1", p["H1"]))["token"]
    assert ma(api.dk_excel_nap(qt, "")) == "dk_excel_khong_phai_xlsx"


def test_trang_tinh_ten_khong_phan_biet_hoa_thuong_va_dau_cach(cd):
    api, qt = cd
    t = b64({"  HỌC SINH ": [HS_TD, ["H1", "An", "10A1"]], "phòng": [PH_TD, ["P1", 10]], "Hướng dẫn": [["bỏ qua"], ["H9", "x", "10A1"]]})
    xt = ok(api.dk_excel_xem_truoc(qt, t))
    assert xt["hoc_sinh"]["moi"] == 1 and xt["phong"]["moi"] == 1
    assert xt["giao_vien"]["co"] is False and xt["thieu_sheet"] == ["giao_vien"]
    r = ok(api.dk_excel_nap(qt, t))
    assert r["hoc_sinh"]["moi"] == 1 and r["giao_vien"]["moi"] == 0 and r["phong"]["moi"] == 1
    assert [x["ma"] for x in ok(api.dk_hs_danh_sach(qt))] == ["H1"]                          # «Hướng dẫn» không bao giờ nạp


# ---------------------------------------------------------------- (c) dòng lỗi
def tep_loi():
    return b64({
        "Học sinh": [HS_TD,
                     ["H1", "Nguyễn An", "10A1"],       # 2: tốt
                     ["", "Không mã", "10A1"],          # 3: mã trống
                     ["H3", "Không lớp", ""],           # 4: lớp trống
                     ["H4", "Khối lạ", "3A1"],          # 5: khối 3 ngoài dải 6–12
                     ["H1", "Trùng mã", "10A2"],        # 6: trùng mã với dòng 2
                     [None, None, None],                # 7: dòng trống: bỏ qua, không phải lỗi
                     ["H5", "x" * 61, "10A1"],          # 8: tên > 60
                     ["H6", "", "10A1"],                # 9: thiếu họ tên
                     ["H7", "Lê Bảy", "12C3"]],         # 10: tốt
        "Giáo viên": [GV_TD, ["Cô Hoa"], [""], ["Cô Hoa"], ["y" * 61], ["Thầy Nam"]],
        "Phòng": [PH_TD, ["P1", 40], ["P2", 0], ["P3", -5], ["P4", "abc"], ["", 20], ["P1", 10], ["P5", 25.5], ["P6", None], ["P7", 15]],
    })


def test_dong_loi_bo_qua_va_liet_ke_dong_hop_le_van_nap(cd):
    api, qt = cd
    t = tep_loi()
    xt = ok(api.dk_excel_xem_truoc(qt, t))
    hs = {e["dong"]: e["ly_do"] for e in xt["hoc_sinh"]["loi"]}
    assert hs == {3: "dk_excel_ma_trong", 4: "dk_excel_lop_trong", 5: "dk_excel_khoi_ngoai",
                  6: "dk_excel_trung_ma", 8: "dk_excel_ten_dai", 9: "dk_excel_ten_trong"}
    assert xt["hoc_sinh"]["moi"] == 2 and xt["hoc_sinh"]["tong"] == 8                         # dòng trống không đếm
    gv = {e["dong"]: e["ly_do"] for e in xt["giao_vien"]["loi"]}
    assert gv == {4: "dk_excel_trung_ten", 5: "dk_excel_ten_dai"} and xt["giao_vien"]["moi"] == 2   # dòng 3 trống bỏ qua
    ph = {e["dong"]: e["ly_do"] for e in xt["phong"]["loi"]}
    assert ph == {3: "dk_excel_suc_chua", 4: "dk_excel_suc_chua", 5: "dk_excel_suc_chua", 6: "dk_excel_ten_trong",
                  7: "dk_excel_trung_ten", 8: "dk_excel_suc_chua", 9: "dk_excel_suc_chua"}
    assert xt["phong"]["moi"] == 2 and xt["co_the_nap"] is True
    assert all(e["sheet"] == k for k in ("hoc_sinh", "giao_vien", "phong") for e in xt[k]["loi"])
    r = ok(api.dk_excel_nap(qt, t))
    assert r["hoc_sinh"]["moi"] == 2 and r["giao_vien"]["moi"] == 2 and r["phong"]["moi"] == 2
    assert len(r["loi"]) == len(xt["hoc_sinh"]["loi"]) + len(xt["giao_vien"]["loi"]) + len(xt["phong"]["loi"])
    assert sorted(x["ma"] for x in ok(api.dk_hs_danh_sach(qt))) == ["H1", "H7"]
    assert sorted(p["ten"] for p in ok(api.dk_phong_danh_sach(qt))) == ["P1", "P7"]
    assert sorted(g["ten"] for g in ok(api.dk_gv_danh_sach(qt))) == ["Cô Hoa", "Thầy Nam"]


# ---------------------------------------------------------------- (d) nạp lại
def test_nap_lai_giu_pin_hoc_sinh_them_moi_bo_qua_gv_phong_da_co(cd):
    api, qt = cd
    r1 = ok(api.dk_excel_nap(qt, tep_tot()))
    pin1 = {x["ma"]: x["pin"] for x in r1["hoc_sinh"]["pin"]}
    t2 = b64({
        "Học sinh": [HS_TD, ["H1", "Nguyễn An (sửa tên)", "10A3"], ["H9", "Mới Chín", "12A1"]],
        "Giáo viên": [GV_TD, ["Cô Hoa"], ["Cô Mới"]],
        "Phòng": [PH_TD, ["P101", 99], ["P103", 20]],
    })
    xt = ok(api.dk_excel_xem_truoc(qt, t2))
    assert (xt["hoc_sinh"]["moi"], xt["hoc_sinh"]["da_co"]) == (1, 1)
    assert (xt["giao_vien"]["moi"], xt["giao_vien"]["da_co"]) == (1, 1)
    assert (xt["phong"]["moi"], xt["phong"]["da_co"]) == (1, 1)
    r2 = ok(api.dk_excel_nap(qt, t2))
    assert [x["ma"] for x in r2["hoc_sinh"]["pin"]] == ["H9"]                                  # em cũ KHÔNG nhận PIN mới
    assert (r2["hoc_sinh"]["moi"], r2["hoc_sinh"]["da_co"]) == (1, 1)
    assert [x["ten"] for x in r2["giao_vien"]["pin"]] == ["Cô Mới"] and r2["giao_vien"]["da_co"] == 1
    assert (r2["phong"]["moi"], r2["phong"]["da_co"]) == (1, 1)
    hs = {x["ma"]: x for x in ok(api.dk_hs_danh_sach(qt))}
    assert hs["H1"]["ho_ten"] == "Nguyễn An (sửa tên)" and hs["H1"]["lop"] == "10A3"         # cập nhật thông tin
    assert ok(api.dk_dang_nhap("hoc_sinh", "H1", pin1["H1"]))["token"]                        # PIN cũ vẫn dùng được
    assert {p["ten"]: p["suc_chua"] for p in ok(api.dk_phong_danh_sach(qt))}["P101"] == 40     # phòng đã có: giữ nguyên
    assert len(ok(api.dk_gv_danh_sach(qt))) == 3


# ---------------------------------------------------------------- (e) lỗi mức tệp
def test_loi_muc_tep(cd):
    api, qt = cd
    for ham in (api.dk_excel_xem_truoc, api.dk_excel_nap):
        assert ma(ham(qt, "")) == "dk_excel_khong_phai_xlsx"
        assert ma(ham(qt, base64.b64encode(b"ma,ten,lop\nH1,An,10A1\n").decode())) == "dk_excel_khong_phai_xlsx"   # .csv đổi đuôi
        assert ma(ham(qt, "###không phải base64###")) == "dk_excel_khong_phai_xlsx"
        assert ma(ham(qt, tep_tot(), "ds.csv")) == "dk_excel_khong_phai_xlsx"                  # đuôi tệp khác .xlsx
        assert ma(ham(qt, base64.b64encode(b"x" * (5 * 1024 * 1024 + 1)).decode())) == "dk_excel_qua_lon"
        assert ma(ham(qt, b64({"Sheet1": [["a"], ["b"]]}))) == "dk_excel_khong_co_sheet"
        assert ma(ham(qt, b64({"Học sinh": [["Mã", "Tên", "Khối"], ["H1", "An", "10"]]}))) == "dk_excel_tieu_de_sai"   # lỗi gõ tiêu đề
        assert ma(ham(qt, b64({"Học sinh": [["H1", "An", "10A1"]]}))) == "dk_excel_tieu_de_sai"                      # thiếu hàng tiêu đề
    r = api.dk_excel_xem_truoc(qt, b64({"Phòng": [["Tên phòng", "Sức"], ["P1", 3]]}))
    assert r["errors"][0]["code"] == "dk_excel_tieu_de_sai" and r["errors"][0]["params"]["sheet"] == "Phòng"
    assert ok(api.dk_excel_xem_truoc(qt, tep_tot(), "DS.XLSX"))["hoc_sinh"]["moi"] == 3        # đuôi in hoa vẫn là .xlsx


def test_nhieu_dong_nhat_5000(cd):
    api, qt = cd
    hang = [HS_TD] + [["M%d" % i, "Em %d" % i, "10A1"] for i in range(5000)]
    assert ok(api.dk_excel_xem_truoc(qt, b64({"Học sinh": hang})))["hoc_sinh"]["moi"] == 5000
    hang.append(["M5000", "Em 5000", "10A1"])
    r = api.dk_excel_xem_truoc(qt, b64({"Học sinh": hang}))
    assert ma(r) == "dk_excel_qua_nhieu_dong" and r["errors"][0]["params"]["toi_da"] == 5000


# ---------------------------------------------------------------- (f) xem trước không ghi
def test_xem_truoc_khong_ghi_gi(cd):
    api, qt = cd
    t0 = dem(api)
    for t in (tep_tot(), tep_loi()):
        ok(api.dk_excel_xem_truoc(qt, t))
    assert dem(api) == t0                                                                      # cả nhật ký cũng không thêm dòng


def test_xem_truoc_dem_dung_so_da_co(cd):
    api, qt = cd
    ok(api.dk_excel_nap(qt, tep_tot()))
    t0 = dem(api)
    xt = ok(api.dk_excel_xem_truoc(qt, tep_tot()))
    assert (xt["hoc_sinh"]["moi"], xt["hoc_sinh"]["da_co"]) == (0, 3)
    assert (xt["giao_vien"]["moi"], xt["giao_vien"]["da_co"]) == (0, 2)
    assert (xt["phong"]["moi"], xt["phong"]["da_co"]) == (0, 2)
    assert dem(api) == t0


# ---------------------------------------------------------------- (g) quyền
def test_chi_quan_tri_goi_duoc(cd):
    api, qt = cd
    ok(api.dk_gv_tao_hang_loat(qt, "Cô An"))
    gv = ok(api.dk_gv_tao_hang_loat(qt, "Cô Bình"))["da_tao"][0]
    ok(api.dk_hs_nap_danh_sach(qt, "H1\tAn\t10A1"))
    pin_hs = ok(api.dk_hs_nap_danh_sach(qt, "H2\tBình\t10A1"))["pin"][0]["pin"]
    tg = ok(api.dk_dang_nhap("giao_vien", gv["ten"], gv["pin"]))["token"]
    th = ok(api.dk_dang_nhap("hoc_sinh", "H2", pin_hs))["token"]
    t0 = dem(api)
    for tok, mong in ((tg, "dk_khong_du_quyen"), (th, "dk_khong_du_quyen"), ("token-gia", "dk_can_dang_nhap"), (None, "dk_can_dang_nhap")):
        assert ma(api.dk_excel_mau(tok)) == mong
        assert ma(api.dk_excel_xem_truoc(tok, tep_tot())) == mong
        assert ma(api.dk_excel_nap(tok, tep_tot())) == mong
    assert dem(api) == t0


def test_ba_ham_nam_trong_bang_quyen_cong_khai():
    import phan_quyen as pq
    for ten in ("dk_excel_mau", "dk_excel_xem_truoc", "dk_excel_nap"):
        assert pq.QUYEN[ten] == pq.CONG_KHAI                                                   # cổng tự kiểm phiên, như mọi hàm dk_*


def test_chuoi_loi_moi_co_trong_bang_i18n():
    import i18n_errors as ie
    for ma_ in ("dk_excel_khong_phai_xlsx", "dk_excel_qua_lon", "dk_excel_khong_co_sheet", "dk_excel_tieu_de_sai", "dk_excel_qua_nhieu_dong",
                "dk_excel_khong_co_dong", "dk_excel_ma_trong", "dk_excel_ma_sai", "dk_excel_ten_trong", "dk_excel_ten_dai", "dk_excel_lop_trong",
                "dk_excel_khoi_ngoai", "dk_excel_trung_ma", "dk_excel_suc_chua", "dk_excel_trung_ten"):
        assert ie.MESSAGES[ma_]["vi"] and ie.MESSAGES[ma_]["en"]


# ---------------------------------------------------------------- ca biên
def test_ten_co_dau_ma_so_va_khoang_trang_thua(cd):
    api, qt = cd
    t = b64({"Học sinh": [HS_TD, [10002, "  Đặng   Thị  Ánh ", " 10A1 "], ["0007", "Ông Ích", "12A1"], ["A B", "Mã có cách", "10A1"]],
             "Giáo viên": [GV_TD, ["  Cô  Ngọc Ánh "]]})
    xt = ok(api.dk_excel_xem_truoc(qt, t))
    assert xt["hoc_sinh"]["loi"] == [{"sheet": "hoc_sinh", "dong": 4, "ly_do": "dk_excel_ma_sai", "params": {}}]
    r = ok(api.dk_excel_nap(qt, t))
    hs = {x["ma"]: x for x in ok(api.dk_hs_danh_sach(qt))}
    assert set(hs) == {"10002", "0007"} and hs["10002"]["ho_ten"] == "Đặng Thị Ánh" and hs["10002"]["lop"] == "10A1"
    assert r["giao_vien"]["pin"][0]["ten"] == "Cô Ngọc Ánh"


def test_bo_hoc_sinh_khi_giao_dien_khoa_danh_sach_hoc_sinh(cd):
    """Giai đoạn học sinh đã bắt đầu đăng ký: ô dán không thêm học sinh nữa; giao diện báo `bo_hoc_sinh` thì trang «Học sinh» bị bỏ qua."""
    api, qt = cd
    xt = ok(api.dk_excel_xem_truoc(qt, tep_tot(), "", True))
    assert xt["hs_bi_khoa"] is True and xt["hoc_sinh"]["co"] is False and xt["hoc_sinh"]["moi"] == 0 and "hoc_sinh" not in xt["thieu_sheet"]
    assert xt["giao_vien"]["moi"] == 2 and xt["phong"]["moi"] == 2
    r = ok(api.dk_excel_nap(qt, tep_tot(), "", True))
    assert r["hoc_sinh"]["moi"] == 0 and r["giao_vien"]["moi"] == 2 and r["phong"]["moi"] == 2
    assert ok(api.dk_hs_danh_sach(qt)) == []
    assert ok(api.dk_excel_xem_truoc(qt, tep_tot()))["hs_bi_khoa"] is False                    # mặc định: như cũ


def test_trang_tinh_khai_kich_thuoc_khong_lo_van_tu_choi_nhanh(cd):
    """Một ô ở XFD1048576 làm trang tính khai kích thước cực lớn: chỉ đọc vài cột đầu nên không tốn hàng chục giây."""
    import time
    api, qt = cd
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Học sinh"
    ws.append(HS_TD)
    ws.append(["H1", "An", "10A1"])
    ws.cell(row=1048576, column=16384, value="x")
    bo = io.BytesIO()
    wb.save(bo)
    t = base64.b64encode(bo.getvalue()).decode()
    t0 = time.time()
    r = api.dk_excel_xem_truoc(qt, t)
    assert time.time() - t0 < 5
    assert not r["ok"] and r["errors"][0]["code"] == "dk_excel_qua_nhieu_dong"
