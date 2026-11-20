"""UX1F-L2 — bố cục phiếu giải trình PDF: phiếu thường vừa MỘT trang, không có trang gần như trống, tiêu đề cột
không gãy giữa từ. Dữ liệu MÔ PHỎNG (du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx, seed 3)."""
import base64
import os
import re

import pytest

pytest.importorskip("reportlab")
pypdf = pytest.importorskip("pypdf")

import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_FA = os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx")
CAC_TIEU_DE = ["Nguyện vọng", "Huy chương", "Loại CLB", "Mức vào được", "Điểm thi"]


@pytest.fixture(scope="module")
def pdf_40_em(tmp_path_factory):
    d = tmp_path_factory.mktemp("ux1f_l2")
    (d / "goc").mkdir()
    (d / "xuat").mkdir()
    slug = ws.tao(str(d / "goc"), "Trường học", None)
    api = PipelineAPI(ws.duong_dan_db(str(d / "goc"), slug), thu_muc_xuat=str(d / "xuat"),
                      thu_muc_goc_ws=str(d / "goc"))
    assert api.update_workspace_config({"rules": {"fa_daa": True}})["ok"]
    with open(SO_FA, "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    assert api.run_pipeline(3)["ok"]
    with api._ket_noi_doc() as cur:
        sids = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id LIMIT 40")]
    r = api.export_phieu_giai_trinh_pdf(str(d / "xuat" / "p.pdf"), student_ids=sids)
    assert r["ok"], r
    return r["data"]["path"], r["data"]["n_trang"]


def _trang(duong):
    return [p.extract_text() for p in pypdf.PdfReader(duong).pages]


def test_40_em_toi_da_44_trang(pdf_40_em):
    duong, n = pdf_40_em
    assert n == len(_trang(duong)) <= 44          # trước UX1F: 75


def test_khong_co_trang_gan_nhu_trong(pdf_40_em):
    for i, t in enumerate(_trang(pdf_40_em[0]), 1):
        assert len(t) >= 200, (i, len(t))


def test_tieu_de_cot_khong_gay_giua_tu(pdf_40_em):
    chu = " ".join(" ".join(_trang(pdf_40_em[0])).split())      # gộp mọi khoảng trắng và xuống dòng
    for tu in CAC_TIEU_DE:
        assert tu in chu, tu
    assert "Huy chương" in chu and "Mức vào được" in chu
    # gãy giữa từ = có khoảng trắng chen vào GIỮA một từ tiêu đề
    assert not re.search(r"Huy ch\s+ương|Huy c\s+hương|Nguyện v\s+ọng|Nguyện\s+vọn\s+g|Mức v\s+ào|Mức vào đ\s+ược|Loại C\s+LB|Điểm th\s+i", chu)


# ---- UX1F-L2 (checker 1): tiêu đề của buổi CUỐI không bao giờ nằm một mình ở đáy trang
def _gt_gia(n_buoi, dai):
    def lc(i):
        return {"hang": i, "ten_clb": "CLB Giả %d" % i, "loai_clb": "TU_DO", "diem_em": 7.0, "chon_loc": True,
                "da_nhan": 10, "suc_chua": 20, "diem_chuan_loai": "diem", "diem_chuan": 6.0,
                "cau": "Câu giải thích khá dài về vì sao em được hoặc chưa được xếp. " * dai}
    buoi = [{"buoi": "Buổi %d" % (b + 1), "ket_qua": "x", "ten_clb": "CLB Giả 1", "cac_lua_chon": [lc(1), lc(2)],
             "diem_da_thi": [{"ten_clb": "CLB Giả 1", "diem_em": 7.0, "diem_chuan": 6.0, "diem_chuan_loai": "diem"}]}
            for b in range(n_buoi)]
    return {"buoi": buoi, "fa_bat": False, "run": {}}


def test_tieu_de_buoi_cuoi_khong_mot_minh_o_day_trang(tmp_path):
    import xuat_pdf
    from phieu_giai_trinh import _khoi_pdf
    xau = re.compile(r"^(Buổi \d+|Kết quả:.*|Điểm các CLB em đã thi)$")
    n_hai_trang = 0
    for n_buoi in range(3, 9):
        for dai in (0, 1, 2, 3):
            khoi = _khoi_pdf(xuat_pdf, _gt_gia(n_buoi, dai), ("s1", "Em Giả", "10A1"), 7, None, "Phiếu")
            duong = xuat_pdf.dung_pdf(str(tmp_path / ("p%d_%d.pdf" % (n_buoi, dai))), khoi)
            trang = pypdf.PdfReader(duong).pages
            n_hai_trang += len(trang) > 1
            for i, p in enumerate(trang, 1):
                dong = [d for d in p.extract_text().splitlines() if d.strip() and not d.startswith("Trang ")]
                assert not xau.match(dong[-1]), (n_buoi, dai, i, dong[-1])
    assert n_hai_trang > 0                                # phép quét có thật sự tạo phiếu nhiều trang
