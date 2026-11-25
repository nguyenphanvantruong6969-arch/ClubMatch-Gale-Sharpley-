# -*- coding: utf-8 -*-
"""Sinh SO_NHAP_300HS_DOI_CHE_DO.xlsx — DỮ LIỆU MÔ PHỎNG (không phải học sinh thật).
Dùng lại bộ sinh du_lieu_test/tao_so_nhap_doi_che_do.py (một sổ hợp lệ cho mọi chế độ),
nâng lên 300 học sinh và nhân đôi chỉ tiêu CLB Giới hạn / Tuyển chọn để giữ độ chọi.
    python docs/bao_cao_300hs/sinh_300hs.py
"""
import os, sys
GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test")); sys.path.insert(0, GOC)
import tao_so_nhap_doi_che_do as t  # noqa: E402

N = 300
t.N_HOC_SINH = N
t.CLB_MOI_BUOI = {b: [(ten, loai, (N if loai == t.so_nhap.TU_DO else cho * 2), san)
                      for (ten, loai, cho, san) in ds] for b, ds in t.CLB_MOI_BUOI.items()}
t.GHI_CHU[1] = "DỮ LIỆU MÔ PHỎNG (docs/bao_cao_300hs/sinh_300hs.py, seed 20261122). Không phải học sinh thật."
RA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SO_NHAP_300HS_DOI_CHE_DO.xlsx")
if __name__ == "__main__":
    print(t.ghi(RA))
