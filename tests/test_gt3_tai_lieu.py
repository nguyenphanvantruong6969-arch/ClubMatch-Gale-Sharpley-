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


def test_kich_ban_danh_dau_buoc_can_tich_hop():
    for ten in ("KICH_BAN_DEMO.md", "KICH_BAN_VIDEO.md"):
        assert "(sau tích hợp)" in doc(ten), ten
        assert re.search(r"^(\s*1\.\s|\|\s*1\s*\|)", doc(ten), re.M), f"{ten}: phải đánh số bước"


def test_vai_tro_ai_dan_nguon_nhat_ky_va_noi_khong_co_mo_hinh_hoc_may():
    van_ban = doc("VAI_TRO_AI.md")
    assert "docs/nhat_ky_ai/NHAT_KY_AI.md" in van_ban
    assert "không" in van_ban and "học máy" in van_ban
    req = open(os.path.join(GOC, "requirements.txt"), encoding="utf-8").read().lower()
    for thu_vien in ("torch", "tensorflow", "sklearn", "scikit", "transformers", "openai", "anthropic"):
        assert thu_vien not in req, thu_vien                # lời khẳng định "không có mô hình" phải còn đúng
