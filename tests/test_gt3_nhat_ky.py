"""GT3-L3: nhật ký thao tác (chỉ thêm). Dữ liệu MÔ PHỎNG, mật khẩu giả."""

import csv
import json
import sqlite3

import pytest

import nhat_ky as nk
import phan_quyen as pq

MK = "matkhau-gia-1"
MK2 = "matkhau-gia-2"


def ma_loi(r):
    return [e["code"] for e in r["errors"]]


def dong(api, **loc):
    con = sqlite3.connect(api.db_path)
    try:
        con.row_factory = sqlite3.Row
        where = " AND ".join(f"{k} = ?" for k in loc)
        sql = "SELECT * FROM nhat_ky_thao_tac" + (" WHERE " + where if where else "") + " ORDER BY id"
        return [dict(r) for r in con.execute(sql, list(loc.values()))]
    finally:
        con.close()


@pytest.fixture
def co_tk(api):
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]

    def vao(ten):
        api.dang_xuat()
        if ten:
            assert api.dang_nhap(ten, MK)["ok"]
    vao("quantri")
    return vao


# ------------------------------------------------------------------ chưa có tài khoản
def test_chua_co_tai_khoan_khong_ghi_dong_nao(api):
    assert api.create_or_update_club("A", "CLB A", 5, 0, "")["ok"]
    assert api.create_student_if_missing("s1", "Hoc sinh 1")["ok"]
    assert api.dang_nhap("x", MK)["errors"][0]["code"] == "gt3_chua_co_tai_khoan"
    assert dong(api) == []


def test_bang_va_trigger_co_san_va_rong(api):
    con = sqlite3.connect(api.db_path)
    try:
        ten = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE name LIKE 'nhat_ky_thao_tac%'")}
    finally:
        con.close()
    assert ten == {"nhat_ky_thao_tac", "nhat_ky_thao_tac_khong_sua", "nhat_ky_thao_tac_khong_xoa"}


# ---------------------------------------------------------------- mỗi hành động một dòng
def test_tao_tai_khoan_dau_tien_ghi_mot_dong_va_dang_nhap_them_mot(api):
    api.tao_tai_khoan("quantri", MK, "quan_tri")
    d = dong(api)
    assert [(r["nguoi"], r["vai"], r["hanh_dong"], r["ket_qua"]) for r in d] == [
        ("quantri", "quan_tri", "tao_tai_khoan", "ok")]
    api.dang_xuat()
    api.dang_nhap("quantri", MK)
    assert [r["hanh_dong"] for r in dong(api)] == ["tao_tai_khoan", "dang_xuat", "dang_nhap"]


def test_doi_cau_hinh_ghi_dung_mot_dong(api, co_tk):
    truoc = len(dong(api))
    r = api.create_or_update_club("A", "CLB A", 5, 0, "")
    assert r["ok"]
    moi = dong(api)[truoc:]
    assert len(moi) == 1
    assert (moi[0]["nguoi"], moi[0]["vai"], moi[0]["hanh_dong"], moi[0]["ket_qua"]) == (
        "quantri", "quan_tri", "create_or_update_club", "ok")
    assert json.loads(moi[0]["chi_tiet"])["club_id"] == "A"


def test_chay_xep_ghi_dung_mot_dong(api, co_tk):
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_student_if_missing("s1", "Hoc sinh 1")
    truoc = len(dong(api))
    api.run_pipeline()
    moi = dong(api)[truoc:]
    assert [r["hanh_dong"] for r in moi] == ["run_pipeline"]
    assert moi[0]["ket_qua"] in ("ok",) or moi[0]["ket_qua"]      # ok hoặc mã lỗi của lần chạy


def test_dang_nhap_sai_ghi_mot_dong_va_ten_that_duoc_ghi(api, co_tk):
    api.dang_xuat()
    truoc = len(dong(api))
    r = api.dang_nhap("quantri", "sai-mat-khau-xyz")
    assert ma_loi(r) == ["gt3_sai_thong_tin"]
    moi = dong(api)[truoc:]
    assert len(moi) == 1 and moi[0]["hanh_dong"] == "dang_nhap" and moi[0]["ket_qua"] == "gt3_sai_thong_tin"
    assert json.loads(moi[0]["chi_tiet"]) == {"ten": "quantri"} and moi[0]["nguoi"] is None


def test_ten_khong_co_that_khong_duoc_ghi_lai(api, co_tk):
    """Người dùng hay gõ nhầm mật khẩu vào ô tên: chỉ ghi tên khi là tài khoản có thật."""
    api.dang_xuat()
    api.dang_nhap("MatKhauToiGoNham123", "x")
    cuoi = dong(api)[-1]
    assert cuoi["chi_tiet"] == "{}"
    assert "MatKhauToiGoNham123" not in json.dumps(dong(api))


def test_dang_nhap_dung_ghi_nguoi_va_vai(api, co_tk):
    api.dang_xuat()
    api.dang_nhap("gv1", MK)
    cuoi = dong(api)[-1]
    assert (cuoi["nguoi"], cuoi["vai"], cuoi["hanh_dong"], cuoi["ket_qua"]) == ("gv1", "giao_vien", "dang_nhap", "ok")


def test_khoa_sau_nam_lan_sai_ghi_ma_tam_khoa(api, co_tk):
    api.dang_xuat()
    for _ in range(5):
        api.dang_nhap("gv1", "sai")
    assert dong(api)[-1]["ket_qua"] == "gt3_tam_khoa"
    api.dang_nhap("gv1", MK)           # đang khoá
    assert dong(api)[-1]["ket_qua"] == "gt3_tam_khoa"


def test_thao_tac_bi_tu_choi_cung_duoc_ghi(api, co_tk):
    co_tk("gv1")
    truoc = len(dong(api))
    assert ma_loi(api.delete_club("A")) == ["gt3_khong_du_quyen"]
    co_tk(None)
    assert ma_loi(api.reset_data()) == ["gt3_can_dang_nhap"]
    moi = dong(api)[truoc:]
    ghi = [(r["nguoi"], r["hanh_dong"], r["ket_qua"]) for r in moi if r["hanh_dong"] in ("delete_club", "reset_data")]
    assert ghi == [("gv1", "delete_club", "gt3_khong_du_quyen"), (None, "reset_data", "gt3_can_dang_nhap")]


def test_ham_ghi_cua_giao_vien_cung_duoc_ghi_ham_doc_thi_khong(api, co_tk):
    co_tk("quantri")
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_student_if_missing("s1", "Hoc sinh 1")
    co_tk("gv1")
    truoc = len(dong(api))
    assert api.get_dashboard_status()["ok"] and api.list_clubs()["ok"]
    assert len(dong(api)) == truoc                              # đọc: không ghi
    api.submit_preferences("s1", ["A"])
    moi = dong(api)[truoc:]
    assert [(r["nguoi"], r["vai"], r["hanh_dong"]) for r in moi] == [("gv1", "giao_vien", "submit_preferences")]


def test_thay_doi_tai_khoan_duoc_ghi_khong_kem_mat_khau(api, co_tk):
    assert api.tao_tai_khoan("gv2", MK2, "giao_vien")["ok"]
    assert api.doi_mat_khau(MK, "mat-khau-moi-123")["ok"]
    assert api.xoa_tai_khoan("gv2")["ok"]
    hd = [r["hanh_dong"] for r in dong(api)]
    assert hd[-3:] == ["tao_tai_khoan", "doi_mat_khau", "xoa_tai_khoan"]
    tao = dong(api, hanh_dong="tao_tai_khoan")[-1]
    assert json.loads(tao["chi_tiet"]) == {"ten": "gv2", "vai": "giao_vien"}
    assert dong(api, hanh_dong="doi_mat_khau")[-1]["chi_tiet"] == "{}"


def test_khong_dong_nao_chua_mat_khau_hay_noi_dung_tep(api, co_tk):
    api.dang_xuat()
    api.dang_nhap("quantri", "SaiMatKhau-ABC")
    api.dang_nhap("quantri", MK)
    api.tao_tai_khoan("gv9", "BiMat-KhongLo-77", "giao_vien")
    api.doi_mat_khau(MK, "MatKhauMoi-Khac-88")
    api.import_so_nhap("QUJDREVGR0hJSktMTU5PUA==" * 30)
    tat_ca = json.dumps(dong(api), ensure_ascii=False)
    for bi_mat in (MK, "SaiMatKhau-ABC", "BiMat-KhongLo-77", "MatKhauMoi-Khac-88", "QUJDREVG"):
        assert bi_mat not in tat_ca, bi_mat


def test_import_chi_ghi_do_dai_khong_ghi_noi_dung(api, co_tk):
    api.import_so_nhap("A" * 5000)
    ct = dong(api, hanh_dong="import_so_nhap")[-1]["chi_tiet"]
    assert len(ct) <= 300 and "AAAA" not in ct


# ---------------------------------------------------------------- chỉ thêm
def test_update_va_delete_bi_chan(api, co_tk):
    con = sqlite3.connect(api.db_path)
    try:
        with pytest.raises(sqlite3.DatabaseError, match="chi duoc them"):
            con.execute("UPDATE nhat_ky_thao_tac SET nguoi = 'x'")
        with pytest.raises(sqlite3.DatabaseError, match="chi duoc them"):
            con.execute("DELETE FROM nhat_ky_thao_tac")
        con.rollback()
        assert con.execute("SELECT COUNT(*) FROM nhat_ky_thao_tac").fetchone()[0] >= 2
    finally:
        con.close()


def test_reset_data_khong_xoa_nhat_ky(api, co_tk):
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    truoc = len(dong(api))
    r = api.reset_data("hoc_sinh", "XOA")
    assert r["ok"], r
    sau = dong(api)
    assert len(sau) == truoc + 1 and sau[-1]["hanh_dong"] == "reset_data"
    assert api.reset_data("tat_ca", "XOA")["ok"]
    assert len(dong(api)) == truoc + 2


# ------------------------------------------------------------- không làm hỏng thao tác chính
def test_ghi_nhat_ky_loi_khong_lam_hong_thao_tac(api, co_tk, caplog):
    """Bảng nhật ký biến mất (ghi sẽ lỗi): thao tác chính vẫn thành công, không ném, log không mang tham số."""
    con = sqlite3.connect(api.db_path)
    con.execute("DROP TABLE nhat_ky_thao_tac")
    con.commit()
    con.close()
    with caplog.at_level("WARNING"):
        r = api.create_or_update_club("B", "CLB B", 5, 0, "BI-MAT-NOI-DUNG")
    assert r["ok"]
    assert any("không ghi được nhật ký" in m for m in caplog.messages)
    assert "BI-MAT-NOI-DUNG" not in " ".join(caplog.messages)


# ------------------------------------------------------------------ xem + phân trang + CSV
def _them_nhieu(api, n):
    for i in range(n):
        api.create_or_update_club(f"C{i:02d}", f"CLB {i}", 5, 0, "")


def test_phan_trang_moi_nhat_truoc(api, co_tk):
    _them_nhieu(api, 12)
    tong = len(dong(api))
    r = api.get_nhat_ky_thao_tac(1, 5)
    assert r["ok"] and r["data"]["tong"] == tong and r["data"]["so_trang"] == -(-tong // 5)
    assert [x["hanh_dong"] for x in r["data"]["dong"]][0] == "create_or_update_club"
    ids = []
    for p in range(1, r["data"]["so_trang"] + 1):
        ids += [x["id"] for x in api.get_nhat_ky_thao_tac(p, 5)["data"]["dong"]]
    assert ids == sorted(ids, reverse=True) and len(ids) == tong == len(set(ids))
    assert api.get_nhat_ky_thao_tac(999, 5)["data"]["dong"] == []


def test_loc_theo_nguoi_va_hanh_dong(api, co_tk):
    _them_nhieu(api, 3)
    r = api.get_nhat_ky_thao_tac(1, 50, nguoi="quantri", hanh_dong="create_or_update_club")
    assert r["data"]["tong"] == 3 and all(x["hanh_dong"] == "create_or_update_club" for x in r["data"]["dong"])
    assert api.get_nhat_ky_thao_tac(1, 50, nguoi="khong-ai")["data"]["tong"] == 0


def test_tham_so_trang_xau_khong_ne_loi(api, co_tk):
    r = api.get_nhat_ky_thao_tac("abc", None)
    assert r["ok"] and r["data"]["page"] == 1 and r["data"]["page_size"] == 50
    assert api.get_nhat_ky_thao_tac(1, 100000)["data"]["page_size"] == 500


def test_chi_quan_tri_xem_va_xuat(api, co_tk):
    co_tk("gv1")
    assert ma_loi(api.get_nhat_ky_thao_tac()) == ["gt3_khong_du_quyen"]
    assert ma_loi(api.export_nhat_ky_thao_tac_csv()) == ["gt3_khong_du_quyen"]


def test_csv_utf8_bom_giu_nguyen_tieng_viet(api, co_tk, tmp_path):
    api.create_or_update_club("TH", "Câu lạc bộ Tiếng Việt Đẹp", 5, 0, "")
    api.dang_xuat()
    api.dang_nhap("quantri", MK)
    r = api.export_nhat_ky_thao_tac_csv(str(tmp_path / "nk.csv"))
    assert r["ok"], r
    raw = open(r["data"]["path"], "rb").read()
    assert raw.startswith(b"\xef\xbb\xbf")
    with open(r["data"]["path"], encoding="utf-8-sig", newline="") as f:
        d = list(csv.DictReader(f))
    assert list(d[0].keys()) == list(nk.COT)
    assert len(d) == r["data"]["n_rows"] and d == sorted(d, key=lambda x: int(x["id"]))
    assert any("Câu lạc bộ Tiếng Việt Đẹp" in x["chi_tiet"] for x in d)


def test_hai_ham_moi_la_quan_tri_va_phan_loai_ghi_dung():
    assert pq.QUYEN["get_nhat_ky_thao_tac"] == pq.QUAN_TRI
    assert pq.QUYEN["export_nhat_ky_thao_tac_csv"] == pq.QUAN_TRI
    assert not nk.nen_ghi("get_nhat_ky_thao_tac") and not nk.nen_ghi("get_dashboard_status")
    assert not nk.nen_ghi("liet_ke_tai_khoan") and not nk.nen_ghi("get_phien_dang_nhap")
    for n in ("run_pipeline", "reset_data", "update_workspace_config", "submit_preferences", "submit_club_scores",
              "luu_diem_danh", "export_ket_qua", "import_so_nhap", "dang_nhap", "dang_xuat", "tao_tai_khoan",
              "xoa_tai_khoan", "doi_mat_khau", "open_workspace", "export_nhat_ky_thao_tac_csv"):
        assert nk.nen_ghi(n), n


def test_moi_ham_ghi_cua_bang_quyen_deu_duoc_ghi():
    """Hàm không được ghi phải là hàm chỉ đọc: tên bắt đầu bằng get_/list_/… hoặc trong danh sách rõ ràng."""
    khong_ghi = [n for n in pq.QUYEN if not nk.nen_ghi(n)]
    for n in khong_ghi:
        # dk_*: cổng đăng ký có phiên + nhật ký riêng (`dk_nhat_ky`); nhật ký chung không được chứa PIN/mật khẩu trong đối số
        assert n.startswith(nk._DOC) or n in nk._KHONG_GHI or n.startswith("dk_"), n


# ------------------------------------------------------------------ fix1: db_path chụp trước, khoá có hạn, lọc tên
def _api_hai_ws(tmp_path):
    import workspace as ws
    from api import PipelineAPI
    goc = tmp_path / "goc"
    goc.mkdir()
    a = ws.tao(str(goc), "Truong A", None)
    api = PipelineAPI(ws.duong_dan_db(str(goc), a), thu_muc_goc_ws=str(goc))
    return api, a, str(goc)


def _dong_tai(duong):
    con = sqlite3.connect(duong)
    try:
        return [r[0] for r in con.execute("SELECT hanh_dong FROM nhat_ky_thao_tac ORDER BY id")]
    finally:
        con.close()


def test_open_workspace_ghi_vao_csdl_cu_khong_phai_csdl_moi(tmp_path):
    api, a, goc = _api_hai_ws(tmp_path)
    db_a = api.db_path
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    b = api.create_workspace("Truong B")["data"]["slug"]
    assert api.open_workspace(b)["ok"]
    db_b = api.db_path
    assert db_b != db_a
    assert "open_workspace" in _dong_tai(db_a)
    assert "open_workspace" not in _dong_tai(db_b)


def test_xoa_workspace_ghi_vao_csdl_dang_mo_va_khong_tao_tep_la_o_cho_cu(tmp_path):
    api, a, goc = _api_hai_ws(tmp_path)
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    b = api.create_workspace("Truong B")["data"]["slug"]
    db_a = api.db_path
    assert api.open_workspace(b)["ok"]
    assert api.open_workspace(a)["ok"]              # A mở lại; xoá B (không mở) thành công
    import os
    assert api.delete_workspace(b, "XOA")["ok"]
    assert "delete_workspace" in _dong_tai(db_a)
    # ghi vào CSDL đã bị dời đi: không sinh tệp rỗng ở chỗ cũ
    nk.ghi(api, "quantri", "quan_tri", "thu", "ok", "{}", db_path=os.path.join(goc, b, "app.db"))
    assert not os.path.exists(os.path.join(goc, b, "app.db"))


def test_khoa_ghi_dang_giu_thi_loi_goi_bi_tu_choi_tra_ve_ngay_va_dong_ghi_bu_sau(api, co_tk, monkeypatch):
    import threading
    import time
    monkeypatch.setattr(nk, "_CHO_KHOA_GIAY", 0.2)
    co_tk("gv1")
    truoc = len(dong(api))
    nha = threading.Event()
    da_giu = threading.Event()

    def giu():
        with api._khoa_ghi:
            da_giu.set()
            nha.wait(10)
    t = threading.Thread(target=giu)
    t.start()
    da_giu.wait(5)
    try:
        t0 = time.monotonic()
        r = api.reset_data("tat_ca", "XOA")          # quản trị mới được làm: giáo viên bị từ chối
        dt = time.monotonic() - t0
        assert not r["ok"] and ma_loi(r) == ["gt3_khong_du_quyen"]
        assert dt < 3
        assert len(dong(api)) == truoc               # chưa ghi được: khoá còn bị giữ
    finally:
        nha.set()
        t.join()
    for _ in range(50):
        if len(dong(api)) == truoc + 1:
            break
        time.sleep(0.1)
    sau = dong(api)
    assert len(sau) == truoc + 1 and sau[-1]["hanh_dong"] == "reset_data" and sau[-1]["ket_qua"] == "gt3_khong_du_quyen"


def test_loc_nguoi_khong_phan_biet_hoa_thuong(api, co_tk):
    _them_nhieu(api, 2)
    chuan = api.get_nhat_ky_thao_tac(1, 50, nguoi="quantri")["data"]["tong"]
    assert chuan > 0
    assert api.get_nhat_ky_thao_tac(1, 50, nguoi="QuanTri")["data"]["tong"] == chuan


def test_ham_dk_khong_vao_nhat_ky_chung_vi_doi_so_co_pin():
    """Mọi hàm dk_* (kể cả hàm ghi) ở ngoài nhật ký chung: đối số của chúng chứa PIN / mật khẩu."""
    ds = [n for n in pq.QUYEN if n.startswith("dk_")]
    assert ds and all(not nk.nen_ghi(n) for n in ds)
