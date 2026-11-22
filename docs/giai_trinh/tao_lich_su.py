"""Dựng `LICH_SU_THAY_DOI.md`, `LICH_SU_COMMIT.csv` và `LICH_SU_THAY_DOI.pdf` và `.docx` từ lịch sử git THẬT của kho.

Chạy (cần clone ĐỦ lịch sử, không phải shallow):
    git fetch --unshallow origin        # nếu `git rev-parse --is-shallow-repository` in ra true
    python docs/giai_trinh/tao_lich_su.py

- Số liệu (số commit, ngày, tháng, nhánh đã gộp, tệp test) đọc trực tiếp từ git mỗi lần chạy.
- Bảng "minh chứng <-> commit" là danh sách CHỌN TAY ở `MINH_CHUNG` bên dưới; mỗi mã được kiểm bằng `git show`
  (mã không tồn tại thì dừng, không in báo cáo sai). Ngày và tiêu đề commit lấy từ git, không gõ tay.
- Chỉ nêu SỰ VIỆC. Không có nhận xét về mức đóng góp hay kết luận: phần đó do học sinh tự viết.
- `.pdf`: dùng lại bộ dựng của `tao_goi_minh_chung.py` (Chromium qua Playwright); thiếu thì chỉ bỏ riêng .pdf.
Dữ liệu trong báo cáo và các ví dụ là dữ liệu MÔ PHỎNG do máy sinh.
"""

import csv
import importlib.util
import os
import re
import subprocess
import sys
from collections import Counter

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(THU_MUC))
KHO_URL = "https://github.com/nguyenphanvantruong6969-arch/ClubMatch-Gale-Sharpley-"
DUONG_MD = os.path.join(THU_MUC, "LICH_SU_THAY_DOI.md")
DUONG_CSV = os.path.join(THU_MUC, "LICH_SU_COMMIT.csv")
DUONG_PDF = os.path.join(THU_MUC, "LICH_SU_THAY_DOI.pdf")
DUONG_DOCX = os.path.join(THU_MUC, "LICH_SU_THAY_DOI.docx")
DUONG_SVG_XU_LY = os.path.join(THU_MUC, "so_do_xu_ly.svg")
DUONG_SVG_BUOC = os.path.join(THU_MUC, "so_do_luong.svg")
# Hai danh tính tác giả trong git, quy về nhãn đọc được (không in tên hiển thị hay thư điện tử).
NHAN_TAC_GIA = {"Claude": "Claude Code (theo yêu cầu và duyệt của Truong)"}
NHAN_KHAC = "Tài khoản của Truong (gộp yêu cầu gộp PR)"

# Mỗi phần: (tiêu đề, yêu cầu của hội đồng được đáp ứng, ghi chú, [(mã commit, việc commit đó chứng minh)]).
MINH_CHUNG = [
    ("A. Kho mã nguồn và lịch sử thay đổi",
     "\"Kho mã và lịch sử thay đổi\"",
     "Kho có một commit gốc duy nhất; mọi thay đổi sau đó là commit riêng, có ngày, tiêu đề mang mã mục (mục 6).",
     [("e08af78", "Commit gốc 24/10/2026: nhập toàn bộ mã sản phẩm từ kho cũ `RB-STUFF-AFTER-UP` (392 tệp: thuật toán, giao diện, test, quy trình CI)"),
      ("54a5cf4", "Yêu cầu gộp PR #1 (A13), PR đầu tiên vào nhánh chính"),
      ("77b1cb9", "Ví dụ một mục đóng đủ vòng: mã, CHANGELOG, TIEN_DO, sổ đăng ký cùng được cập nhật (A13.11)")]),
    ("B. Phần mã cốt lõi: thuật toán ghép",
     "\"Mã nguồn/phần mã cốt lõi ... thuật toán ghép\"",
     "Các hàm lõi nằm trong `rbda_priority_pipeline.py`; mô tả từng lớp ở `docs/CO_CHE_THUAT_TOAN.md`. Các commit sau commit gốc "
     "đều thêm tham số mới có mặc định giữ nguyên hành vi cũ (bất biến 1 trong `CLAUDE.md`).",
     [("e08af78", "Có mặt từ đầu: `run_rbda`, `club_choice_function`, `compute_club_priority`, `generate_stb_lottery`, "
                  "`chen_stb_cho_hoc_sinh_moi`, `verify_stability`, `validate_data_integrity`, `docs/CO_CHE_THUAT_TOAN.md`"),
      ("c011f69", "A13: khoá ưu tiên theo điểm quyết tâm nối vào `run_rbda` (tham số mới, mặc định `None` = như cũ)"),
      ("3c22e0b", "FA-1: mô hình dữ liệu của chế độ xếp FA-DAA (huy chương, loại CLB, giữ chỗ)"),
      ("1037920", "FA-4 đến FA-8: bộ bọc FA-DAA, số thành viên tối thiểu, lý do, danh sách chờ, bảng nhu cầu, test tính chất"),
      ("adc42d8", "FA-SC-L5: khoá thứ tự bốc thăm theo từng ngày (bảng `stb_buoi`)"),
      ("c8d81a8", "FA-M3: đường B đặt huy chương, đủ 6 cách đặt (ngoại lệ bất biến 2 do Truong duyệt, ghi ở `4a59947`)"),
      ("77fa953", "Z-SOAT: kỹ năng `soat-ma` và `kiem_nhanh.py`: so từng dòng `match_results` của 3 bộ dữ liệu x 20 hạt giống với nhánh gốc")]),
    ("C. Dữ liệu đầu vào, ràng buộc và kiểm lỗi",
     "\"Giải thích dữ liệu đầu vào, ràng buộc\"",
     "Mô tả cột và lỗi: `docs/giai_trinh/DU_LIEU_DAU_VAO.md`. Dưới đây là các commit đưa phần đó vào mã.",
     [("e08af78", "`so_nhap.py`, `api_nhap.py`: đọc Sổ nhập CLB, báo lỗi theo dòng; sổ lỗi cố ý `SO_NHAP_CO_LOI_CO_Y.xlsx`"),
      ("a6738ca", "A13.12: soát nhập phía backend (kẹp trang, chuẩn hoá mã học sinh, từ chối mã rỗng, sao lưu trước khi xoá CLB)"),
      ("49c7319", "A13.11 (N3): CSDL đang bận báo `csdl_dang_ban`; chạy xếp dừng ngay khi không sao lưu được"),
      ("fbc82c9", "A14: thêm lớp của học sinh (`students.class_id`, `chuan_hoa_lop`)"),
      ("9db3039", "FG-2: xem trước sổ ở chế độ huy chương, cảnh báo gom theo mã; sổ mẫu 120 em"),
      ("9934af2", "SG-1: chặn chạy FA khi CLB tuyển chọn có đơn mà không có điểm")]),
    ("D. Xử lý khi không đủ chỗ",
     "\"Cách xử lý khi không đủ chỗ\"",
     "Nhánh trong sơ đồ 4.1. Mặc định: CLB đủ chỉ tiêu thì giữ theo thứ tự ưu tiên, em còn lại thử nguyện vọng kế tiếp; hết nguyện vọng thì "
     "ghi \"Chưa có chỗ\". Các commit dưới đây bổ sung cho chế độ FA-DAA.",
     [("e08af78", "Có từ đầu: vòng lặp `run_rbda` (từ chối rồi thử nguyện vọng kế tiếp, hết nguyện vọng thì không xếp), trang \"Chưa có chỗ\" khi xuất"),
      ("1037920", "FA-5, FA-6: đóng CLB thiếu thành viên tối thiểu; lý do, điểm chuẩn và danh sách chờ"),
      ("bb49d11", "GAP-1: điểm danh 3 buổi đầu; vắng không phép 2/3 thì nhả suất"),
      ("628cfb2", "GAP-2: mời người trong danh sách chờ vào suất vừa nhả"),
      ("e76bf48", "GAP-4: vòng 2, em chưa có CLB chọn vào chỗ còn trống"),
      ("f2e7702", "SG-3: chỗ \"lùi\" (không phải nguyện vọng gốc) lưu riêng và hiển thị riêng"),
      ("18fb8d7", "GAP-7: gợi ý chỉ tiêu kỳ sau từ nhu cầu thật")]),
    ("E. Vai trò của AI và phần việc từng thành viên",
     "\"Xác định rõ bộ phận nào dùng AI (nếu có) ... phần việc từng thành viên\"",
     "Kết luận kỹ thuật (phần mềm khi chạy không có mô hình học máy) nằm ở `docs/giai_trinh/VAI_TRO_AI.md`; việc AI giúp lúc viết mã nằm ở "
     "`docs/nhat_ky_ai/`. Bảng phân công (`PHAN_CONG.md`) do học sinh tự điền; báo cáo này không điền hộ.",
     [("1300e4a", "AI-LOG: nhật ký sử dụng AI dựng chỉ từ dữ liệu có trong kho (bản chi tiết)"),
      ("c43d4d9", "AI-LOG: bản đọc nhanh bằng lời thường (Word, 4 trang)"),
      ("6674e67", "GT3-L4: `VAI_TRO_AI.md`, `PHAN_CONG.md` (mẫu trống), `DU_LIEU_DAU_VAO.md`, `HUONG_DAN_CHAY.md`, sơ đồ luồng"),
      ("5926107", "GT-KH: kế hoạch đáp lại góp ý của hội đồng vòng trước (3 nhóm: giải thích kết quả, thử tiêu chí, vai trò và minh chứng)"),
      ("74ea6be", "FA-KH: kế hoạch FA-DAA; tiếp theo là `4a59947` ghi quyết định của Truong")]),
    ("F. Sơ đồ luồng xử lý",
     "\"Sơ đồ luồng xử lý\"",
     "Hai sơ đồ: đường đi của dữ liệu qua 12 bước (`so_do_luong.svg`) và luồng quyết định bên trong một lần chạy (`so_do_xu_ly.svg`, mục 4).",
     [("6674e67", "GT3-L4: `so_do_luong.svg`, `ve_so_do.py` (sơ đồ 12 bước) và test canh tài liệu"),
      ("4661b7b", "I4: ca mẫu giải trình và gói minh chứng `GOI_MINH_CHUNG.docx/.pdf` dựng lại từ các tệp .md")]),
    ("G. Bộ dữ liệu thử ẩn danh",
     "\"Bộ dữ liệu thử ẩn danh\"",
     "Mọi tên là \"Học sinh mô phỏng nnn\" và mã dạng `HS001`/`FA001`, do máy sinh với hạt giống cố định; không có học sinh thật.",
     [("e08af78", "Script sinh `du_lieu_test/tao_du_lieu_test.py`, `README.md`, `SO_NHAP_MAU_120HS_3BUOI.xlsx`, `SO_NHAP_CO_LOI_CO_Y.xlsx`"),
      ("2df59ce", "A13.6: sáu Sổ nhập mô phỏng (120 và 800 học sinh; hợp lệ, có lỗi, trống) và script sinh lại"),
      ("0e56a1b", "T2: sinh lại sáu sổ theo chữ hướng dẫn mới"),
      ("9db3039", "FG-2: `SO_NHAP_FA_MAU_120HS.xlsx` (sổ mẫu 120 em, chế độ huy chương)"),
      ("6c7bf4d", "FA-10: bảng mô phỏng so cơ chế cũ với FA-DAA (chỉ đo, không đổi mã sản phẩm)"),
      ("4661b7b", "I4: `CA_MAU.md`, ca mẫu có số liệu để đối chiếu đầu vào với kết quả")]),
    ("H. Demo điều chỉnh một quy tắc phân bổ",
     "\"Demo điều chỉnh một quy tắc phân bổ, đối chiếu được đầu vào với kết quả\"",
     "Kịch bản từng bước: `KICH_BAN_DEMO.md`, bước 10 (đổi tiêu chí ở chế độ chạy thử, so sánh với kết quả chính thức, áp dụng hoặc bỏ). "
     "Chạy thử không ghi đè kết quả chính thức.",
     [("ecf2130", "GT2-L1: tiêu chí xếp bằng lời thường (`tieu_chi.py`, `get_tieu_chi`)"),
      ("3f5957c", "GT2-L2: chạy thử (`run_thu`, cột `loai_chay`), tách khỏi lần chạy chính thức"),
      ("e92d544", "GT2-L3: so sánh hai lần chạy (`so_sanh_lan_chay`), xuất HTML và CSV"),
      ("20f396d", "GT2-L4: áp dụng tiêu chí của một lần chạy thử (`ap_dung_tieu_chi`)"),
      ("cc7aa23", "GT4-L7: làm lại các khung tiêu chí, chạy thử, so sánh"),
      ("bd93958", "MT1-L2: ba thẻ mục tiêu, đổi quy tắc bằng 1 đến 2 lần bấm, một giao dịch, chỉ quản trị"),
      ("d9a3f50", "I3: nhật ký thao tác ghi cả chạy thử, áp dụng tiêu chí, mã tra cứu"),
      ("b30faa2", "Sửa tên thẻ trong kịch bản demo và thêm test canh tên thẻ có thật")]),
    ("I. Hướng dẫn chạy và kiểm tự động",
     "\"Cung cấp ... hướng dẫn chạy\"",
     "Lệnh chạy: `README.md` (mục Cách chạy) và `docs/giai_trinh/HUONG_DAN_CHAY.md`.",
     [("e08af78", "`README.md`, `HUONG_DAN_CAI_DAT.md`, quy trình CI `tests.yml` và `build-windows-exe.yml`, bộ test ban đầu"),
      ("2474f3d", "GT3-L4 fix1: số liệu trong hướng dẫn lấy từ lần chạy thật trên sổ mẫu"),
      ("572685d", "Sửa CI (giữ LF cho `CA_MAU.md`) để quy trình xanh trên Windows"),
      ("b765f21", "CI-HUY: huỷ lượt CI cũ khi có commit mới cùng nhánh")]),
]

PHA = [  # (tiền tố mã mục, ý nghĩa; chỉ ghi điều đã có trong tài liệu kế hoạch của kho)
    ("A", "Điểm quyết tâm (A13), lớp học sinh (A14) và các mục A khác trong sổ đăng ký"),
    ("T4M", "Bộ công cụ Microsoft Forms và Lists cho trường"),
    ("T", "Nghiên cứu và làm gọn giao diện (T1 đến T4)"),
    ("FA", "Cơ chế xếp mới FA-DAA (huy chương, loại CLB, đóng CLB thiếu người, danh sách chờ)"),
    ("GAP", "Phần sau xếp của FA-DAA: điểm danh, danh sách chờ, khiếu nại, vòng 2, bảng điều khiển"),
    ("FG", "Gộp biểu mẫu Forms"),
    ("SG", "Mười hai mục SG-1 đến SG-12, làm song song (`docs/ke_hoach/SG_SONG_SONG.md`)"),
    ("GT", "Giải trình kết quả, thử tiêu chí, tài khoản, nhật ký thao tác, gói minh chứng"),
    ("UX", "Làm lại giao diện (UX1, UX2)"),
    ("XP", "Xuất PDF"),
    ("MT", "Ba thẻ mục tiêu"),
    ("SM", "Sổ mẫu"),
    ("CI", "Quy trình kiểm tự động"),
]


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=GOC, capture_output=True, text=True, encoding="utf-8", check=True)
    return r.stdout


def nhan_tac_gia(ten: str) -> str:
    return NHAN_TAC_GIA.get(ten, NHAN_KHAC)


def doc_commit(ma: str) -> dict:
    """Đọc một commit; không có thì dừng (không in báo cáo trích mã sai)."""
    try:
        d = git("show", "-s", "--date=short", "--format=%H%x09%h%x09%ad%x09%an%x09%s", ma).strip().split("\t", 4)
    except subprocess.CalledProcessError:
        sys.exit("Không tìm thấy commit %s. Clone đủ lịch sử rồi chạy lại (git fetch --unshallow origin)." % ma)
    return {"day_du": d[0], "ngan": d[1], "ngay": d[2], "tac_gia": nhan_tac_gia(d[3]), "tieu_de": d[4]}


def o(chu: str) -> str:
    return chu.replace("|", "\\|")


def tong_quan() -> dict:
    if git("rev-parse", "--is-shallow-repository").strip() == "true":
        sys.exit("Kho đang là bản shallow: lịch sử thiếu. Chạy `git fetch --unshallow origin` rồi chạy lại.")
    dong = [d.split("\t") for d in git("log", "--format=%h%x09%ad%x09%an%x09%s%x09%P", "--date=short").splitlines()]
    ngay = sorted(d[1] for d in dong)
    return {
        "tong": len(dong),
        "gop": sum(1 for d in dong if len(d[4].split()) > 1),
        "dau": ngay[0], "cuoi": ngay[-1],
        "thang": sorted(Counter(n[:7] for n in ngay).items()),
        "tac_gia": Counter(nhan_tac_gia(d[2]) for d in dong),
        "gốc": git("rev-list", "--max-parents=0", "HEAD").split(),
        "head": git("rev-parse", "--short", "HEAD").strip(),
        "test": len(git("ls-files", "tests/*.py", "tests/**/*.py").split()),
        "dong": dong,
    }


def bang_pha(dong: list) -> list:
    """Đếm commit không phải gộp theo tiền tố mã mục (tiền tố dài nhất khớp trước)."""
    dem, dau, cuoi = Counter(), {}, {}
    thu_tu = sorted(PHA, key=lambda p: -len(p[0]))
    for h, ngay, _, tieu_de, cha in dong:
        if len(cha.split()) > 1:
            continue
        for tien_to, _ in thu_tu:
            if re.match(r"%s(?![^\W\d_])" % re.escape(tien_to), tieu_de):
                dem[tien_to] += 1
                dau[tien_to] = min(dau.get(tien_to, ngay), ngay)
                cuoi[tien_to] = max(cuoi.get(tien_to, ngay), ngay)
                break
    return [(t, y, dem[t], dau[t], cuoi[t]) for t, y in PHA if dem[t]]


def danh_sach_pr() -> list:
    ra = []
    for d in git("log", "--merges", "--format=%h%x09%ad%x09%s", "--date=short").splitlines():
        h, ngay, tieu_de = d.split("\t", 2)
        m = re.match(r"Merge pull request #(\d+) from [^/]+/(\S+)", tieu_de)
        if m:
            ra.append((int(m.group(1)), h, ngay, m.group(2)))
    for d in git("log", "--format=%h%x09%ad%x09%s", "--date=short").splitlines():
        h, ngay, tieu_de = d.split("\t", 2)
        m = re.search(r"\(#(\d+)\)$", tieu_de)
        if m:
            ra.append((int(m.group(1)), h, ngay, "(tiêu đề ghi số PR) " + o(tieu_de[:60])))
    return sorted(ra)


def dung_md(tq: dict) -> str:
    L = []
    them = L.append
    them("# Báo cáo lịch sử thay đổi và sơ đồ luồng xử lý")
    them("")
    them("> **Dữ liệu mô phỏng.** Mọi tên và điểm trong dự án do máy sinh với hạt giống cố định, không phải học sinh hay khảo sát thật.")
    them("> Báo cáo chỉ nêu sự việc đọc từ lịch sử git; nhận xét về mức đóng góp và mọi kết luận do học sinh thực hiện đề tài tự viết.")
    them("> Tệp này do `docs/giai_trinh/tao_lich_su.py` sinh ra từ git, mốc đối chiếu `%s`. Không sửa tay; sửa script rồi chạy lại." % tq["head"])
    them("")
    them("## 1. Cách đối chiếu")
    them("")
    them("Mỗi mã trong báo cáo là mã commit rút gọn. Xem một commit (tiêu đề, ngày, tệp đổi, nội dung đổi):")
    them("")
    them("```bash")
    them("git show --stat <mã>")
    them("git log --oneline --follow -- rbda_priority_pipeline.py")
    them("```")
    them("")
    them("Trên web: `%s/commit/<mã đầy đủ>`. Bảng đầy đủ mọi commit: `docs/giai_trinh/LICH_SU_COMMIT.csv` (mã, ngày, tác giả, tiêu đề, số tệp)." % KHO_URL)
    them("Cần clone đầy đủ: nếu `git rev-parse --is-shallow-repository` in `true` thì chạy `git fetch --unshallow origin`.")
    them("")
    them("## 2. Số liệu tổng quan")
    them("")
    them("| Mục | Giá trị |")
    them("|---|---|")
    them("| Số commit | %d (trong đó %d commit gộp nhánh) |" % (tq["tong"], tq["gop"]))
    them("| Khoảng thời gian trong kho | %s đến %s |" % (tq["dau"], tq["cuoi"]))
    them("| Commit gốc | %s |" % ", ".join("`%s`" % h for h in tq["gốc"]))
    them("| Tệp test Python | %d |" % tq["test"])
    them("| Yêu cầu gộp PR vào nhánh chính | %d (mục 5) |" % len(danh_sach_pr()))
    for t, n in tq["tac_gia"].most_common():
        them("| Commit của: %s | %d |" % (o(t), n))
    them("")
    them("Commit theo tháng: " + "; ".join("%s: %d" % (t, n) for t, n in tq["thang"]) + ".")
    them("")
    them("Nhãn tác giả được quy từ hai danh tính git; tên hiển thị và thư điện tử không in ở đây. Các commit của tài khoản Truong đều là commit gộp PR.")
    them("")
    them("## 3. Minh chứng và commit tương ứng")
    them("")
    them("Mỗi phần ứng với một ý của yêu cầu \"Bổ sung bằng chứng kỹ thuật và làm rõ vai trò của AI\". Ngày và tiêu đề lấy nguyên từ git.")
    them("")
    for tieu_de, yeu_cau, ghi_chu, ds in MINH_CHUNG:
        them("### %s" % tieu_de)
        them("")
        them("Ứng với yêu cầu: %s. %s" % (yeu_cau, ghi_chu))
        them("")
        them("| Commit | Ngày | Tác giả git | Tiêu đề commit | Chứng minh |")
        them("|---|---|---|---|---|")
        for ma, vai_tro in ds:
            c = doc_commit(ma)
            them("| `%s` | %s | %s | %s | %s |" % (c["ngan"], c["ngay"], o(c["tac_gia"].split(" (")[0]), o(c["tieu_de"][:90]), o(vai_tro)))
        them("")
    them("## 4. Sơ đồ luồng xử lý")
    them("")
    them("### 4.1. Luồng xử lý một lần chạy xếp, gồm nhánh không đủ chỗ")
    them("")
    them("[[SO_DO_XU_LY]]")
    them("")
    them("Tệp: `docs/giai_trinh/so_do_xu_ly.svg`, dựng bằng `docs/giai_trinh/ve_so_do_xu_ly.py`. Tên hàm trong sơ đồ là tên thật "
         "trong `rbda_priority_pipeline.py` và `api.py`. Thứ tự cố định: sao lưu, kiểm dữ liệu, khoá bốc thăm, xếp, soát ổn định, "
         "ghi trong một giao dịch, xuất.")
    them("")
    them("Điểm cần đọc kỹ:")
    them("")
    them("- **Điểm quyết định** (hình thoi, màu vàng) là nơi lần chạy có thể dừng; dừng thì dữ liệu giữ nguyên như trước khi chạy.")
    them("- **Nhánh không đủ chỗ** (màu cam và đỏ) chỉ xảy ra khi CLB đã đủ chỉ tiêu. Phần mềm không xếp ngẫu nhiên em vào CLB khác: "
         "em thử nguyện vọng kế tiếp, hết nguyện vọng thì được liệt kê ở trang \"Chưa có chỗ\".")
    them("- **Bộ phận nào là AI:** không có. Mọi bước là thuật toán xác định (Deferred Acceptance, dự trữ mềm, bốc thăm một lần có khoá, "
         "ưu tiên hai tầng). Kiểm bằng `requirements.txt`: không có thư viện học máy. AI (Claude Code) chỉ tham gia lúc viết mã và tài liệu, "
         "ghi ở `docs/nhat_ky_ai/`.")
    them("")
    them("### 4.2. Đường đi của dữ liệu qua 12 bước")
    them("")
    them("[[SO_DO_BUOC]]")
    them("")
    them("Từng bước, tệp mã và cách xử lý lỗi: `docs/giai_trinh/SO_DO_LUONG.md`.")
    them("")
    them("## 5. Các yêu cầu gộp PR vào nhánh chính")
    them("")
    them("| PR | Commit gộp | Ngày | Nhánh |")
    them("|---|---|---|---|")
    for so, h, ngay, nhanh in danh_sach_pr():
        them("| #%d | `%s` | %s | %s |" % (so, h, ngay, o(nhanh)))
    them("")
    them("Các số PR vắng trong bảng (#2, #5, #22, #26) không có commit gộp trong lịch sử của kho; kho không cho biết lý do.")
    them("")
    them("## 6. Giai đoạn theo mã mục")
    them("")
    them("Đếm commit không phải gộp theo tiền tố mã mục trong tiêu đề. Chỉ một phần commit mang mã nên tổng nhỏ hơn số commit ở mục 2. "
         "Nội dung từng mã: `CHANGELOG.md` và `docs/ke_hoach/TIEN_DO.md`.")
    them("")
    them("| Mã | Nội dung | Số commit | Từ | Đến |")
    them("|---|---|---|---|---|")
    for t, y, n, d, c in bang_pha(tq["dong"]):
        them("| %s | %s | %d | %s | %s |" % (t, o(y), n, d, c))
    them("")
    them("## 7. Giới hạn của minh chứng này")
    them("")
    them("- Lịch sử trong kho này bắt đầu ngày %s bằng commit gốc `%s`, nhập từ kho cũ `RB-STUFF-AFTER-UP`. Phần việc từ 26/08/2026 đến "
         "ngày đó (bản gốc của học sinh, sửa lỗi cho Windows, các vòng rà soát) **không có commit riêng ở đây**; nguồn duy nhất trong kho là "
         "`BAN_GIAO.md` và `docs/nhat_ky_ai/`. Muốn có commit của giai đoạn đó, lấy lịch sử của kho cũ." % (tq["dau"], tq["gốc"][0][:7]))
    them("- Bảng phân công `docs/giai_trinh/PHAN_CONG.md` còn trống: học sinh thực hiện đề tài tự điền. Số commit theo tác giả git ở mục 2 "
         "không cho biết ai viết phần nào, vì phần lớn commit do công cụ AI ghi theo yêu cầu của Truong.")
    them("- Một số commit mang chữ WIP trong tiêu đề (làm dở, test chưa chạy xong). Chúng được giữ nguyên vì lịch sử không bị viết lại.")
    them("- Số liệu kiểm thử nhắc trong các tài liệu là số trên dữ liệu mô phỏng.")
    them("")
    return "\n".join(L)


def ghi_csv(tq: dict) -> None:
    with open(DUONG_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["ma", "ngay", "tac_gia", "gop_nhanh", "so_tep_doi", "tieu_de"])
        so_tep = {}
        ma = None
        for d in git("log", "--no-merges", "--format=@@%h", "--name-only").splitlines():
            if d.startswith("@@"):
                ma = d[2:]
                so_tep[ma] = 0
            elif d.strip():
                so_tep[ma] += 1
        for h, ngay, tg, tieu_de, cha in tq["dong"]:
            w.writerow([h, ngay, nhan_tac_gia(tg), "co" if len(cha.split()) > 1 else "", so_tep.get(h, ""), tieu_de])


def ghi_pdf(md: str) -> bool:
    """Dùng lại bộ dựng HTML/PDF của gói minh chứng; chèn hai SVG vào chỗ đánh dấu."""
    duong = os.path.join(THU_MUC, "tao_goi_minh_chung.py")
    spec = importlib.util.spec_from_file_location("tao_goi_minh_chung", duong)
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    g.TIEU_DE = "Báo cáo lịch sử thay đổi và sơ đồ luồng xử lý"
    g.DUONG_PDF = DUONG_PDF
    html_ = g.dung_html([("LICH_SU_THAY_DOI.md", md)])
    html_ = html_.replace("<h2>4. Sơ đồ", '<h2 style="page-break-before:always">4. Sơ đồ')
    for dau, svg in (("[[SO_DO_XU_LY]]", DUONG_SVG_XU_LY), ("[[SO_DO_BUOC]]", DUONG_SVG_BUOC)):
        with open(svg, encoding="utf-8") as f:
            ma_svg = re.sub(r"<\?xml[^>]*\?>", "", f.read())
        ma_svg = re.sub(r'(<svg[^>]*?) width="\d+" height="\d+"', r'\1 style="display:block;margin:0 auto;max-width:100%;max-height:245mm;width:auto;height:auto"', ma_svg, count=1)
        html_ = html_.replace("<p>%s</p>" % dau, '<div%s>%s</div>' % (' style="page-break-before:always"' if dau == "[[SO_DO_BUOC]]" else "", ma_svg))
    if g.ghi_pdf(html_):
        return True
    return pdf_bang_node(html_)


def svg_ra_png(svg: str, png: str) -> bool:
    """Chụp SVG thành PNG bằng Playwright của Node (docx không nhúng được SVG)."""
    tam = png + ".html"
    with open(svg, encoding="utf-8") as f:
        ma = re.sub(r"<\?xml[^>]*\?>", "", f.read())
    with open(tam, "w", encoding="utf-8") as f:
        f.write('<html><body style="margin:0">%s</body></html>' % ma)
    kich_ban = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--no-sandbox']});"
                "const p=await b.newPage({viewport:{width:1200,height:900},deviceScaleFactor:1.5});await p.goto('file://'+process.argv[1]);"
                "await p.screenshot({path:process.argv[2],fullPage:true,timeout:120000});await b.close();})();")
    try:
        subprocess.run(["node", "-e", kich_ban, tam, png], check=True, timeout=240, capture_output=True)
        return True
    except (OSError, subprocess.SubprocessError):
        return False
    finally:
        if os.path.exists(tam):
            os.remove(tam)


def ghi_docx(md: str) -> bool:
    """Dùng lại bộ dựng .docx của gói minh chứng, rồi thay hai dòng đánh dấu bằng ảnh sơ đồ."""
    spec = importlib.util.spec_from_file_location("tao_goi_minh_chung", os.path.join(THU_MUC, "tao_goi_minh_chung.py"))
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    g.TIEU_DE = "Báo cáo lịch sử thay đổi và sơ đồ luồng xử lý"
    g.DUONG_DOCX = DUONG_DOCX
    if not g.ghi_docx([("LICH_SU_THAY_DOI.md", md)]):
        return False
    import docx
    from docx.shared import Cm
    tai_lieu = docx.Document(DUONG_DOCX)
    for dau, svg in (("[[SO_DO_XU_LY]]", DUONG_SVG_XU_LY), ("[[SO_DO_BUOC]]", DUONG_SVG_BUOC)):
        png = os.path.join(THU_MUC, "_so_do_tam.png")
        if not svg_ra_png(svg, png):
            print("Không chụp được sơ đồ: .docx giữ dòng đánh dấu")
            continue
        for dv in tai_lieu.paragraphs:
            if dv.text.strip() == dau:
                for r in list(dv.runs):
                    r.text = ""
                dv.add_run().add_picture(png, height=Cm(21) if dau == "[[SO_DO_XU_LY]]" else None,
                                         width=None if dau == "[[SO_DO_XU_LY]]" else Cm(17))
        os.remove(png)
    rong = {5: (2.0, 2.1, 2.2, 5.2, 5.5), 4: (2.0, 2.1, 2.3, 10.6), 3: (3.0, 4.0, 10.0)}
    for b in tai_lieu.tables:
        w = rong.get(len(b.columns))
        if w and len(b.columns) in (4, 5):
            b.autofit = False
            for c, cm in zip(b.columns, w):
                c.width = Cm(cm)
            for hang in b.rows:
                for o, cm in zip(hang.cells, w):
                    o.width = Cm(cm)
    tai_lieu.save(DUONG_DOCX)
    return True


def pdf_bang_node(html_: str) -> bool:
    """Dự phòng khi Python không có playwright: dùng Playwright của Node (cùng Chromium cài sẵn)."""
    tam = os.path.join(THU_MUC, "_lich_su_tam.html")
    with open(tam, "w", encoding="utf-8") as f:
        f.write(html_)
    kich_ban = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--no-sandbox']});"
                "const p=await b.newPage();await p.goto('file://'+process.argv[1]);"
                "await p.pdf({path:process.argv[2],format:'A4',printBackground:true,"
                "margin:{top:'15mm',bottom:'15mm',left:'10mm',right:'10mm'}});await b.close();})();")
    try:
        subprocess.run(["node", "-e", kich_ban, tam, DUONG_PDF], check=True, timeout=240, capture_output=True)
        return True
    except (OSError, subprocess.SubprocessError):
        print("Không in được .pdf bằng Node")
        return False
    finally:
        if os.path.exists(tam):
            os.remove(tam)


def main() -> int:
    tq = tong_quan()
    md = dung_md(tq)
    with open(DUONG_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(md.replace("[[SO_DO_XU_LY]]", "![Sơ đồ luồng xử lý](so_do_xu_ly.svg)").replace("[[SO_DO_BUOC]]", "![Sơ đồ 12 bước](so_do_luong.svg)"))
    ghi_csv(tq)
    ok = ghi_pdf(md)
    ok_docx = ghi_docx(md)
    print("md :", DUONG_MD)
    print("csv:", DUONG_CSV)
    print("pdf:", DUONG_PDF if ok else "không dựng")
    print("docx:", DUONG_DOCX if ok_docx else "không dựng")
    return 0


if __name__ == "__main__":
    sys.exit(main())
