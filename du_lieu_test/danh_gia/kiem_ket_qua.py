# -*- coding: utf-8 -*-
"""Kiểm các ràng buộc CỨNG trên toàn bộ JSON của `ket_qua/` (thoát 1 nếu vi phạm):

  1. mọi ô `a.cap_chan` / `a.ngoai_danh_sach` của RB-DA = 0 (cơ chế Boston, thứ tự bốc thăm, TTC được phép khác 0);
  2. `doi_chieu_so_lieu.dat` = true (bộ TEST, seed 42: 108/120, NV1 64, khớp từng dòng `match_results`);
  3. ở mọi cấu hình quét: số em được xếp ≤ cận trên ghép cực đại (`b.gia_uu_tien_on_dinh` ≥ 0 ở từng trường);
  4. biến thể `max_choices = 10` trùng mặc định; số em đổi CLB khớp `tieu_chi.so_sanh_lan_chay`.

    python du_lieu_test/danh_gia/kiem_ket_qua.py [THƯ_MỤC]
"""
import glob
import json
import os
import sys

THU_MUC = os.path.dirname(os.path.abspath(__file__))
CO_CHE_KHONG_ON_DINH = ("boston", "thu_tu_boc_tham", "ttc")


def _quet(node, duong, ra, ten):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("a.cap_chan", "a.ngoai_danh_sach") and isinstance(v, dict):
                ra["so_o"] += 1
                gt = [v.get("tb")] + (v.get("theo_bo") or []) + (v.get("ktc95") or [])
                if any(x not in (0, 0.0, None) for x in gt) and not any(m in duong for m in CO_CHE_KHONG_ON_DINH):
                    ra["loi"].append("%s %s %s tb=%s" % (ten, duong, k, v.get("tb")))
            elif k == "cap_chan" and isinstance(v, int) and v != 0:
                ra["loi"].append("%s %s cap_chan=%s" % (ten, duong, v))
            else:
                _quet(v, duong + "/" + k, ra, ten)
    elif isinstance(node, list):
        for i, x in enumerate(node):
            _quet(x, duong + "[%d]" % i, ra, ten)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    thu_muc = a[0] if a else os.path.join(THU_MUC, "ket_qua")
    ra = {"so_o": 0, "loi": []}
    cac = {}
    for f in sorted(glob.glob(os.path.join(thu_muc, "*.json"))):
        with open(f, encoding="utf-8") as h:
            cac[os.path.basename(f)] = json.load(h)
        _quet(cac[os.path.basename(f)], "", ra, os.path.basename(f))
    dc = cac.get("doi_chieu_so_lieu.json")
    if dc is None or not dc.get("dat"):
        ra["loi"].append("doi_chieu_so_lieu: thiếu hoặc KHÔNG đạt")
    q = cac.get("quet_quy_mo.json")
    if q:
        for c in q["cac_cau_hinh"]:
            g = c["chi_so"]["b.gia_uu_tien_on_dinh"]["theo_bo"]
            if min(g) < 0:
                ra["loi"].append("quet %s: được xếp > cận trên (%s)" % (c["tham_so"], min(g)))
    b = cac.get("bien_the_tieu_chi.json")
    if b:
        if not b["max_choices_10_trung_mac_dinh"]:
            ra["loi"].append("max_choices=10 KHÔNG trùng mặc định")
        for x in b["doi_chieu_so_sanh_lan_chay"]:
            if x["so_doi_tieu_chi"] != x["doi_clb_do_dg1"]:
                ra["loi"].append("churn lệch so_sanh_lan_chay: %s" % x)
    print("đã kiểm %d ô cap_chan/ngoai_danh_sach trong %d tệp; vi phạm: %d" % (ra["so_o"], len(cac), len(ra["loi"])))
    for x in ra["loi"]:
        print("  ✗", x)
    return 1 if ra["loi"] else 0


if __name__ == "__main__":
    sys.exit(main())
