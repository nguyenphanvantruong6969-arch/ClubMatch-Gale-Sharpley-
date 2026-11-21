"""In các tệp test (trong danh sách tham số) có test hỏng ở lần chạy trước (.pytest_cache lastfailed).

Dùng trong tests.yml: chỉ chạy lại `--lf` khi phần này thật sự có test hỏng cũ. Không cần thư viện ngoài.
"""
import json
import os
import sys

DUONG = os.path.join(".pytest_cache", "v", "cache", "lastfailed")


def tep_hong(tep_cua_phan):
    if not os.path.exists(DUONG):
        return []
    with open(DUONG, encoding="utf-8") as f:
        hong = json.load(f)
    tap = {t.replace("\\", "/") for t in tep_cua_phan}
    return sorted({k.split("::")[0] for k in hong if k.split("::")[0] in tap})


if __name__ == "__main__":
    print(" ".join(tep_hong(sys.argv[1:])))
