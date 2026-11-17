"""Tích hợp GT1+GT2+GT3 (I2: chế độ học sinh khoá ở backend khi có tài khoản). Dữ liệu MÔ PHỎNG."""

import pytest

import phan_quyen as pq
from _fa import dung_fa_clb
from _wharton import tat_wharton

MK = "matkhau-gia-1"
HS = {"s1": "Nguyễn Văn Ánh", "s2": "Trần Thị Bé"}


def _dung(api):
    tat_wharton(api)
    dung_fa_clb(api, A=(1, None, None, None, None, "thu_2"), B=(5, None, None, None, None, "thu_2"))
    for sid, ten in HS.items():
        assert api.create_student_if_missing(sid, ten)["ok"]
        assert api.submit_preferences(sid, ["A", "B"])["ok"]
    assert api.run_pipeline(seed=3)["ok"]
    assert api.tao_ma_tra_cuu()["ok"]
    with api._ket_noi_doc() as cur:
        return dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))


def _ma_loi(r):
    return [e["code"] for e in (r.get("errors") or [])]


@pytest.fixture
def co_tk(api):
    ma = _dung(api)
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()
    assert api.dang_nhap("gv1", MK)["ok"]
    return api, ma


def test_chua_co_tai_khoan_che_do_hoc_sinh_khong_khoa_gi(api):
    ma = _dung(api)
    r = api.vao_che_do_hoc_sinh()
    assert r["ok"] and r["data"]["khoa"] is False
    assert api.get_run_history()["ok"]                       # vẫn như GT1 DONE
    assert api.tra_cuu_hoc_sinh("s1", ma["s1"])["ok"]
    assert api.thoat_che_do_hoc_sinh("", "")["ok"]


def test_o_che_do_hoc_sinh_chi_con_tra_cuu_va_thoat(co_tk):
    api, ma = co_tk
    assert api.vao_che_do_hoc_sinh()["data"]["khoa"] is True
    for goi in (lambda: api.get_run_history(), lambda: api.export_ket_qua(), lambda: api.run_pipeline(seed=1),
                lambda: api.reset_data(), lambda: api.get_giai_trinh_hoc_sinh("s2"),
                lambda: api.tao_lai_ma_tra_cuu(), lambda: api.dang_nhap("quantri", MK),
                lambda: api.dang_xuat(), lambda: api.vao_che_do_hoc_sinh()):
        r = goi()
        assert not r["ok"] and _ma_loi(r) == ["gt3_che_do_hoc_sinh"]
    # học sinh vẫn tra cứu được, và chỉ thấy thẻ của mình
    r = api.tra_cuu_hoc_sinh("s1", ma["s1"])
    assert r["ok"] and "Trần" not in str(r["data"])
    assert api.get_phien_dang_nhap()["ok"]


def test_thoat_can_dung_quan_tri_khong_ma_hoi_phan_nao_sai(co_tk):
    api, _ = co_tk
    api.vao_che_do_hoc_sinh()
    sai = [api.thoat_che_do_hoc_sinh("quantri", "sai"), api.thoat_che_do_hoc_sinh("khongco", MK)]
    assert [_ma_loi(r) for r in sai] == [["gt3_sai_thong_tin"]] * 2
    assert sai[0]["errors"] == sai[1]["errors"]
    gv = api.thoat_che_do_hoc_sinh("gv1", MK)                # đúng mật khẩu nhưng chỉ là giáo viên
    assert _ma_loi(gv) == ["gt3_sai_thong_tin"]
    assert api.get_phien_dang_nhap()["data"]["dang_nhap"] is False
    assert not api.get_run_history()["ok"]                   # vẫn khoá
    ok = api.thoat_che_do_hoc_sinh("quantri", MK)
    assert ok["ok"] and ok["data"]["vai"] == "quan_tri"
    assert api.get_run_history()["ok"]


def test_mat_khau_khong_vao_nhat_ky(co_tk):
    api, _ = co_tk
    api.vao_che_do_hoc_sinh()
    api.thoat_che_do_hoc_sinh("quantri", "sai-bi-mat-xyz")
    api.thoat_che_do_hoc_sinh("quantri", MK)
    with api._ket_noi_doc() as cur:
        dong = cur.execute("SELECT chi_tiet FROM nhat_ky_thao_tac").fetchall()
    assert dong and not any(MK in (d[0] or "") or "sai-bi-mat-xyz" in (d[0] or "") for d in dong)


def test_bang_quyen_che_do_hoc_sinh():
    assert pq.QUYEN["thoat_che_do_hoc_sinh"] == pq.CONG_KHAI
    assert pq.QUYEN["vao_che_do_hoc_sinh"] == pq.GIAO_VIEN


# ----------------------------------------------------------------------------- I3: nhật ký cho thao tác GT1/GT2
def _dong_nk(api, hanh_dong):
    with api._ket_noi_doc() as cur:
        return [dict(zip(("nguoi", "vai", "ket_qua", "chi_tiet"), r)) for r in cur.execute(
            "SELECT nguoi, vai, ket_qua, chi_tiet FROM nhat_ky_thao_tac WHERE hanh_dong = ? ORDER BY id",
            (hanh_dong,))]


def test_i3_moi_thao_tac_gt1_gt2_de_lai_dung_mot_dong(co_tk):
    api, ma = co_tk
    assert api.dang_xuat()["ok"] and api.dang_nhap("quantri", MK)["ok"]
    luat_thu = {"priority": "tier", "tiers": ["khong_co_nhom_nay"]}
    r = api.run_thu(luat_thu)
    assert r["ok"], r
    assert api.tao_ma_tra_cuu()["ok"]
    lai = api.tao_lai_ma_tra_cuu("s1")
    assert lai["ok"], lai
    assert api.export_ma_tra_cuu_csv()["ok"]
    assert api.export_phieu_giai_trinh()["ok"]
    # đúng MỘT dòng cho mỗi lời gọi (`_dung` gọi tao_ma_tra_cuu khi chưa có tài khoản nên không để dòng nào)
    for ten in ("run_thu", "tao_ma_tra_cuu", "tao_lai_ma_tra_cuu", "export_ma_tra_cuu_csv", "export_phieu_giai_trinh"):
        dong = _dong_nk(api, ten)
        assert len(dong) == 1, ten
        assert dong[0]["ket_qua"] == "ok" and dong[0]["nguoi"] == "quantri" and dong[0]["vai"] == "quan_tri", ten
    # mã tra cứu / mật khẩu / mã của học sinh khác không nằm trong nhật ký
    with api._ket_noi_doc() as cur:
        toan = str(cur.execute("SELECT * FROM nhat_ky_thao_tac").fetchall())
    for bi_mat in [lai["data"].get("ma", "?x?"), MK, *ma.values()]:
        assert str(bi_mat) not in toan


def test_i3_ap_dung_tieu_chi_de_lai_dung_mot_dong(tmp_path):
    from test_gt2_ap_dung import LUAT_THU, _mo
    a, _db, slug = _mo(tmp_path)
    assert a.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    r = a.run_thu(LUAT_THU)
    assert r["ok"], r
    k = a.ap_dung_tieu_chi(r["data"]["run_id"], slug)
    assert k["ok"], k
    for ten in ("run_thu", "ap_dung_tieu_chi"):
        dong = _dong_nk(a, ten)
        assert len(dong) == 1 and dong[0]["ket_qua"] == "ok" and dong[0]["nguoi"] == "quantri", ten
    assert _dong_nk(a, "update_workspace_config") == []         # lời gọi lồng bên trong không ghi thêm dòng


def test_i3_giao_vien_bi_tu_choi_quan_tri_va_dong_nhat_ky_ghi_loi(co_tk):
    api, _ = co_tk
    for ten, goi in (("run_thu", lambda: api.run_thu({"priority": "tier"})),
                     ("tao_lai_ma_tra_cuu", lambda: api.tao_lai_ma_tra_cuu("s1")),
                     ("export_ma_tra_cuu_csv", lambda: api.export_ma_tra_cuu_csv())):
        r = goi()
        assert not r["ok"]
        dong = _dong_nk(api, ten)
        assert len(dong) == 1 and dong[0]["nguoi"] == "gv1" and dong[0]["ket_qua"] != "ok", ten


def test_i3_chi_tiet_dong_nhat_ky_khong_lo_bi_mat(co_tk):
    api, _ = co_tk
    assert api.dang_xuat()["ok"] and api.dang_nhap("quantri", MK)["ok"]
    assert api.run_thu({"priority": "tier", "tiers": ["khong_co_nhom_nay"]})["ok"]
    assert api.tao_lai_ma_tra_cuu("s1")["ok"]
    assert api.export_phieu_giai_trinh(student_ids=["s1"])["ok"]
    for ten in ("run_thu", "tao_lai_ma_tra_cuu", "export_phieu_giai_trinh"):
        (dong,) = _dong_nk(api, ten)
        assert len(dong["chi_tiet"] or "") <= 300 and "Nguyễn" not in (dong["chi_tiet"] or ""), ten
    assert "s2" not in (_dong_nk(api, "tao_lai_ma_tra_cuu")[0]["chi_tiet"] or "")


# ----------------------------------------------------------------------------- I4: ca mẫu + gói minh chứng
def _nap_ca_mau():
    import os
    import sys
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(goc, "du_lieu_test"))
    sys.path.insert(0, os.path.join(goc, "docs", "giai_trinh"))
    import tao_ca_mau_giai_trinh as t
    return goc, t


def test_i4_ca_mau_sinh_lai_giong_het_tung_byte():
    import os
    goc, t = _nap_ca_mau()
    with open(os.path.join(goc, "docs", "giai_trinh", "CA_MAU.md"), encoding="utf-8", newline="") as f:
        co_san = f.read()
    lan1, lan2 = t.tao_ca_mau(), t.tao_ca_mau()
    assert lan1 == lan2                     # hai lần chạy cho cùng tệp
    assert lan1 == co_san, "CA_MAU.md đã cũ: chạy python du_lieu_test/tao_ca_mau_giai_trinh.py"
    assert "DỮ LIỆU MÔ PHỎNG" in co_san


def test_i4_moi_ca_khop_dau_ra_that_cua_phan_mem(tmp_path):
    import os
    import re
    goc, t = _nap_ca_mau()
    with open(os.path.join(goc, "docs", "giai_trinh", "CA_MAU.md"), encoding="utf-8") as f:
        van_ban = f.read()
    a, slug, _db = t._dung_workspace(str(tmp_path))
    ca = re.findall(r"^### Ca (\d+) — .+ \((\w+)\)$", van_ban, re.M)
    assert [int(n) for n, _ in ca] == [1, 2, 3, 4, 5, 6]
    with a._ket_noi_doc() as cur:
        xep = dict(cur.execute("SELECT student_id, club_id FROM match_results"))
        ten_clb = dict(cur.execute("SELECT club_id, name FROM clubs"))
        nv1 = dict(cur.execute("SELECT student_id, club_id FROM preferences WHERE rank = 1"))
    for n, sid in ca:
        duoc_nv1 = xep.get(sid) == nv1.get(sid)
        assert duoc_nv1 is (int(n) <= 3), f"ca {n} ({sid}): sai nhóm được/không được nguyện vọng 1"
        ket = ten_clb.get(xep.get(sid))
        assert f"Kết quả: **{ket or 'chưa có chỗ'}**" in van_ban
        gt = a.get_giai_trinh_hoc_sinh(sid)["data"]["buoi"][0]
        for x in gt["cac_lua_chon"]:
            assert f"- (hạng {x['hang']}) {x['cau']}" in van_ban, (sid, x["hang"])
    # thông báo lỗi trong tệp = thông báo thật
    r = a.update_workspace_config({"rules": t.LUAT_XUNG_DOT}, slug)
    assert not r["ok"] and f"- {t._msg(r)}" in van_ban
    for dong in t.i18n_errors.format_all(t._ca_bi_chan(str(tmp_path / "chan"))["errors"], "vi"):
        assert f"- {dong}" in van_ban
    # chạy thử không ghi đè kết quả chính thức, số em đổi chỗ khớp
    truoc = dict(xep)
    thu = a.run_thu(t.LUAT_THU)
    so_doi = a.so_sanh_lan_chay(thu["data"]["run_id"])["data"]["so_doi"]
    assert f"Số em đổi chỗ: **{so_doi}**." in van_ban
    with a._ket_noi_doc() as cur:
        assert dict(cur.execute("SELECT student_id, club_id FROM match_results")) == truoc


def test_i4_goi_minh_chung_dung_duoc_docx_va_html(tmp_path, monkeypatch):
    pytest.importorskip("docx")
    import docx
    _goc, _t = _nap_ca_mau()
    import tao_goi_minh_chung as g
    monkeypatch.setattr(g, "DUONG_DOCX", str(tmp_path / "goi.docx"))
    cac_tep = g.doc_cac_tep()
    assert [ten for ten, _ in cac_tep] == g.THU_TU
    assert g.ghi_docx(cac_tep)
    chu = "\n".join(p.text for p in docx.Document(str(tmp_path / "goi.docx")).paragraphs)
    assert "DỮ LIỆU MÔ PHỎNG" in chu and "Ca mẫu giải trình và tiêu chí" in chu
    trang = g.dung_html(cac_tep)
    assert "<table>" in trang and "Ca 6 —" in trang and "(sau tích hợp)" not in trang
