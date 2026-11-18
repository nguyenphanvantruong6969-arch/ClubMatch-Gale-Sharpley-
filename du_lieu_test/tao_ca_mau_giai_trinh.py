"""I4 (tích hợp GT1+GT2+GT3): sinh `docs/giai_trinh/CA_MAU.md` — các ca mẫu lấy THẲNG từ đầu ra của phần mềm.

Chạy: python du_lieu_test/tao_ca_mau_giai_trinh.py        (ghi đè docs/giai_trinh/CA_MAU.md)
Dữ liệu: bộ TEST_0* (120 học sinh MÔ PHỎNG, 10 CLB), hạt giống 42. Cùng mã + cùng dữ liệu cho ra cùng tệp từng byte.
Tệp chỉ chứa dữ kiện và câu do phần mềm sinh; không có nhận xét hay kết luận (phần đó do học sinh tự viết).
"""

import os
import shutil
import sqlite3
import sys
import tempfile

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (GOC, os.path.join(GOC, "du_lieu_test")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import api as api_mod  # noqa: E402
import cau_hinh_ws  # noqa: E402
import do_anh_huong_seed as d  # noqa: E402
import i18n_errors  # noqa: E402
import workspace as ws  # noqa: E402

DUONG_RA = os.path.join(GOC, "docs", "giai_trinh", "CA_MAU.md")
SEED = 42
BO = d.BO_DU_LIEU[2][1]                                   # TEST_0*: 120 em / 10 CLB
LUAT_THU = {"priority": "score+tier", "tiers": ["chinh_sach"], "tier_mode": "strict"}
LUAT_XUNG_DOT = {"priority": "score+tier", "tiers": ["chinh_sach", "chinh_sach"]}
SO_CA = 3
SO_DONG_DOI = 8


def _so(x):
    return "—" if x is None else x


def _msg(r):
    return " ".join(i18n_errors.format_all(r["errors"], "vi"))


def _dung_workspace(tmp):
    """Workspace mới (đã chạy xếp chính thức, hạt giống SEED). Trả (api, slug)."""
    os.makedirs(os.path.join(tmp, "nguon"))
    nguon = d.nap_bo(os.path.join(tmp, "nguon"), BO)
    goc = os.path.join(tmp, "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Ca mẫu", {})
    db = ws.duong_dan_db(goc, slug)
    shutil.copyfile(nguon, db)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
    a = api_mod.PipelineAPI(db, thu_muc_goc_ws=goc)
    r = a.run_pipeline(seed=SEED)
    assert r["ok"], r
    return a, slug, db


def _ds_hoc_sinh(a):
    with a._ket_noi_doc() as cur:
        return [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")]


def _bang_lua_chon(gt):
    ra = ["| Hạng | CLB | Điểm của em | Đã nhận / Sức chứa | Điểm chuẩn | Được xếp |", "|---|---|---|---|---|---|"]
    for x in gt["cac_lua_chon"]:
        ra.append("| %s | %s | %s | %s / %s | %s | %s |" % (
            x["hang"], x["ten_clb"], x["diem_em"], x["da_nhan"], x["suc_chua"],
            "—" if x["diem_chuan"] is None else x["diem_chuan"],
            "có" if x["duoc_xep"] else "không"))
    return ra


def _ca_hoc_sinh(a, sid, nhan):
    r = a.get_giai_trinh_hoc_sinh(sid)
    assert r["ok"], r
    dl = r["data"]
    ra = ["### %s — %s (%s)" % (nhan, dl["ten"], sid), ""]
    for b in dl["buoi"]:
        ra.append("Kết quả: **%s**" % (b["ten_clb"] or "chưa có chỗ"))
        ra.append("")
        ra += _bang_lua_chon(b)
        ra.append("")
        if b["cau_tom_tat"]:
            ra.append("- (tóm tắt) %s" % b["cau_tom_tat"])
        for x in b["cac_lua_chon"]:
            ra.append("- (hạng %s) %s" % (x["hang"], x["cau"]))
        ra.append("")
    return ra


def _chon_ca(a, ds):
    """3 em được nguyện vọng 1, 3 em không — đầu danh sách theo mã, thứ tự cố định."""
    duoc1, khong = [], []
    for sid in ds:
        b = a.get_giai_trinh_hoc_sinh(sid)["data"]["buoi"][0]
        hang1 = next((x for x in b["cac_lua_chon"] if x["hang"] == 1), None)
        if hang1 is None:
            continue
        (duoc1 if hang1["duoc_xep"] else khong).append(sid)
    return duoc1[:SO_CA], khong[:SO_CA]


def _ca_bi_chan(tmp):
    """Dữ liệu thiếu: một học sinh có nguyện vọng nhưng bị mất khỏi danh sách -> chạy xếp bị chặn."""
    os.makedirs(os.path.join(tmp, "chan"))
    db = d.nap_bo(os.path.join(tmp, "chan"), BO)
    con = sqlite3.connect(db)
    con.execute("DELETE FROM students WHERE student_id = 'HS001'")
    con.commit()
    con.close()
    r = api_mod.PipelineAPI(db).run_pipeline(seed=SEED)
    assert not r["ok"], "chạy xếp lẽ ra phải bị chặn"
    return r


def _bang_so_sanh(s):
    t = s["tong"]
    chi_so = [("Số em", "n"), ("Số em đã có chỗ", "da_xep"), ("Số em chưa có chỗ", "chua_xep"),
              ("Tỉ lệ có chỗ (%)", "pct_da_xep"), ("Tỉ lệ được nguyện vọng 1 (%)", "pct_nv1"),
              ("Tỉ lệ được trong 3 nguyện vọng đầu (%)", "pct_top3"), ("Hạng nguyện vọng trung bình", "hang_tb")]
    ra = ["| Chỉ số | Chính thức (mặc định) | Chạy thử |", "|---|---|---|"]
    for ten, k in chi_so:
        ra.append("| %s | %s | %s |" % (ten, t["b"][k], t["a"][k]))
    return ra


def tao_ca_mau() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        a, slug, _db = _dung_workspace(os.path.join(tmp, "chinh"))
        ds = _ds_hoc_sinh(a)
        duoc1, khong = _chon_ca(a, ds)
        assert len(duoc1) == SO_CA and len(khong) == SO_CA

        ra = ["# Ca mẫu giải trình và tiêu chí", "",
              "> **DỮ LIỆU MÔ PHỎNG.** Tên và điểm do máy sinh (hạt giống cố định). Không phải học sinh hay khảo sát thật.",
              "> Tệp này do `du_lieu_test/tao_ca_mau_giai_trinh.py` sinh từ đầu ra của phần mềm; chạy lại cho ra đúng tệp này.",
              "> Chỉ ghi dữ kiện và câu của phần mềm. Nhận xét, kết luận do học sinh tự viết, không nằm ở đây.", "",
              "Bộ dữ liệu: `du_lieu_test/TEST_01–03` (%d học sinh, 10 CLB, 1 buổi). Hạt giống xếp: %d." % (len(ds), SEED), ""]

        ra += ["## 1. Ba em được nguyện vọng 1", ""]
        for i, sid in enumerate(duoc1, 1):
            ra += _ca_hoc_sinh(a, sid, "Ca %d" % i)
        ra += ["## 2. Ba em không được nguyện vọng 1", ""]
        for i, sid in enumerate(khong, 1):
            ra += _ca_hoc_sinh(a, sid, "Ca %d" % (i + SO_CA))

        ra += ["## 3. Chạy xếp bị chặn vì thiếu dữ liệu", "",
               "Cách tạo: xoá học sinh `HS001` khỏi danh sách, giữ nguyên nguyện vọng của em.", "",
               "Thông báo của phần mềm:", ""]
        ra += ["- %s" % x for x in i18n_errors.format_all(_ca_bi_chan(tmp)["errors"], "vi")]
        ra.append("")

        ra += ["## 4. Tiêu chí mâu thuẫn bị từ chối khi lưu", "",
               "Cách tạo: lưu luật xếp có tên nhóm ưu tiên `chinh_sach` hai lần.", "",
               "Thông báo của phần mềm:", ""]
        r = a.update_workspace_config({"rules": LUAT_XUNG_DOT}, slug)
        assert not r["ok"], r
        ra += ["- %s" % _msg(r), ""]

        ra += ["## 5. So sánh tiêu chí mặc định với một tiêu chí thử", ""]
        thu = a.run_thu(LUAT_THU)
        assert thu["ok"], thu
        s = a.so_sanh_lan_chay(thu["data"]["run_id"])
        assert s["ok"], s
        s = s["data"]
        ra += ["Tiêu chí chính thức (bằng lời, theo phần mềm):", ""]
        ra += ["- %s" % x["chu"] for x in s["b"]["mo_ta"]]
        ra += ["", "Tiêu chí chạy thử (bằng lời, theo phần mềm):", ""]
        ra += ["- %s" % x["chu"] for x in s["a"]["mo_ta"]]
        ra += ["", "Kết quả chạy thử không ghi đè kết quả chính thức.", ""]
        ra += _bang_so_sanh(s)
        ra += ["", "Số em đổi chỗ: **%d**." % s["so_doi"], "", "### Theo nhóm", "",
               "| Nhóm | Số em | Có chỗ (chính thức → thử) | Nguyện vọng 1 % (chính thức → thử) |", "|---|---|---|---|"]
        for g in s["nhom"]:
            ra.append("| %s | %s | %s → %s | %s → %s |" % (
                g["khoa"] or "(không thuộc nhóm nào)", g["b"]["n"], g["b"]["da_xep"], g["a"]["da_xep"],
                g["b"]["pct_nv1"], g["a"]["pct_nv1"]))
        ra += ["", "### Theo CLB", "", "| CLB | Sức chứa | Đã nhận (chính thức → thử) | Điểm chuẩn (chính thức → thử) |",
               "|---|---|---|---|"]
        for c in s["clb"]:
            ra.append("| %s | %s | %s → %s | %s → %s |" % (
                c["ten"], c["suc_chua"], c["b"]["da_nhan"], c["a"]["da_nhan"], _so(c["b"]["diem_chuan"]), _so(c["a"]["diem_chuan"])))
        ra += ["", "### %d em đổi chỗ đầu danh sách (theo mã)" % min(SO_DONG_DOI, s["so_doi"]), "",
               "| Mã | Tên | Chính thức | Chạy thử |", "|---|---|---|---|"]
        for x in sorted(s["doi"], key=lambda z: z["student_id"])[:SO_DONG_DOI]:
            ra.append("| %s | %s | %s | %s |" % (x["student_id"], x["ten"], x["den_ten"] or "chưa có chỗ", x["tu_ten"] or "chưa có chỗ"))
        ra.append("")
    return "\n".join(ra).rstrip("\n") + "\n"


def main():
    van_ban = tao_ca_mau()
    with open(DUONG_RA, "w", encoding="utf-8", newline="\n") as f:
        f.write(van_ban)
    print("Đã ghi %s (%d dòng)" % (DUONG_RA, van_ban.count("\n")))


if __name__ == "__main__":
    main()
