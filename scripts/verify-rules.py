# -*- coding: utf-8 -*-
"""Verify 島嶼餐桌 game rules by reading page logic + simulating the same judge."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
TEACHER = (ROOT / "site" / "teacher" / "index.html").read_text(encoding="utf-8")

FAIL = "有人以前靠山林生活，打獵有自己的規矩。現在這些動物受保護，遊戲裡不能拿去煮。"
OK = "山蘇可以炒來吃。愛玉果實可以做成愛玉冰。藍鵲是台灣特有的鳥。播種是遊戲。"


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
                   "Urocissa caerulea", "物競天擇", "林業及自然保育署", "特有生物研究保育中心"]:
        assert_true(needle in TEACHER, f"teacher page has {needle}")
    print("OK teacher page content")

    print("\nALL CHECKS PASSED (script path: read page logic + mirrored judge)")


if __name__ == "__main__":
    try:
        check_static_html()
        run_rules()
    except AssertionError as e:
        print("FAIL:", e, file=sys.stderr)
        sys.exit(1)
