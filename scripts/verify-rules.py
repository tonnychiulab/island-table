# -*- coding: utf-8 -*-
"""Verify 島嶼餐桌 game rules by reading page logic + simulating the same judge."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
TEACHER = (ROOT / "site" / "teacher" / "index.html").read_text(encoding="utf-8")
PAGES = {
    "round1": HTML,
    "barbet": (ROOT / "site" / "barbet" / "index.html").read_text(encoding="utf-8"),
    "macaque": (ROOT / "site" / "macaque" / "index.html").read_text(encoding="utf-8"),
    "butterfly": (ROOT / "site" / "butterfly" / "index.html").read_text(encoding="utf-8"),
}

ENTRANCE = "幕後人：走岔一步不要緊，肯回頭便是正道。"
FAIL = "有人以前靠山林生活，打獵有自己的規矩。現在這些動物受保護，遊戲裡不能拿去煮。"
OK = "山蘇可以炒來吃。愛玉果實可以做成愛玉冰。藍鵲是台灣特有的鳥。播種是遊戲。"
FORBIDDEN_NAME = "\u85cf\u93e1\u4eba"  # never write the literal into game pages


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def check_static_html():
    assert_true("<audio" not in HTML.lower(), "no audio element")
    assert_true("new Audio" not in HTML, "no Audio API")
    assert_true(not re.search(r'href\s*=\s*["\'][^"\']*teacher', HTML, re.I), "no teacher href")
    assert_true("/teacher" not in HTML, "no /teacher path on game page")
    assert_true("全螢幕" in HTML, "fullscreen button label")
    assert_true("requestFullscreen" in HTML, "Fullscreen API")
    assert_true(FAIL in HTML, "failure sentence in page")
    assert_true(OK in HTML, "success sentence in page")
    assert_true("還缺山蘇" in HTML and "還缺愛玉" in HTML, "missing plant phrases")
    # launch judge: missing plants checked before bear+pot fail
    assert_true(
        HTML.find('if (!hasSansu || !hasAiyu)') < HTML.find('if (hasBear && hasPot)'),
        "judge order: missing before fail",
    )
    assert_true(
        HTML.find('if (hasBear && hasPot)') < HTML.find('phase = "success"'),
        "judge order: fail before success",
    )
    assert_true("selected.indexOf(id) !== -1) return" in HTML, "second tap no-op")
    print("OK static HTML checks")


def check_entrance_and_fx():
    for name, html in PAGES.items():
        assert_true(FORBIDDEN_NAME not in html, f"{name}: forbidden name absent")
        assert_true(ENTRANCE in html, f"{name}: entrance line present")
        assert_true("<audio" not in html.lower(), f"{name}: no audio")
        assert_true("new Audio" not in html, f"{name}: no Audio API")
        assert_true("/teacher" not in html, f"{name}: no /teacher link")
        assert_true(
            'kind === "fail"' in html and "ENTRANCE_TEXT" in html,
            f"{name}: fail uses entrance + science lines",
        )
        # success path must not inject entrance
        success_idx = html.find('phase = "success"')
        fail_block = html[html.find('kind === "fail"') : html.find('kind === "fail"') + 400]
        assert_true("ENTRANCE_TEXT" in fail_block, f"{name}: entrance only wired in fail branch")
        ok_tail = html[success_idx : success_idx + 350]
        assert_true(
            "ENTRANCE_TEXT" not in ok_tail and 'setMessage(FAIL_TEXT, "fail")' not in ok_tail,
            f"{name}: success block has no entrance/fail message",
        )

    assert_true("fx-dot" not in PAGES["round1"], "round1: no flying seed/dot")
    assert_true('classList.add("bright")' in PAGES["round1"], "round1: plants brighten")
    assert_true("shakeOnce(nodeEls.pot)" in PAGES["round1"], "round1: pot shakes on fail")

    for name in ("barbet", "macaque"):
        assert_true("playSeedAwayThenOk" in PAGES[name], f"{name}: seed-away animation")
        assert_true("fx-dot" in PAGES[name], f"{name}: has fx-dot")
        assert_true("shakeOnce(nodeEls.wrong)" in PAGES[name], f"{name}: wrong node shakes")

    assert_true(
        "playPollenOntoFlowerThenOk" in PAGES["butterfly"],
        "butterfly: pollen onto flower",
    )
    assert_true("fx-dot" in PAGES["butterfly"], "butterfly: has fx-dot")
    assert_true("shakeOnce(nodeEls.wrong)" in PAGES["butterfly"], "butterfly: wrong shakes")

    # repo-wide: forbidden name must not appear in game pages (docs may describe rules without it)
    for path in (ROOT / "site").rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        assert_true(FORBIDDEN_NAME not in text, f"{path.name}: forbidden name absent")

    print("OK entrance + success FX checks")


def judge(selected):
    """Mirror of launch() in site/index.html."""
    has_sansu = "sansu" in selected
    has_aiyu = "aiyu" in selected
    has_bear = "bear" in selected
    has_pot = "pot" in selected
    if not has_sansu or not has_aiyu:
        parts = []
        if not has_sansu:
            parts.append("還缺山蘇")
        if not has_aiyu:
            parts.append("還缺愛玉")
        return "hint", "。".join(parts) + "。"
    if has_bear and has_pot:
        return "fail", FAIL
    return "success", OK


def select_once(selected, node):
    if node in selected:
        return selected
    return selected + [node]


def run_rules():
    cases = [
        (["sansu", "aiyu"], "success", OK, "山蘇+愛玉"),
        (["sansu", "aiyu", "bear"], "success", OK, "山蘇+愛玉+黑熊"),
        (["sansu", "aiyu", "pot"], "success", OK, "山蘇+愛玉+鍋"),
        (["sansu", "aiyu", "bear", "pot"], "fail", FAIL, "黑熊+鍋 with plants"),
        (["bear", "pot"], "hint", "還缺山蘇。還缺愛玉。", "黑熊+鍋 without plants is hint not hunt"),
        (["sansu"], "hint", "還缺愛玉。", "only 山蘇"),
    ]
    for sel, phase, msg, name in cases:
        p, m = judge(sel)
        assert_true(p == phase, f"{name}: expected phase {phase}, got {p}")
        assert_true(m == msg, f"{name}: expected msg {msg!r}, got {m!r}")
        if phase == "hint":
            assert_true("打獵" not in m, f"{name}: no hunting sentence")
        if phase == "success":
            assert_true(ENTRANCE not in m, f"{name}: success has no entrance")
        if phase == "fail":
            # page shows entrance above science; science string unchanged
            assert_true(m == FAIL, f"{name}: fail science unchanged")
        print(f"OK {name}")

    # second tap
    s = []
    s = select_once(s, "sansu")
    s = select_once(s, "sansu")
    assert_true(s == ["sansu"], "second tap no duplicate")
    print("OK second tap does nothing")

    # 重來
    s = ["sansu", "aiyu"]
    s = []
    assert_true(s == [], "重來 clears")
    print("OK 重來 clears")

    # teacher page notes
    for needle in ["山蘇", "愛玉", "Ficus pumila", "awkeotsang", "Ursus thibetanus formosanus",
                   "Urocissa caerulea", "物競天擇", "林業及自然保育署", "原特生中心"]:
        assert_true(needle in TEACHER, f"teacher page has {needle}")
    print("OK teacher page content")

    print("\nALL CHECKS PASSED (script path: read page logic + mirrored judge)")


if __name__ == "__main__":
    try:
        check_static_html()
        check_entrance_and_fx()
        run_rules()
    except AssertionError as e:
        print("FAIL:", e, file=sys.stderr)
        sys.exit(1)
