"""DK5-L2: vùng chịu lỗi của diễn tập (sao lưu/khôi phục, khoá khi nghỉ, hạn chót, nộp lại, hoàn nguyên giữa giao dịch,
nhật ký chỉ thêm). Dữ liệu MÔ PHỎNG. Đồng hồ giả được tiêm vào, không `sleep`."""
import datetime
import glob
import hashlib
import os
import shutil
import sqlite3


import api as api_mod
from api import PipelineAPI
from du_lieu_test import dien_tap_dk5 as dt
from du_lieu_test.dien_tap_dk5 import ok

NHO = dict(so_hs=60, so_clb=8)


def _mach(tmp_path, dung_den="xep", ten="app.db"):
    api = PipelineAPI(str(tmp_path / ten))
    du = dt.dung_du_lieu(**NHO)
    return api, du, dt.chay(api, du, dung_den=dung_den)


def _bang(path, ten):
    c = sqlite3.connect(path)
    try:
        return c.execute("SELECT * FROM %s ORDER BY 1,2,3" % ten).fetchall()
    finally:
        c.close()


def _bam_csdl(path, bo_qua=()):
    """Băm của MỌI bảng (mọi dòng, mọi cột) trừ `bo_qua` — bằng nhau nghĩa là CSDL nguyên trạng."""
    c = sqlite3.connect(path)
    try:
        ten = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY 1")]
        h = hashlib.sha256()
        for t in ten:
            if t in bo_qua:
                continue
            h.update(t.encode())
            for r in c.execute("SELECT * FROM %s ORDER BY rowid" % t):
                h.update(repr(r).encode())
        return h.hexdigest()
    finally:
        c.close()


def test_l2a_sao_luu_roi_khoi_phuc_giong_het(tmp_path):
    api, du, kq = _mach(tmp_path)
    qt = kq["token_qt"]
    bak = os.path.join(str(tmp_path), ok(api.dk_sao_luu(qt))["tep"])
    assert os.path.exists(bak)
    # khôi phục = chép bản sao lưu sang chỗ khác rồi mở bằng phần mềm
    moi = str(tmp_path / "khoi_phuc.db")
    shutil.copy(bak, moi)
    kp = PipelineAPI(moi)
    for ten in ("match_results", "run_history", "students", "clubs", "club_scores", "dk_nguyen_vong", "dk_hoc_sinh"):
        assert _bang(moi, ten) == _bang(api.db_path, ten), ten          # MỌI dòng
    assert len(_bang(moi, "match_results")) == 60 * 2
    qt2 = ok(kp.dk_dang_nhap("quan_tri", "", dt.MAT_KHAU))["token"]
    assert ok(kp.dk_ket_qua_xep(qt2))["run_id"] == kq["xep"]["run_id"]


def test_l2b_khoa_khi_nghi_dung_dong_ho_gia(tmp_path):
    api = PipelineAPI(str(tmp_path / "app.db"))
    gio = [1000.0]
    api._dong_ho = lambda: gio[0]
    ok(api.dk_khoi_tao(dt.MAT_KHAU, dt.MA_TRUONG, ["T2"], [6, 12]))
    qt = ok(api.dk_dang_nhap("quan_tri", "", dt.MAT_KHAU))["token"]
    gio[0] += 119                                   # chưa quá 120 s: còn dùng được và đồng hồ nghỉ được làm mới
    assert api.dk_hs_danh_sach(qt)["ok"]
    gio[0] += 119
    assert api.dk_hs_danh_sach(qt)["ok"]
    gio[0] += 121                                   # quá 120 s không thao tác: khoá
    r = api.dk_hs_danh_sach(qt)
    assert not r["ok"] and r["errors"][0]["code"] == "dk_het_phien_nghi"
    assert api.dk_hs_danh_sach(qt)["errors"][0]["code"] == "dk_can_dang_nhap"     # phiên đã bị bỏ, phải đăng nhập lại
    qt2 = ok(api.dk_dang_nhap("quan_tri", "", dt.MAT_KHAU))["token"]
    assert api.dk_hs_danh_sach(qt2)["ok"]


def test_l2c_het_han_tu_dong_dong_va_tu_choi_nop(tmp_path):
    api, du, kq = _mach(tmp_path, dung_den="nhap_diem")      # đã nộp xong, đang ở nhap_diem
    qt = kq["token_qt"]
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))            # mở lại để thử hạn chót
    han = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat(timespec="minutes")
    ok(api.dk_dat_han(qt, "hs_dang_ky", han))
    ma = du["hs"][0]["ma"]
    token = ok(api.dk_dang_nhap("hoc_sinh", ma, kq["pin_hs"][ma]))["token"]
    cu = ok(api.dk_hs_nguyen_vong(token))["nguyen_vong"]
    api._dk_bay_gio = lambda: datetime.datetime.now() + datetime.timedelta(hours=2)      # đồng hồ tiêm: quá hạn
    r = api.dk_hs_luu(token, [])
    assert not r["ok"] and r["errors"][0]["code"] == "dk_hs_chua_mo"
    assert ok(api.dk_trang_thai())["giai_doan"] == "nhap_diem"
    assert ok(api.dk_hs_nguyen_vong(token))["nguyen_vong"] == cu       # lần nộp trước đó còn nguyên


def test_l2d_nop_lai_chi_giu_lan_cuoi(tmp_path):
    api = PipelineAPI(str(tmp_path / "app.db"))
    du = dt.dung_du_lieu(**NHO)
    kq = dt.chay(api, du, dung_den="nhap_diem")
    qt, ids = kq["token_qt"], kq["ids"]
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    ma = du["hs"][3]["ma"]
    td = [c["ten"] for c in du["clb"] if c["buoi"] == "T2" and c["loai"] == "Tự do"]
    token = ok(api.dk_dang_nhap("hoc_sinh", ma, kq["pin_hs"][ma]))["token"]
    ok(api.dk_hs_luu(token, [{"clb_id": ids[td[0]]}, {"clb_id": ids[td[1]]}]))
    ok(api.dk_hs_luu(token, [{"clb_id": ids[td[1]]}, {"clb_id": ids[td[0]]}]))     # nộp lại: đảo hạng
    nv = [x for x in ok(api.dk_hs_nguyen_vong(token))["nguyen_vong"]]
    assert [x["clb_id"] for x in nv] == [ids[td[1]], ids[td[0]]]
    c = sqlite3.connect(api.db_path)
    try:
        assert c.execute("SELECT COUNT(*) FROM dk_nguyen_vong WHERE student_id = ?", (ma,)).fetchone()[0] == 2
        assert c.execute("SELECT COUNT(*) FROM dk_nguyen_vong WHERE student_id = ? AND buoi = 'T3'", (ma,)).fetchone()[0] == 0
    finally:
        c.close()


def test_l2e_hong_giua_giao_dich_ghi_ve_nguyen_trang(tmp_path, monkeypatch):
    api, du, kq = _mach(tmp_path, dung_den="nhap_diem")
    qt = kq["token_qt"]
    # Hai bảng nhật ký CHỈ-THÊM được giữ có chủ ý khi hoàn nguyên (bất biến 4): chỉ được thêm dòng, dòng cũ không đổi.
    nhat_ky = ("dk_nhat_ky", "wharton_nhat_ky")
    truoc = _bam_csdl(api.db_path, bo_qua=nhat_ky)
    wh_truoc = _bang(api.db_path, "wharton_nhat_ky")
    nk_truoc = len(_bang(api.db_path, "dk_nhat_ky"))
    khoa_truoc = _bang(api.db_path, "stb_lock")

    def no(*a, **k):                                # chạy trong giao dịch ghi: SAU khi đã ghi kết quả + khoá STB, TRƯỚC run_history
        raise RuntimeError("loi gia lap giua giao dich")
    monkeypatch.setattr(api_mod, "luat_xep_de_ghi", no)
    r = api.dk_chot_va_xep(qt, 7)
    assert not r["ok"] and r["errors"][0]["code"] == "dk_chot_that_bai"        # run_pipeline tự rollback rồi trả lỗi; Chốt và xếp hoàn nguyên phần nhập sổ
    assert _bam_csdl(api.db_path, bo_qua=nhat_ky) == truoc               # mọi bảng khác giống hệt từng byte dữ liệu
    assert _bang(api.db_path, "wharton_nhat_ky")[:len(wh_truoc)] == wh_truoc
    assert len(_bang(api.db_path, "run_history")) == 0
    assert _bang(api.db_path, "stb_lock") == khoa_truoc and khoa_truoc[0][1] == 0      # chưa khoá hạt giống
    assert len(_bang(api.db_path, "dk_nhat_ky")) == nk_truoc + 1                       # đúng một dòng nhật ký «chot_that_bai»
    assert ok(api.dk_trang_thai())["giai_doan"] == "nhap_diem"
    monkeypatch.undo()
    d = ok(api.dk_chot_va_xep(qt, 7))                                  # sau lỗi vẫn chạy lại được và hạt giống 7 dùng được
    assert d["seed"] == 7 and len(_bang(api.db_path, "run_history")) == 1


def test_l2f_run_history_chi_them(tmp_path):
    api, du, kq = _mach(tmp_path)
    qt = kq["token_qt"]
    mot = _bang(api.db_path, "run_history")
    assert len(mot) == 1
    ok(api.dk_chot_va_xep(qt, 7))
    hai = _bang(api.db_path, "run_history")
    assert len(hai) == 2 and hai[:1] == mot                            # dòng cũ nguyên văn
    r = api.dk_chot_va_xep(qt, 99)                                      # hạt giống khoá: bị từ chối, không thêm dòng
    assert not r["ok"] and _bang(api.db_path, "run_history") == hai
    assert glob.glob(str(tmp_path / "app.db.bak-*"))                   # mỗi lần chốt đều sao lưu trước (bất biến 5)
