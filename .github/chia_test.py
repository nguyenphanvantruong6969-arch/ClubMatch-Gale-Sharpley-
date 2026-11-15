"""Chia các tệp tests/test_*.py thành N phần cân bằng (theo kích thước tệp) để CI chạy song song.

Dùng: python .github/chia_test.py <phan> <so_phan>   (phan tính từ 1) -> in danh sách tệp, cách nhau dấu cách.
Chia tất định: cùng bộ tệp luôn ra cùng cách chia. Không cần thư viện ngoài.
"""
import glob
import os
import sys


def chia(so_phan):
    tep = sorted(glob.glob(os.path.join("tests", "test_*.py")))
    # Tệp giao diện (Chromium) chạy chậm hơn hẳn: nhân trọng số để cân bằng thời gian.
    def nang(t):
        return os.path.getsize(t) * (4 if "giao_dien" in os.path.basename(t) else 1)
    phan = [[] for _ in range(so_phan)]
    tong = [0] * so_phan
    for t in sorted(tep, key=lambda t: (-nang(t), t)):
        i = tong.index(min(tong))
        phan[i].append(t)
        tong[i] += nang(t)
    return [sorted(p) for p in phan]


if __name__ == "__main__":
    k, n = int(sys.argv[1]), int(sys.argv[2])
    print(" ".join(chia(n)[k - 1]))
