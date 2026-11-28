"""TK1 — giao diện kiosk "tự nhiên, ổn định" (Chromium thật; dữ liệu MÔ PHỎNG, không phải khảo sát thật).

Lô L1: token (thang chữ, thang khoảng cách, chiều cao điều khiển 36/44, bo góc, bóng, thời lượng) và
`scrollbar-gutter: stable`. Cổng đăng ký (`.dk-*`) không thuộc phạm vi: bị loại khỏi phép đếm tĩnh.
Các lô sau (L2 nút/ô nhập, L3 tab/thanh cảnh báo) thêm test vào CÙNG tệp này, dùng chung fixture `mo_ux5a`.
"""

import os
import re

from _ux5a_chung import GOC, mo_ux5a  # noqa: F401

CSS = os.path.join(GOC, "style.css")
THE_QUAN_TRI = ["pipeline", "fallback", "scoring", "results", "others", "admin"]
RE_PX = re.compile(r"^(-?[\d.]+)px$")


def _khoi_css(text):
    """[(bộ chọn, thân)] của mọi khối trong style.css, đi sâu vào @media / @supports; bỏ chú thích."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    kq, sau, buf, sel, bd = [], 0, "", "", 0
    for i, c in enumerate(text):
        if c == "{":
            if sau == 0:
                sel, buf, bd = buf.strip(), "", i + 1
            sau += 1
        elif c == "}":
            sau -= 1
            if sau == 0:
                than = text[bd:i]
                if sel.startswith(("@media", "@supports")):
                    kq += _khoi_css(than)
                elif not sel.startswith("@"):
                    kq.append((sel, than))
                buf = ""
        elif sau == 0:
            buf += c
    return kq


def _co_chu_goc(text):
    m = re.search(r"html,\s*body\s*\{[^}]*font-size:\s*([\d.]+)px", text)
    return float(m.group(1)) if m else 16.0


def _co_chu_px(gt, rem_px):
    gt = gt.replace("!important", "").strip()
    if gt in ("0", "inherit", "initial", "unset") or gt.startswith("var("):
        return None                              # token: được đếm qua định nghĩa trên :root
    if gt.endswith("rem"):
        return round(float(gt[:-3]) * rem_px, 2)
    if gt.endswith("em") or gt.endswith("%"):
        return None                              # tương đối theo cha: không phải bậc chữ độc lập
    m = RE_PX.match(gt)
    return float(m.group(1)) if m else None


def test_so_co_chu_khac_nhau_trong_style_css_toi_da_tam():
    """Kiểm nhận (d): ≤ 8 cỡ chữ khác nhau (đã quy ra px) ngoài cổng đăng ký; thang chữ nằm trên :root."""
    text = open(CSS, encoding="utf-8").read()
    rem_px = _co_chu_goc(text)
    khoi = _khoi_css(text)
    token = {}
    for sel, than in khoi:
        if sel.strip() == ":root":
            for ten, gt in re.findall(r"(--fs-[\w]+):\s*([^;]+);", than):
                token[ten] = _co_chu_px(gt, rem_px)
    assert len(token) == 6 and all(token.values()), token
    cac = set(token.values())
    for sel, than in khoi:
        if "dk-" in sel:
            continue
        for gt in re.findall(r"(?<![-\w])font-size:\s*([^;}]+)", than):
            gt = gt.strip()
            m = re.fullmatch(r"var\((--fs-[\w]+)\)", gt)
            if m:
                assert m.group(1) in token, gt
                continue
            px = _co_chu_px(gt, rem_px)
            if px is not None:
                cac.add(px)
    assert len(cac) <= 8, sorted(cac)


def test_token_khoang_cach_cao_do_ban_kinh_tren_root(mo_ux5a):  # noqa: F811
    page, api, loi = mo_ux5a("quan_tri")
    v = page.evaluate("""() => { const s = getComputedStyle(document.documentElement);
      return ['--sp-1','--sp-2','--sp-3','--sp-4','--sp-5','--sp-6','--sp-7','--control-h-sm','--control-h',
              '--radius-sm','--radius-md','--radius-pill','--shadow-1','--shadow-2','--dur-1','--dur-2']
        .map(k => [k, s.getPropertyValue(k).trim()]); }""")
    d = dict(v)
    assert [d["--sp-%d" % i] for i in range(1, 8)] == ["4px", "8px", "12px", "16px", "24px", "32px", "48px"], d
    assert (d["--control-h-sm"], d["--control-h"]) == ("36px", "44px"), d
    assert (d["--radius-sm"], d["--radius-md"], d["--radius-pill"]) == ("6px", "10px", "999px"), d
    assert d["--shadow-1"] and d["--shadow-2"] and d["--dur-1"] and d["--dur-2"], d
    assert not loi, loi


def test_gutter_thanh_cuon_on_dinh_va_h1_cung_toa_do_trai(mo_ux5a):  # noqa: F811
    """Phát hiện 1: thẻ dài có thanh cuộn, thẻ ngắn không → nội dung nhảy ngang. `scrollbar-gutter: stable`
    giữ chỗ; `h1` của mọi thẻ cùng toạ độ trái (kiểm nhận b)."""
    page, api, loi = mo_ux5a("quan_tri")
    assert page.evaluate("getComputedStyle(document.documentElement).scrollbarGutter").startswith("stable")
    trai = {}
    for tab in THE_QUAN_TRI:
        page.locator('.nav-item[data-tab="%s"]' % tab).click()
        page.wait_for_selector("#view-%s" % tab, state="visible")
        trai[tab] = page.evaluate(
            "(t) => document.querySelector('#view-' + t + ' h1').getBoundingClientRect().left", tab)
    assert len({round(x, 1) for x in trai.values()}) == 1, trai
    assert not loi, loi
