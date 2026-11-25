"""DK2-L1/L3: JSON bản mẫu cổng đăng ký -> Sổ nhập -> phần mềm nhập 0 lỗi (chế độ huy chương). Dữ liệu MÔ PHỎNG."""
import base64
import json
import random
import sqlite3

import openpyxl
import pytest

import cau_hinh_ws as ch
import dk2_so_nhap as dk
import so_nhap

BUOI = ["Thứ 2", "Thứ 4"]
LOAI = ["Tự do", "Giới hạn", "Tuyển chọn"]


def ban_mau(n_hs=30, n_clb=10, seed=1):
    """Dữ liệu giống nút 'Chép dữ liệu xuất' của bản mẫu (dinhDang 1), sinh tất định."""
    r = random.Random(seed)
    clb = []
    for i in range(n_clb):
        loai = LOAI[0] if i < len(BUOI) else LOAI[i % 3]
        c = {"ma": "c%d" % (i + 1), "ten": "CLB %d" % (i + 1), "buoi": BUOI[i % len(BUOI)], "loai": loai,
             "chiTieu": None if loai == "Tự do" else r.randint(2, 6), "diemSan": None,
             "phong": "P%d" % (i + 1), "sucChuaPhong": 40}
        if loai == "Tuyển chọn":
            c["diemSan"] = r.choice([4, 5, 6])
        clb.append(c)
    hs = []
    for k in range(n_hs):
        nv = []
        for b in BUOI:
            o = [c for c in clb if c["buoi"] == b]
            r.shuffle(o)
            chon = o[:r.randint(1, min(len(o), 4))]
            hc = iter(["Vàng", "Bạc", "Đồng"])
            for c in chon:
                thi = c["loai"] == "Tuyển chọn"
                diem = r.choice([None, r.randint(0, 10), "%d,5" % r.randint(0, 9)]) if thi else None
                nv.append({"clb": c["ma"], "thi": thi, "diem": diem,
                           "huyChuong": None if c["loai"] == "Tự do" else next(hc, None)})
        r.shuffle(nv)          # đảo buổi: converter phải xếp lại thành một dãy theo buổi
        hs.append({"ma": "HS%04d" % (k + 1), "hoTen": "Em %d" % k, "lop": "1%dA%d" % (k % 3, k % 4 + 1), "nv": nv})
    return {"dinhDang": 1, "duLieu": "MÔ PHỎNG", "buoi": BUOI, "clb": clb, "hocSinh": hs}


def _nhap(api, p):
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "wharton": True}})
    with open(p, "rb") as f:
        return api.import_so_nhap(base64.b64encode(f.read()).decode("ascii"))


@pytest.mark.parametrize("n_hs,n_clb", [(30, 10), (798, 40)])
def test_nhap_0_loi_va_xep_dung_diem_san(api, tmp_path, n_hs, n_clb):
    d = ban_mau(n_hs, n_clb)
    p = str(tmp_path / "so.xlsx")
    kq = dk.ghi_tu_ban_mau(d, p)
    assert kq["so_clb"] == n_clb and kq["so_hs"] == n_hs and kq["so_nv_bo"] > 0
    ra = _nhap(api, p)
    assert ra["ok"] and ra["errors"] == [], ra
    con = sqlite3.connect(api.db_path)
    assert con.execute("select count(*) from clubs").fetchone()[0] == n_clb
    assert con.execute("select count(*) from students").fetchone()[0] == n_hs
    assert api.run_pipeline(seed=7)["ok"]
    san = {c["ma"]: c["diemSan"] for c in d["clb"] if c["loai"] == "Tuyển chọn"}
    diem = {(h["ma"], x["clb"]): x["diem"] for h in d["hocSinh"] for x in h["nv"]}
    nhan = con.execute("select student_id, club_id from match_results where club_id is not null").fetchall()
    con.close()
    assert nhan
    for sid, cid in nhan:
        if cid in san:
            assert so_nhap.doc_diem(diem[(sid, cid)]) >= san[cid], (sid, cid)


def test_mot_day_nv_theo_buoi_huy_chuong_va_cot(tmp_path):
    d = ban_mau()
    p = str(tmp_path / "so.xlsx")
    dk.ghi_tu_ban_mau(d, p)
    wb = openpyxl.load_workbook(p)
    clb = [c.value for c in wb["1. CLB"][1]]
    for cot in ("Tên CLB", "Buổi", "Chỉ tiêu", "Mã CLB", "Loại", "Điểm sàn", "Sức chứa phòng", "Địa điểm"):
        assert cot in clb
    assert "Lớp" in [c.value for c in wb["2. Học sinh"][1]]
    assert "Huy chương (60/30/10)" in [c.value for c in wb["2. Học sinh"][2]]
    doc = so_nhap.doc_so_nhap(openpyxl.load_workbook(p))
    assert not doc["loi"]
    buoi = {c["ma"]: c["buoi"] for c in d["clb"]}
    loai = {c["ma"]: c["loai"] for c in d["clb"]}
    goc = {h["ma"]: h for h in d["hocSinh"]}
    for s in doc["students"]:
        thu_tu = [BUOI.index(buoi[x["club_id"]]) for x in s["nv"]]
        assert thu_tu == sorted(thu_tu)                       # NV1…NVk liền một dãy, không bắt đầu lại
        trong_buoi = [x["clb"] for b in BUOI for x in goc[s["student_id"]]["nv"] if buoi[x["clb"]] == b
                      and not (loai[x["clb"]] == "Tuyển chọn" and x["diem"] is None)]
        assert [x["club_id"] for x in s["nv"]] == trong_buoi  # trong buổi giữ thứ tự em xếp
        assert s["class_id"] == goc[s["student_id"]]["lop"]
        for x in s["nv"]:
            assert x["diem_w"] in ("", "60", "30", "10")
            if loai[x["club_id"]] == "Tự do":
                assert x["diem_w"] == ""
            if not x["thi"]:
                assert x["diem"] == ""


def test_tu_ban_mau_chuyen_dung_kieu():
    clubs, hs = dk.tu_ban_mau(ban_mau(5, 6))
    c = {x["club_id"]: x for x in clubs}
    assert c["c1"]["loai"] == so_nhap.TU_DO and c["c1"]["capacity"] == 40      # Tự do: chỉ tiêu = sức chứa phòng
    assert c["c1"]["buoi"] == "thu_2" and c["c1"]["dia_diem"] == "P1" and c["c1"]["suc_chua_phong"] == 40
    tc = [x for x in clubs if x["loai"] == so_nhap.TUYEN_CHON]
    assert tc and all(x["diem_san"] is not None for x in tc)
    d = ban_mau(1, 6)
    d["hocSinh"][0]["nv"] = [{"clb": tc[0]["club_id"], "thi": True, "diem": "8,5", "huyChuong": "Bạc"}]
    _, hs = dk.tu_ban_mau(d)
    assert hs[0]["nv"] == [{"club_id": tc[0]["club_id"], "thi": True, "diem": 8.5, "diem_w": 30}]
    d["hocSinh"][0]["nv"] = [{"clb": tc[0]["club_id"], "thi": False}, {"clb": "c1"},
                             {"clb": tc[0]["club_id"] if len(tc) < 2 else tc[1]["club_id"], "thi": True, "diem": None}]
    bo = []
    _, hs = dk.tu_ban_mau(d, bo)
    assert [x["club_id"] for x in hs[0]["nv"]] == ["c1"] and len(bo) == 2   # không thi / không điểm: bỏ


def _sua(sua):
    d = ban_mau(3, 6)
    sua(d)
    return d


def _sai(sua):
    d = _sua(sua)
    with pytest.raises(dk.LoiBanMau) as e:
        dk.tu_ban_mau(d)
    return " ".join(e.value.loi)


def test_du_lieu_sai_bao_ro_va_khong_ghi_tep(tmp_path):
    assert "dinhDang" in _sai(lambda d: d.update(dinhDang=2))
    assert "Không có CLB" in _sai(lambda d: d.update(clb=[]))
    assert "không có trong danh sách" in _sai(lambda d: d["hocSinh"][0]["nv"].append({"clb": "zz"}))
    assert "hai lần" in _sai(lambda d: d["hocSinh"][0]["nv"].append(dict(d["hocSinh"][0]["nv"][0])))
    assert "loại phải là" in _sai(lambda d: d["clb"][3].update(loai="Lạ"))
    assert "chỉ tiêu" in _sai(lambda d: d["clb"][4].update(chiTieu=0))
    assert "sức chứa" in _sai(lambda d: d["clb"][3].update(sucChuaPhong=-1))
    assert "trùng" in _sai(lambda d: d["clb"][3].update(ma="c1"))
    assert "thiếu mã" in _sai(lambda d: d["clb"][3].update(ten=""))
    assert "không phải một bản ghi" in _sai(lambda d: d["clb"].append(1))
    assert "không phải một bản ghi" in _sai(lambda d: d["hocSinh"].append(1))
    assert "mã bị trùng" in _sai(lambda d: d["hocSinh"].append(dict(d["hocSinh"][0])))

    def tc(d):
        return next(c for c in d["clb"] if c["loai"] == "Tuyển chọn")

    assert "điểm sàn" in _sai(lambda d: tc(d).update(diemSan=11))
    assert "điểm sàn" in _sai(lambda d: tc(d).update(diemSan="abc"))
    assert "số nguyên" in _sai(lambda d: tc(d).update(diemSan=5.5))
    assert dk.tu_ban_mau(_sua(lambda d: tc(d).update(diemSan=6.0)))
    nv = [{"clb": "c1", "huyChuong": "Vàng"}]
    assert "không nhận huy chương" in _sai(lambda d: d["hocSinh"][0].update(nv=nv))

    def hai_vang(d):
        g = [c["ma"] for c in d["clb"] if c["buoi"] == "Thứ 2" and c["loai"] != "Tự do"][:2]
        d["hocSinh"][0]["nv"] = [{"clb": x, "huyChuong": "Vàng"} for x in g]
    assert "hai lần trong một buổi" in _sai(hai_vang)
    assert "không hợp lệ" in _sai(lambda d: d["hocSinh"][0].update(nv=[{"clb": tc(d)["ma"], "huyChuong": "Kim"}]))
    assert "phải từ 0 đến 10" in _sai(lambda d: d["hocSinh"][0].update(
        nv=[{"clb": tc(d)["ma"], "thi": True, "diem": "-1"}]))
    assert "phải từ 0 đến 10" in _sai(lambda d: d["hocSinh"][0].update(
        nv=[{"clb": tc(d)["ma"], "thi": True, "diem": True}]))

    def qua_tran(d):
        d["clb"] += [{"ma": "x%d" % i, "ten": "X%d" % i, "buoi": "Thứ 2", "loai": "Tuyển chọn", "chiTieu": 2,
                      "diemSan": 1} for i in range(6)]
        d["hocSinh"][0]["nv"] = [{"clb": "x%d" % i, "thi": True, "diem": 5} for i in range(6)]
    assert "quá" in _sai(qua_tran)
    p = tmp_path / "khong.xlsx"
    with pytest.raises(dk.LoiBanMau):
        dk.ghi_tu_ban_mau({"dinhDang": 1, "clb": [{"ma": "a"}]}, str(p))
    assert not p.exists()


def test_cli(tmp_path, capsys):
    vao, ra = tmp_path / "vao.json", tmp_path / "ra.xlsx"
    vao.write_text(json.dumps(ban_mau(4, 6), ensure_ascii=False), encoding="utf-8")
    assert dk.main([str(vao), str(ra)]) == 0 and ra.exists()
    assert "Đã ghi" in capsys.readouterr().out
    vao.write_text('{"dinhDang": 9}', encoding="utf-8")
    assert dk.main([str(vao), str(tmp_path / "b.xlsx")]) == 1
    assert "Chưa ghi sổ" in capsys.readouterr().err
    assert dk.main([str(tmp_path / "khong_co.json"), str(ra)]) == 1
    assert "Không đọc được" in capsys.readouterr().err
