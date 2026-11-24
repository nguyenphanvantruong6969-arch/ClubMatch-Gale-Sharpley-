# Prompt tiep tuc SF-A (Sonnet, coder A)

Branch: claude/happy-cerf-xvn495-st-a

Doc CLAUDE.md, roi `docs/phien/claude__happy-cerf-xvn495-st-a.md` (handoff) va `docs/phien/SF_GIAO_THUC.md`. Tra loi Truong bang tieng Viet.

Viec con lai, theo thu tu:
1. `git fetch`, merge origin/claude/happy-cerf-xvn495-st-b neu co commit moi; doc handoff cua B, tra loi Ask moi (neu co).
2. SF-A5 = ST-A-008, Truong da chon phuong an (a): chia PDF phieu toan truong theo lop (tai dung `theo_lop` trong xuat_pdf.py), co bao tien do; KHONG them thu vien. Test truoc (xfail 2 cai o tests_stress/a), muc tieu 3000 hoc sinh <= 30 s. Giu noi dung chu trong o va so trang nhu cu.
3. Review B lan 2 (SF §5): kiem 3 viec UI (ST-B-006 ma `club_capacity_not_integer`/`capacity_too_large` o js/05_quan_ly.js; ST-B-007 xac nhan lan 2 roi `delete_club(id,true)` / `delete_student(id,true)`; ST-A-001 hien `data.warnings` trong js/18_cai_dat.js). Chi bao cao, toi da 2 vong.
4. Xac nhan: `kiem_nhanh` 7/7, `ruff check .`, byte-identical 3 bo x 20 seed, tests_stress/a va /b chay rieng, test_sf_a_*.py. Cap nhat CHANGELOG.md, TIEN_DO.md, handoff; chay skill `soat-ma` truoc khi push.
5. Khi B xong va CI xanh: B mo MOT PR `SF: fix stress-test bugs`; Truong merge. Khong tao PR neu Truong chua yeu cau.

Khong dung subagent. Qua ~400k token: ket thuc luot, ghi handoff, dung.
