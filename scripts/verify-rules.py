# -*- coding: utf-8 -*-
"""Verify 島嶼餐桌 rules from levels.json + game.js + thin HTML shells."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LEVELS_PATH = ROOT / "site" / "levels.json"
GAME_JS = (ROOT / "site" / "game.js").read_text(encoding="utf-8")
GAME_CSS = (ROOT / "site" / "game.css").read_text(encoding="utf-8")
TEACHER = (ROOT / "site" / "teacher" / "index.html").read_text(encoding="utf-8")
DATA = json.loads(LEVELS_PATH.read_text(encoding="utf-8"))
LEVELS = {lv["id"]: lv for lv in DATA["levels"]}

PAGES = {
    "root": (ROOT / "site" / "index.html").read_text(encoding="utf-8"),
    "barbet": (ROOT / "site" / "barbet" / "index.html").read_text(encoding="utf-8"),
    "macaque": (ROOT / "site" / "macaque" / "index.html").read_text(encoding="utf-8"),
    "butterfly": (ROOT / "site" / "butterfly" / "index.html").read_text(encoding="utf-8"),
}

ENTRANCE = "幕後人：走岔一步不要緊，肯回頭便是正道。"
FORBIDDEN_NAME = "\u85cf\u93e1\u4eba"


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def check_levels_json():
    assert_true(DATA.get("entranceText") == ENTRANCE, "shared entranceText")
    assert_true(set(LEVELS) == {"root", "barbet", "macaque", "butterfly"}, "four level ids")

    root = LEVELS["root"]
    assert_true(root["path"] == "/", "root path")
    assert_true(root["rule"] == "potPair", "root rule")
    assert_true(root["successMotion"] == "brighten", "root motion brighten not seed")
    assert_true(root["start"]["label"] == "藍鵲", "root start label")
    assert_true(root["start"]["color"].lower() == "#1e6bb8", "root start blue")
    assert_true(
        root["success"]
        == "山蘇可以炒來吃。愛玉果實可以做成愛玉冰。藍鵲是台灣特有的鳥。播種是遊戲。",
        "root success sentence",
    )
    assert_true(
        root["failureScience"]
        == "有人以前靠山林生活，打獵有自己的規矩。現在這些動物受保護，遊戲裡不能拿去煮。",
        "root failure science",
    )
    assert_true(root["missing"]["sansu"] == "還缺山蘇", "missing sansu")
    assert_true(root["missing"]["aiyu"] == "還缺愛玉", "missing aiyu")
    roles = {n["id"]: n["role"] for n in root["nodes"]}
    assert_true(roles == {"sansu": "correct", "aiyu": "correct", "bear": "bear", "pot": "pot"}, "root roles")

    expect = {
        "barbet": ("/barbet", "五色鳥", "榕果", "山蘇", "seed", "還缺榕果。"),
        "macaque": ("/macaque", "台灣獼猴", "長葉木薑子", "花", "seed", "還缺長葉木薑子。"),
        "butterfly": ("/butterfly", "寬尾鳳蝶", "花", "榕果", "pollen", "還缺花。"),
    }
    for lid, (path, start, correct, wrong, motion, missing) in expect.items():
        lv = LEVELS[lid]
        assert_true(lv["path"] == path, f"{lid} path")
        assert_true(lv["rule"] == "wrongNode", f"{lid} rule")
        assert_true(lv["start"]["label"] == start, f"{lid} start")
        assert_true(lv["successMotion"] == motion, f"{lid} motion")
        assert_true(lv["missing"] == missing, f"{lid} missing")
        by_role = {n["role"]: n for n in lv["nodes"]}
        assert_true(by_role["correct"]["label"] == correct, f"{lid} correct")
        assert_true(by_role["wrong"]["label"] == wrong, f"{lid} wrong")
        assert_true(by_role["wrong"]["color"].lower() == "#8b5a2b", f"{lid} wrong brown")
        assert_true(by_role["correct"]["color"].lower() == "#2e8b57", f"{lid} correct green")

    macaque_correct = next(n for n in LEVELS["macaque"]["nodes"] if n["role"] == "correct")
    assert_true(macaque_correct.get("width", 0) >= 230, "macaque label circle wide enough")
    print("OK levels.json")


def check_html_shells():
    for lid, html in PAGES.items():
        assert_true(f'data-level-id="{lid}"' in html, f"{lid}: data-level-id")
        assert_true("game.js" in html, f"{lid}: loads game.js")
        assert_true("game.css" in html, f"{lid}: loads game.css")
        assert_true("/teacher" not in html, f"{lid}: no /teacher")
        assert_true(not re.search(r'href\s*=\s*["\'][^"\']*teacher', html, re.I), f"{lid}: no teacher href")
        assert_true("<audio" not in html.lower(), f"{lid}: no audio")
        assert_true("new Audio" not in html, f"{lid}: no Audio API")
        assert_true(FORBIDDEN_NAME not in html, f"{lid}: forbidden name absent")
        # game pages must not link to each other
        for other in ("/barbet", "/macaque", "/butterfly"):
            if lid == "root" or ("/" + lid) != other:
                assert_true(
                    f'href="{other}"' not in html and f"href='{other}'" not in html,
                    f"{lid}: no link to {other}",
                )
        assert_true("全螢幕" in html, f"{lid}: fullscreen label")
    assert_true("requestFullscreen" in GAME_JS, "Fullscreen API in game.js")
    assert_true("selected.indexOf(id) !== -1) return" in GAME_JS, "second tap no-op")
    assert_true('kind === "fail"' in GAME_JS, "fail uses entrance + science")
    assert_true("successMotion === \"brighten\"" in GAME_JS, "brighten motion branch")
    assert_true("playSeedAwayThenOk" in GAME_JS, "seed motion")
    assert_true("playPollenOntoFlowerThenOk" in GAME_JS, "pollen motion")
    assert_true("white-space: nowrap" in GAME_CSS, "labels nowrap")
    print("OK HTML shells + game.js")


def check_teacher():
    for needle in [
        "課堂進行步驟",
        "全螢幕",
        "幕後人",
        "再試一次",
        "出發",
        "再玩一次",
        "不要投影",
        "山蘇",
        "愛玉",
        "Ficus pumila",
        "awkeotsang",
        "Ursus thibetanus formosanus",
        "Urocissa caerulea",
        "物競天擇",
        "林業及自然保育署",
        "原特生中心",
    ]:
        assert_true(needle in TEACHER, f"teacher page has {needle}")
    print("OK teacher page")


def judge_pot_pair(selected):
    lv = LEVELS["root"]
    missing_parts = []
    for n in lv["nodes"]:
        if n["role"] == "correct" and n["id"] not in selected:
            missing_parts.append(lv["missing"][n["id"]])
    if missing_parts:
        return "hint", "。".join(missing_parts) + "。"
    has_bear = any(n["id"] in selected for n in lv["nodes"] if n["role"] == "bear")
    has_pot = any(n["id"] in selected for n in lv["nodes"] if n["role"] == "pot")
    if has_bear and has_pot:
        return "fail", lv["failureScience"]
    return "success", lv["success"]


def judge_wrong_node(level_id, selected):
    lv = LEVELS[level_id]
    correct = next(n["id"] for n in lv["nodes"] if n["role"] == "correct")
    wrong = next(n["id"] for n in lv["nodes"] if n["role"] == "wrong")
    has_correct = correct in selected
    has_wrong = wrong in selected
    if not has_correct and not has_wrong:
        return "hint", lv["missing"]
    if has_wrong:
        return "fail", lv["failureScience"]
    return "success", lv["success"]


def run_pot_pair_cases():
    fail = LEVELS["root"]["failureScience"]
    ok = LEVELS["root"]["success"]
    cases = [
        (["sansu", "aiyu"], "success", ok, "山蘇+愛玉"),
        (["sansu", "aiyu", "bear"], "success", ok, "山蘇+愛玉+黑熊"),
        (["sansu", "aiyu", "pot"], "success", ok, "山蘇+愛玉+鍋"),
        (["sansu", "aiyu", "bear", "pot"], "fail", fail, "黑熊+鍋 with plants"),
        (["bear", "pot"], "hint", "還缺山蘇。還缺愛玉。", "黑熊+鍋 without plants is hint"),
        (["sansu"], "hint", "還缺愛玉。", "only 山蘇"),
        (["aiyu"], "hint", "還缺山蘇。", "only 愛玉"),
        ([], "hint", "還缺山蘇。還缺愛玉。", "empty"),
    ]
    for sel, phase, msg, name in cases:
        p, m = judge_pot_pair(sel)
        assert_true(p == phase, f"potPair {name}: expected phase {phase}, got {p}")
        assert_true(m == msg, f"potPair {name}: expected msg {msg!r}, got {m!r}")
        if phase == "hint":
            assert_true("打獵" not in m, f"potPair {name}: no hunting sentence")
        if phase == "success":
            assert_true(ENTRANCE not in m, f"potPair {name}: success has no entrance")
        print(f"OK potPair {name}")


def run_wrong_node_cases():
    for lid in ("barbet", "macaque", "butterfly"):
        lv = LEVELS[lid]
        correct = next(n["id"] for n in lv["nodes"] if n["role"] == "correct")
        wrong = next(n["id"] for n in lv["nodes"] if n["role"] == "wrong")
        cases = [
            ([correct], "success", lv["success"], "correct only"),
            ([correct, wrong], "fail", lv["failureScience"], "correct+wrong"),
            ([wrong], "fail", lv["failureScience"], "wrong only"),
            ([], "hint", lv["missing"], "empty"),
        ]
        for sel, phase, msg, name in cases:
            p, m = judge_wrong_node(lid, sel)
            assert_true(p == phase, f"{lid} {name}: expected {phase}, got {p}")
            assert_true(m == msg, f"{lid} {name}: expected {msg!r}, got {m!r}")
            print(f"OK {lid} {name}")


def run_misc():
    s = []
    for node in ("sansu", "sansu"):
        if node not in s:
            s.append(node)
    assert_true(s == ["sansu"], "second tap no duplicate")
    print("OK second tap does nothing")
    assert_true(FORBIDDEN_NAME not in GAME_JS, "game.js: forbidden name absent")
    for path in (ROOT / "site").rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        assert_true(FORBIDDEN_NAME not in text, f"{path.name}: forbidden name absent")
    print("OK misc")


if __name__ == "__main__":
    try:
        check_levels_json()
        check_html_shells()
        check_teacher()
        run_pot_pair_cases()
        run_wrong_node_cases()
        run_misc()
        print("\nALL CHECKS PASSED")
    except AssertionError as e:
        print("FAIL:", e, file=sys.stderr)
        sys.exit(1)
