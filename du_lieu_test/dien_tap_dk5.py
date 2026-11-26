"""DK5: diễn tập toàn trình đăng ký -> xếp. DỮ LIỆU MÔ PHỎNG (MÔ PHỎNG), không phải khảo sát thật.

Chỉ đi qua API DK3/DK4 (`{ok, data, errors}`); không ghi SQLite trực tiếp. Bộ sinh tất định: cùng `seed` -> cùng JSON
(`random.Random(seed)`, không dùng `hash()`; sắp xếp mọi tập trước khi lấy mẫu).
"""
import json
import random
import time

NHAN = "MÔ PHỎNG"
BUOI = ["T2", "T3"]
KHOI = [6, 12]
SO_PHONG_MOI_BUOI_TOI_DA = 40
MAT_KHAU = "dientap-qt"
MA_TRUONG = "DIENTAP"


def dung_du_lieu(seed=20261126, so_hs=798, so_clb=40, so_buoi=2):
    """Bộ dữ liệu mô phỏng thuần (dict JSON được). Mỗi buổi: ~70% Tự do, ~20% Giới hạn, còn lại Tuyển chọn."""
    rng = random.Random(seed)
    buoi = ["T%d" % (2 + i) for i in range(so_buoi)]
    moi_buoi = so_clb // so_buoi
    so_gv = moi_buoi                                  # mỗi giáo viên 1 CLB mỗi buổi (D14)
    gv = ["Giáo viên %02d (mô phỏng)" % (i + 1) for i in range(so_gv)]
    phong = [{"ten": "Phòng %02d" % (i + 1), "suc_chua": 60} for i in range(moi_buoi)]
    clb = []
    for b_i, b in enumerate(buoi):
        for i in range(moi_buoi):
            loai = "Tự do" if i < int(moi_buoi * 0.7) else ("Giới hạn" if i < int(moi_buoi * 0.9) else "Tuyển chọn")
            d = {"ten": "CLB %s-%02d" % (b, i + 1), "buoi": b, "loai": loai, "gv": (i + b_i) % so_gv, "phong": i,
                 "khoi_tu": 6, "khoi_den": 12}
            if loai == "Giới hạn":
                d["chi_tieu"] = 40
            elif loai == "Tuyển chọn":
                d.update(chi_tieu=25, diem_san=5, khoi_tu=8)
            clb.append(d)
    hs = []
    so_lop = max(1, so_hs // 28)
    for i in range(so_hs):
        khoi = KHOI[0] + i % (KHOI[1] - KHOI[0] + 1)
        lop = "%dA%d" % (khoi, 1 + (i // 7) % max(1, so_lop // 7))
        hs.append({"ma": "S%04d" % (i + 1), "ten": "HS %04d (mô phỏng)" % (i + 1), "lop": lop, "khoi": khoi})
    nguyen_vong = {}
    diem = {}
    for h in hs:
        ds = []
        for b in buoi:
            hop_le = sorted((c for c in clb if c["buoi"] == b and c["khoi_tu"] <= h["khoi"] <= c["khoi_den"]), key=lambda c: c["ten"])
            td = [c for c in hop_le if c["loai"] == "Tự do"]
            khac = [c for c in hop_le if c["loai"] != "Tự do"]
            chon = rng.sample(khac, min(len(khac), rng.randint(2, 4))) + rng.sample(td, min(len(td), rng.randint(2, 3)))
            rng.shuffle(chon)
            da_thi = 0
            for c in chon:
                thi = c["loai"] == "Tuyển chọn" and da_thi < 2
                da_thi += thi
                ds.append({"clb": c["ten"], "thi": thi})
                if thi:
                    diem[(h["ma"], c["ten"])] = round(rng.uniform(3, 10), 1)
        nguyen_vong[h["ma"]] = ds
    return {"nhan": NHAN, "seed": seed, "buoi": buoi, "gv": gv, "phong": phong, "clb": clb, "hs": hs,
            "nguyen_vong": nguyen_vong, "diem": [[m, c, d] for (m, c), d in sorted(diem.items())]}


def json_bytes(du_lieu):
    return json.dumps(du_lieu, ensure_ascii=False, sort_keys=True).encode("utf-8")


def ok(r):
    assert r["ok"] and r["errors"] == [], r
    return r["data"]


class Dong_ho:
    def __init__(self):
        self.pha = {}

    def do(self, ten):
        dong_ho = self

        class _C:
            def __enter__(self):
                self.t = time.perf_counter()

            def __exit__(self, *a):
                dong_ho.pha[ten] = round(time.perf_counter() - self.t, 3)
        return _C()


def chay(api, du_lieu, so_kiosk=4, seed_xep=7, tu_dang_ky_gv=0.5, dong_ho=None, dung_den="xep"):
    """Chạy toàn trình qua API (`dung_den="nhap_diem"`: dừng ngay sau khi nhập điểm, chưa «Chốt và xếp»). Trả `{pha, ids, token_qt, so_hs, so_kiosk, thu_tu_nop, ...}`; mọi lời gọi phải `ok` và rỗng lỗi."""
    dh = dong_ho or Dong_ho()
    kq = {"nhan": NHAN}
    with dh.do("cai_dat"):
        ok(api.dk_khoi_tao(MAT_KHAU, MA_TRUONG, du_lieu["buoi"], KHOI))
        qt = ok(api.dk_dang_nhap("quan_tri", "", MAT_KHAU))["token"]
        for p in du_lieu["phong"]:
            ok(api.dk_phong_luu(qt, p["ten"], p["suc_chua"]))
        # Không dùng `phong_id` do `dk_phong_luu` trả (lỗi sản phẩm: lấy lastrowid sau dòng nhật ký -> id lệch 1); đọc lại từ danh sách.
        theo_ten = {r["ten"]: r["phong_id"] for r in ok(api.dk_phong_danh_sach(qt))}
        phong_id = [theo_ten[p["ten"]] for p in du_lieu["phong"]]
        ok(api.dk_hs_nap_danh_sach(qt, "\n".join("%s\t%s\t%s" % (h["ma"], h["ten"], h["lop"]) for h in du_lieu["hs"])))
        ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    with dh.do("giao_vien"):
        n_tu = int(len(du_lieu["gv"]) * tu_dang_ky_gv)
        tok_gv = {}
        for i, ten in enumerate(du_lieu["gv"]):
            if i < n_tu:
                pin = "%04d" % (1000 + i)
                ok(api.dk_gv_tu_dang_ky(MA_TRUONG, ten, pin))
            else:
                pin = None
            tok_gv[i] = (ten, pin)
        moi = [t for i, (t, p) in tok_gv.items() if p is None]
        if moi:
            for x in ok(api.dk_gv_tao_hang_loat(qt, "\n".join(moi)))["da_tao"]:
                for i, (t, p) in list(tok_gv.items()):
                    if t == x["ten"]:
                        tok_gv[i] = (t, x["pin"])
        tk = {i: ok(api.dk_dang_nhap("giao_vien", t, p))["token"] for i, (t, p) in tok_gv.items()}
        ids = {}
        for c in du_lieu["clb"]:
            d = {"ten": c["ten"], "buoi": c["buoi"], "loai": c["loai"], "phong_id": phong_id[c["phong"]],
                 "chi_tieu": c.get("chi_tieu"), "khoi_tu": c["khoi_tu"], "khoi_den": c["khoi_den"], "diem_san": c.get("diem_san")}
            ids[c["ten"]] = ok(api.dk_clb_luu(tk[c["gv"]], d))["clb_id"]
        ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    with dh.do("duyet"):
        qt = ok(api.dk_dang_nhap("quan_tri", "", MAT_KHAU))["token"]       # phiên mới: máy chậm có thể làm phiên cũ hết giờ nghỉ
        for cid in ids.values():
            ok(api.dk_clb_duyet(qt, cid, "duyet"))
        ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    with dh.do("hoc_sinh_nop"):
        qt = ok(api.dk_dang_nhap("quan_tri", "", MAT_KHAU))["token"]       # phiên mới: máy chậm có thể làm phiên cũ hết giờ nghỉ
        pins = {}
        for h in du_lieu["hs"]:
            pins[h["ma"]] = ok(api.dk_hs_dat_lai_pin(qt, h["ma"]))["pin"]
        thu_tu = []
        hang_doi = list(du_lieu["hs"])
        kiosk = [None] * so_kiosk                         # mỗi máy giữ một em đang đăng nhập
        while hang_doi or any(k is not None for k in kiosk):
            for k in range(so_kiosk):                     # vòng tròn: nộp em đang giữ rồi nạp em kế tiếp
                if kiosk[k] is not None:
                    ma, token = kiosk[k]
                    nv = [{"clb_id": ids[x["clb"]], "thi": x["thi"]} for x in du_lieu["nguyen_vong"][ma]]
                    ok(api.dk_hs_luu(token, nv))
                    ok(api.dk_dang_xuat(token))
                    thu_tu.append((k, ma))
                    kiosk[k] = None
                if hang_doi:
                    h = hang_doi.pop(0)
                    kiosk[k] = (h["ma"], ok(api.dk_dang_nhap("hoc_sinh", h["ma"], pins[h["ma"]]))["token"])
        kq["thu_tu_nop"] = thu_tu
    with dh.do("nhap_diem"):
        # Máy chậm (CI Windows): pha học sinh nộp có thể dài hơn 120 s nên phiên quản trị đã bị khoá vì nghỉ (đúng thiết kế).
        qt = ok(api.dk_dang_nhap("quan_tri", "", MAT_KHAU))["token"]
        ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
        theo_clb = {}
        for m, c, d in du_lieu["diem"]:
            theo_clb.setdefault(c, []).append("%s\t%s" % (m, d))
        for c, dong in theo_clb.items():
            r = ok(api.dk_diem_dan(qt, ids[c], "\n".join(dong)))
            assert r["loi"] == [], r
        assert ok(api.dk_diem_thieu(qt)) == []
    if dung_den != "xep":
        kq["xep"] = None
    else:
        with dh.do("chot_va_xep"):
            kq["xep"] = ok(api.dk_chot_va_xep(qt, seed_xep))
    kq.update(pha=dh.pha, ids=ids, token_qt=qt, so_hs=len(du_lieu["hs"]), so_kiosk=so_kiosk, pin_hs=pins)
    return kq


def xuat(api, qt, duong_dan):
    return ok(api.dk_xuat_so_nhap(qt, duong_dan))
