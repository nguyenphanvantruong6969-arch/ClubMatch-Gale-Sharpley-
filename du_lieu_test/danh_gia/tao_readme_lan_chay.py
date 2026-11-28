# -*- coding: utf-8 -*-
"""Ghi `ket_qua/README_LAN_CHAY.md` từ trường `lan_chay` của từng JSON (commit, lệnh, thời gian). Không số gõ tay.

    python du_lieu_test/danh_gia/tao_readme_lan_chay.py [THƯ_MỤC] [--ghi-chu "văn bản"]
"""
import json
import os
import sys

THU_MUC = os.path.dirname(os.path.abspath(__file__))


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    ghi_chu = ""
    if "--ghi-chu" in a:
        i = a.index("--ghi-chu")
        ghi_chu = a[i + 1]
        a = a[:i] + a[i + 2:]
    thu_muc = a[0] if a else os.path.join(THU_MUC, "ket_qua")
    dong = []
    for ten in sorted(os.listdir(thu_muc)):
        if not ten.endswith(".json"):
            continue
        with open(os.path.join(thu_muc, ten), encoding="utf-8") as f:
            d = json.load(f)
        lc = d.get("lan_chay") or {}
        cfg = (d.get("dinh_nghia") or {}).get("cau_hinh_chay") or {}
        dong.append("| `%s` | `%s` | `%s` | %s | %s | %s |" % (
            ten, (lc.get("commit") or "?")[:10], lc.get("lenh"), lc.get("thoi_gian_giay"), lc.get("bat_dau"),
            "%s trường × %s lần bốc thăm" % (len((d.get("dinh_nghia") or {}).get("seed_du_lieu") or []),
                                              len((d.get("dinh_nghia") or {}).get("seed_boc_tham") or []))
            if cfg.get("che_do") else ""))
    ra = ["# Lần chạy đầy đủ DG1 — nguồn gốc các JSON", "",
          "> **TOÀN BỘ SỐ ĐO TRÊN DỮ LIỆU MÔ PHỎNG** (bộ sinh `_sinh.py`, `mo_phong_fa_daa.py`, và các bộ mẫu trong `du_lieu_test/`), không phải khảo sát học sinh thật.",
          "> Tệp này do `tao_readme_lan_chay.py` sinh từ trường `lan_chay` trong từng JSON.", "",
          "| Tệp | Commit | Lệnh | Giây | Bắt đầu | Lưới |", "|---|---|---|---|---|---|"] + dong
    if ghi_chu:
        ra += ["", ghi_chu]
    ra += ["", "Python / máy: " + "; ".join(sorted({"%s — %s" % ((json.load(open(os.path.join(thu_muc, t), encoding='utf-8')).get('lan_chay') or {}).get('python'),
                                                                 (json.load(open(os.path.join(thu_muc, t), encoding='utf-8')).get('lan_chay') or {}).get('may'))
                                                   for t in os.listdir(thu_muc) if t.endswith('.json')})), ""]
    with open(os.path.join(thu_muc, "README_LAN_CHAY.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(ra))
    print("ghi README_LAN_CHAY.md")


if __name__ == "__main__":
    main()
