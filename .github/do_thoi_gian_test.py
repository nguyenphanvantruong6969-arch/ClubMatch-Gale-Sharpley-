"""Ghi `.github/thoi_gian_test.json` (giây mỗi tệp test) từ một báo cáo JUnit của pytest.

Dùng (khi bộ test thay đổi nhiều và các phần CI lệch nhau):
    python -m pytest -q --junitxml=junit.xml tests/
    python .github/do_thoi_gian_test.py junit.xml
`chia_test.py` đọc tệp này để chia các phần CI theo thời gian thật. Không cần thư viện ngoài.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

RA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thoi_gian_test.json")


def tong_theo_tep(duong_junit):
    tong = defaultdict(float)
    for tc in ET.parse(duong_junit).getroot().iter("testcase"):
        lop = tc.get("classname", "")  # vd "tests.test_abc" hoặc "tests.test_abc.TestX"
        phan = lop.split(".")
        if len(phan) < 2 or phan[0] != "tests":
            continue
        tep = "tests/" + phan[1] + ".py"
        tong[tep] += float(tc.get("time") or 0)
    return {k: round(v, 1) for k, v in sorted(tong.items())}


if __name__ == "__main__":
    du_lieu = tong_theo_tep(sys.argv[1])
    with open(RA, "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, ensure_ascii=False, indent=0, sort_keys=True)
        f.write("\n")
    print(f"{len(du_lieu)} tệp, tổng {sum(du_lieu.values()):.0f} giây -> {RA}")
