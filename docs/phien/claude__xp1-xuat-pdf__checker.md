# XP1 checker log (CHECKER session; only this file is edited)

## L1 — reviewed 1444d12..446c362: 1 BUG, 1 note
- reportlab==5.1.0 exists on PyPI and installs (wheel downloaded here). L1 tests 10/10 pass WITH pypdf; ruff clean.
- OFL file is the Be Vietnam Pro licence (Copyright 2021 The Be Vietnam Pro Project Authors); both .ttf carry that copyright + SIL OFL text. OK.
- Font embedding, page count, "Trang x/y", no-overwrite, temp-file cleanup and missing-font error all behave as specified.
1. BUG `tests/test_xp1_pdf_loi.py:7` module-level `pytest.importorskip("pypdf")` skips the WHOLE file when pypdf is absent
   (verified: without pypdf, `1 skipped`). Plan says use pypdf only if already installed, else assert font embedded + `/Count n` in bytes.
   Tests that need no pypdf (font embedded, no-overwrite, temp file, error mid-build, missing font) are lost too.
   Fix: import pypdf with try/except; keep a bytes-level fallback (`/Count 3`, `/FontFile2`, `BeVietnamPro`, no leftover tmp) running always.
2. Note (needs lead/Truong decision): `pypdf` in requirements-dev.txt is a 2nd new library (dev-only). §0 allows only reportlab.
   If kept, label it dev-only; preferred: drop it and rely on the bytes-level asserts.

## L1 fix1 — reviewed 446c362..d56c913: NO BUGS
- Without pypdf: 8 passed, 5 skipped (only the text-extraction tests); bytes-level page count (`/Count`), `/FontFile2`, no-overwrite, tmp cleanup, mid-build error, missing font all run. With pypdf: 13 passed. ruff clean.
- `pypdf` removed from requirements-dev.txt; requirements.txt unchanged (reportlab only). Bug 1 and note 2 resolved.
