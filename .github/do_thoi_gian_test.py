"""Tổng thời gian (giây) mỗi tệp test từ một hay nhiều báo cáo JUnit của pytest.

Dùng:
    python .github/do_thoi_gian_test.py junit1.xml [junit2.xml ...]
        -> ghi `.github/thoi_gian_test.json` (số đo Linux)
    python .github/do_thoi_gian_test.py --windows junit*.xml
        -> ghi `.github/thoi_gian_test_windows.json` (số đo Windows)
    python .github/do_thoi_gian_test.py --in junit*.xml
        -> chỉ IN ra một dòng JSON (CI dùng: đọc log để cập nhật số đo đúng máy CI)
`chia_test.py` đọc các tệp này để chia các phần CI theo thời gian thật. Không cần thư viện ngoài.
Đầu vào là báo cáo do chính pytest trong repo tạo ra (không phải dữ liệu từ ngoài).
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

GOC = os.path.dirname(os.path.abspath(__file__))


def tong_theo_tep(cac_junit):
    tong = defaultdict(float)
    for duong in cac_junit:
        if not os.path.exists(duong):
            continue
        for tc in ET.parse(duong).getroot().iter("testcase"):
            phan = tc.get("classname", "").split(".")  # vd "tests.test_abc" / "tests.test_abc.TestX"
            if len(phan) < 2 or phan[0] != "tests":
                continue
            tong["tests/" + phan[1] + ".py"] += float(tc.get("time") or 0)
    return {k: round(v, 1) for k, v in sorted(tong.items())}


if __name__ == "__main__":
    co = [a for a in sys.argv[1:] if a.startswith("--")]
    tep = [a for a in sys.argv[1:] if not a.startswith("--")]
    du_lieu = tong_theo_tep(tep)
    if "--in" in co:
        print("THOI_GIAN_TEP_JSON " + json.dumps(du_lieu, ensure_ascii=False, sort_keys=True))
        sys.exit(0)
    ra = os.path.join(GOC, "thoi_gian_test_windows.json" if "--windows" in co else "thoi_gian_test.json")
    with open(ra, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=0, sort_keys=True)
        f.write("\n")
    print(f"{len(du_lieu)} tệp, tổng {sum(du_lieu.values()):.0f} giây -> {ra}")
