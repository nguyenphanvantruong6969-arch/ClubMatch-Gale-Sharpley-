"""GT3-L4: bộ tài liệu minh chứng `docs/giai_trinh/`. Chỉ kiểm hình thức và độ khớp với mã; không chấm nội dung."""

import os
import re
import xml.etree.ElementTree as ET

import pytest

import i18n_errors

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THU_MUC = os.path.join(GOC, "docs", "giai_trinh")
TEP_MD = ["VAI_TRO_AI.md", "SO_DO_LUONG.md", "HUONG_DAN_CHAY.md", "DU_LIEU_DAU_VAO.md", "PHAN_CONG.md",
          "KICH_BAN_DEMO.md", "KICH_BAN_VIDEO.md"]
# Mã nội bộ không được lộ trong chữ giáo viên / học sinh đọc (GT1, L2, C3, I4, D-GT5, FA-M7 ...).
MA_NOI_BO = re.compile(r"\b(GT\d|D-GT\d|[LIC]\d|FA-[A-Z]{1,2}\d+|[A-Z]\d{1,2})\b")


def doc(ten):
    with open(os.path.join(THU_MUC, ten), encoding="utf-8") as f:
        return f.read()


@pytest.mark.parametrize("ten", TEP_MD)
def test_tep_ton_tai_va_noi_la_du_lieu_mo_phong(ten):
    assert os.path.isfile(os.path.join(THU_MUC, ten)), ten
    assert "mô phỏng" in doc(ten).lower(), ten


def test_so_do_svg_ton_tai_va_la_xml_hop_le_voi_nen_trang():
    duong = os.path.join(THU_MUC, "so_do_luong.svg")
    goc = ET.parse(duong).getroot()
    assert goc.tag.endswith("svg")
    noi_dung = open(duong, encoding="utf-8").read()
    assert "<rect" in noi_dung and "#ffffff" in noi_dung.lower(), "cần nền trắng để đọc được ở cả hai giao diện"
    assert "mô phỏng" in noi_dung.lower()


@pytest.mark.parametrize("ten", TEP_MD)
def test_khong_lo_ma_noi_bo(ten):
    sach = re.sub(r"```.*?```", "", doc(ten), flags=re.S)           # đoạn lệnh không tính
    sach = re.sub(r"`[^`]*`", "", sach)                              # tên tệp, hàm trong dấu huyền không tính
    loi = sorted(set(MA_NOI_BO.findall(sach)))
    assert not loi, (ten, loi)


def _ma_loi_nhac_toi(van_ban):
    """Mã lỗi viết trong dấu huyền ở dạng `ma_loi` mà có trong bảng lỗi hoặc trông như mã lỗi."""
    return {m for m in re.findall(r"`([a-z][a-z0-9_]{3,})`", van_ban) if m in i18n_errors.MESSAGES}


def test_moi_ma_loi_duoc_nhac_deu_co_that_va_chu_trich_dung_nguyen_van():
    van_ban = doc("DU_LIEU_DAU_VAO.md")
    ma = _ma_loi_nhac_toi(van_ban)
    assert len(ma) >= 10, "DU_LIEU_DAU_VAO.md phải trích các lỗi thật"
    for m in ma:
        vi = i18n_errors.MESSAGES[m]["vi"]
        assert vi in van_ban, f"{m}: chữ trích không đúng nguyên văn bảng lỗi"
    # mã viết trong dấu huyền trông như mã lỗi nhưng không có trong bảng
    for m in re.findall(r"`((?:gt3|so_nhap|wharton|khieu_nai|csv)_[a-z0-9_]+)`", "".join(doc(t) for t in TEP_MD)):
        assert m in i18n_errors.MESSAGES, m


def test_moi_duong_dan_nhac_toi_deu_ton_tai():
    sai = []
    for ten in TEP_MD:
        for tok in re.findall(r"`([^`\s]+)`", doc(ten)):
            if re.search(r"[*<>{}|]|\.\.\.|:", tok) or tok.startswith("-") or tok.endswith("/*"):
                continue
            if "/" in tok or re.search(r"\.(py|md|xlsx|svg|csv|json|bat|txt|html)$", tok):
                tok_sach = tok.replace("\\", "/").lstrip("./") if tok.startswith("./") else tok.replace("\\", "/")
                if tok_sach.startswith((".venv/", ".venv_build/")) or tok_sach in ("app.db", "match_results.csv", "nhat_ky_thao_tac.csv"):
                    continue
                if not (os.path.exists(os.path.join(GOC, tok_sach)) or os.path.exists(os.path.join(THU_MUC, tok_sach))):
                    sai.append((ten, tok))
    assert not sai, sai


def test_phan_cong_chi_la_mau_trong():
    van_ban = doc("PHAN_CONG.md")
    dong_bang = [d for d in van_ban.splitlines() if d.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", d)]
    assert len(dong_bang) >= 3                              # tiêu đề + hai thành viên
    for d in dong_bang[1:]:
        o = [c.strip() for c in d.strip("|").split("|")]
        assert o[0] in ("Thành viên 1", "Thành viên 2"), d
        assert all(c == "" for c in o[1:]), f"ô phải để trống cho học sinh tự điền: {d}"
    assert "Mã nguồn" in van_ban and "Nghiên cứu" in van_ban


def test_kich_ban_khong_con_buoc_cho_tich_hop():
    """I4: bản gộp đã có giải trình + tiêu chí, nên không còn dấu "(sau tích hợp)" ở tài liệu nào."""
    for ten in sorted(os.listdir(THU_MUC)):
        if ten.endswith(".md"):
            assert "(sau tích hợp)" not in doc(ten), ten
    for ten in ("KICH_BAN_DEMO.md", "KICH_BAN_VIDEO.md"):
        assert "Thử cấu hình" in doc(ten) and "Chế độ học sinh tra cứu" in doc(ten), ten
        assert re.search(r"^(\s*1\.\s|\|\s*1\s*\|)", doc(ten), re.M), f"{ten}: phải đánh số bước"


def test_vai_tro_ai_dan_nguon_nhat_ky_va_noi_khong_co_mo_hinh_hoc_may():
    van_ban = doc("VAI_TRO_AI.md")
    assert "docs/nhat_ky_ai/NHAT_KY_AI.md" in van_ban
    assert "không" in van_ban and "học máy" in van_ban
    req = open(os.path.join(GOC, "requirements.txt"), encoding="utf-8").read().lower()
    for thu_vien in ("torch", "tensorflow", "sklearn", "scikit", "transformers", "openai", "anthropic"):
        assert thu_vien not in req, thu_vien                # lời khẳng định "không có mô hình" phải còn đúng


# ---- Số liệu tài liệu nêu phải khớp một lần chạy THẬT (không gian bật chế độ huy chương, hạt giống 42) ----

def test_huong_dan_chay_dan_bat_che_do_huy_chuong_truoc_khi_nap_va_khong_con_buoc_phong():
    van_ban = doc("HUONG_DAN_CHAY.md")
    assert "Xếp theo loại CLB và huy chương" in van_ban
    assert "fa_cot_bo_qua" not in van_ban
    for ten in ("HUONG_DAN_CHAY.md", "KICH_BAN_DEMO.md", "KICH_BAN_VIDEO.md"):
        vb = doc(ten)
        assert "Phóng cho đủ" not in vb.replace("Không dùng nút \"Phóng cho đủ 100\"", ""), ten
        assert "phong_wharton_hang_loat" not in vb, ten
    assert van_ban.index("Bật chế độ huy chương trước khi nạp") < van_ban.index("kéo tệp")


def test_so_lieu_fa001_fa002_trong_tai_lieu_khop_lan_chay_that(tmp_path):
    import base64
    import csv

    pytest.importorskip("openpyxl")
    import cau_hinh_ws as ch
    from api import PipelineAPI

    api = PipelineAPI(str(tmp_path / "app.db"))
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True}})
    with open(os.path.join(GOC, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx"), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    tt = api.xem_truoc_so_nhap(b64)
    assert tt["ok"] and tt["data"]["canh_bao"] == [] and tt["data"]["loi"] == []
    assert (tt["data"]["n_clb"], tt["data"]["n_buoi"], tt["data"]["n_hoc_sinh"], tt["data"]["n_nguyen_vong"],
            tt["data"]["n_thi"]) == (8, 2, 120, 829, 194)
    assert api.import_so_nhap(b64)["ok"]
    kq = api.run_pipeline(42)
    assert kq["ok"] and kq["data"]["n_matched"] == 120 and kq["data"]["rounds_run"] == 8
    with open(kq["data"]["export_path"], encoding="utf-8") as f:
        dong = {(r["student_id"], r["buoi"]): (r["club_id"], r["rank_in_student_pref"]) for r in csv.DictReader(f)}
    ly_do = api.get_ly_do_ket_qua()["data"]
    assert ly_do["fa_bat"] is True and ly_do["cau"]["FA001"]["thu_2"]

    van_ban = doc("HUONG_DAN_CHAY.md")
    # Bảng FA001 trong mục 6 và dòng FA002 ngay dưới đó.
    for buoi in ("thu_2", "thu_5"):
        clb, hang = dong[("FA001", buoi)]
        assert "| `%s` | `%s` | %s |" % (buoi, clb, hang) in van_ban, (buoi, clb, hang)
    fa2 = "FA002` cùng hạt giống: `thu_2` nhận `%s` (hạng %s), `thu_5` nhận `%s` (hạng %s)" % (
        dong[("FA002", "thu_2")][0], dong[("FA002", "thu_2")][1],
        dong[("FA002", "thu_5")][0], dong[("FA002", "thu_5")][1])
    assert fa2 in van_ban
    demo, video = doc("KICH_BAN_DEMO.md"), doc("KICH_BAN_VIDEO.md")
    h = {k: v[1] for k, v in dong.items()}
    assert "Thứ 5 nhận nguyện vọng %s (`%s`)" % (h[("FA001", "thu_5")], dong[("FA001", "thu_5")][0]) in demo
    assert "Thứ 2 nhận nguyện vọng %s (`%s`)" % (h[("FA001", "thu_2")], dong[("FA001", "thu_2")][0]) in demo
    assert "Thứ 2 nhận nguyện vọng %s, Thứ 5 nhận nguyện vọng %s" % (h[("FA002", "thu_2")], h[("FA002", "thu_5")]) in demo
    assert "FA001: Thứ 5 hạng %s, Thứ 2 hạng %s; FA002: Thứ 2 hạng %s, Thứ 5 hạng %s" % (
        h[("FA001", "thu_5")], h[("FA001", "thu_2")], h[("FA002", "thu_2")], h[("FA002", "thu_5")]) in video


def test_ten_the_trong_kich_ban_khop_nhan_giao_dien():
    """Mọi "thẻ X" trong kịch bản demo/video phải là nhãn thẻ thật trên giao diện (i18n.js nav_*)."""
    with open(os.path.join(GOC, "i18n.js"), encoding="utf-8") as f:
        nhan = {n.strip() for n in re.findall(r'nav_\w+:\s*"([^"{]+)', f.read())}
    for ten in ("KICH_BAN_DEMO.md", "KICH_BAN_VIDEO.md"):
        with open(os.path.join(THU_MUC, ten), encoding="utf-8") as f:
            noi_dung = f.read()
        for the in re.findall(r"thẻ \**([A-ZĐÀ-Ỹ][\wÀ-ỹ]*(?: [a-zà-ỹ][\wà-ỹ]*)?)", noi_dung):
            the = the.strip("*").strip()
            assert any(the == n or n.startswith(the) or the.startswith(n) for n in nhan), (ten, the)
