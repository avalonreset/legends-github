#!/usr/bin/env python3
"""Render outlined Legends Font SVG design cards (rev r1) for the legends-github README."""
import argparse
import math
from pathlib import Path
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True


def _find_typeset_root() -> Path:
    candidates = []
    if os.environ.get("AVALON_TYPESET_ROOT"):
        candidates.append(Path(os.environ["AVALON_TYPESET_ROOT"]))
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidates.append(parent / "avalonreset")
        candidates.append(parent / "cto-legends-glowup" / "repos" / "avalonreset")
    for cand in candidates:
        if (cand / "typeset.py").is_file():
            return cand
    raise SystemExit("FAIL: typeset.py not found; set AVALON_TYPESET_ROOT to the avalonreset directory.")


AVALON_ROOT = _find_typeset_root()
sys.path.insert(0, str(AVALON_ROOT))
from typeset import FONT, Typesetter, width  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REV = "r1"
CARDS_DIR = ROOT / "assets" / "cards" / REV

TYPE = {"head": 14, "title": 12, "body": 11, "label": 9}
K_WIDE = 829 / 886

BORDER = 'stroke="#ffffff" stroke-opacity="0.09" stroke-width="1"'
HAIR = 'stroke="#ffffff" stroke-opacity="0.07" stroke-width="1"'
CHIP = 'fill="#090a0e" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1"'
RED = 'stroke="#ff0000" stroke-opacity="0.68" stroke-width="1"'
RED_HAIR = 'stroke="#ff0000" stroke-opacity="0.30" stroke-width="1"'


def u(role: str, k: float) -> float:
    return round(TYPE[role] / k, 2)


def svg(vb: str, body: str, t: Typesetter = None) -> str:
    defs = t.defs() if t else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="100%">\n{defs}{body}</svg>\n'


def button(t: Typesetter, cx: float, y: float, fill: str, label: str, size: float, weight: str = "600") -> str:
    plain = re.sub(r"<[^>]+>|&\w+;", "", label)
    spacing = size * 0.1 if plain.isupper() else 0.0
    return t.run(cx, y, size, label, fill, weight, "middle", spacing)


def panel_defs(h: float) -> str:
    return (
        "  <defs>\n"
        f'    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="{h}" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.04"/>'
        '<stop offset="0.55" stop-color="#ffffff" stop-opacity="0"/></linearGradient>\n'
        f'    <linearGradient id="edge" x1="0" y1="0" x2="0" y2="{h}" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.22"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0.08"/></linearGradient>\n'
        "  </defs>\n"
    )


def render_slot_1() -> None:
    """Slot 1: Agent handoff header bar above the copy-paste code block."""
    t = Typesetter()
    ti, bd = u("title", K_WIDE), u("body", K_WIDE)
    note = "// paste this into claude code, codex or any coding agent and it does the setup"
    h = 34
    y_base = 22.5
    body = (
        f'  <rect x="0.5" y="0.5" width="885" height="{h - 1}" rx="4" fill="#0c0507" {RED}/>\n'
        f'  <rect x="0.5" y="0.5" width="4" height="{h - 1}" rx="2" fill="#ff0000"/>\n'
        + t.run(16, y_base, ti, "&gt;_", "#ff0000", "700")
        + t.run(16 + width("&gt;_", ti) + 8, y_base, ti, "agent handoff", "#ffffff", "700")
        + t.run(16 + width("&gt;_", ti) + 8 + width("agent handoff", ti) + 12, y_base, bd, note, "#a1a1aa")
    )
    (CARDS_DIR / "slot-1-agent-handoff.svg").write_text(svg(f"0 0 886 {h}", body, t), encoding="utf-8")


def render_slot_2() -> None:
    """Slot 2: Three-pillar overview card for legends-github."""
    t = Typesetter()
    hd, ti, bd, lb = u("head", K_WIDE), u("title", K_WIDE), u("body", K_WIDE), u("label", K_WIDE)
    x0, x1 = 20, 866
    h = 198
    body = (
        panel_defs(h)
        + f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="#000000"/>\n'
        + f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="url(#sheen)" stroke="url(#edge)" stroke-width="1"/>\n'
        + f'  <rect x="1" y="1" width="4" height="{h - 2}" rx="2" fill="#ff0000"/>\n'
    )
    y_head = 26
    body += t.run(x0, y_head, ti, "&gt;_", "#ff0000", "700")
    x_title = x0 + width("&gt;_", ti) + 8
    headline = "Audit repo health. Rank 20 search topics. Ship clean releases."
    right_tag = "// 13 workflows · dataforseo · pixel parity"
    assert x_title + width(headline, hd) + 16 <= x1 - width(right_tag, lb), "Slot 2 header collision"
    body += t.run(x_title, y_head, hd, headline, "#ffffff", "700")
    body += t.run(x1, y_head, lb, right_tag, "#a1a1aa", "400", "end")
    body += f'  <line x1="{x0}" y1="40" x2="{x1}" y2="40" {HAIR}/>\n'

    pillars = [
        (
            "01",
            "13 clean-tree workflows",
            [
                "Audit README, license, community,",
                "and release readiness into external",
                "artifacts without dirtying git.",
            ],
        ),
        (
            "02",
            "20-topic &amp; SERP discovery",
            [
                "Pull verified DataForSEO demand,",
                "strip build-tool filler, and rank",
                "20 commercial-intent repo topics.",
            ],
        ),
        (
            "03",
            "Preservation &amp; pixel parity",
            [
                "Score existing READMEs verbatim",
                "and verify live 1280x640 Open Graph",
                "social cards via GitHub GraphQL.",
            ],
        ),
    ]
    gap = 28
    col_w = (x1 - x0 - 2 * gap) / 3
    y_col_head = 67
    for i, (num, title, lines) in enumerate(pillars):
        cx = x0 + i * (col_w + gap)
        plain_title = title.replace("&amp;", "&")
        assert width(num, lb) + 9 + width(plain_title, ti) <= col_w, f"Slot 2 pillar title overflow: {title}"
        body += t.run(cx, y_col_head, lb, num, "#ff0000", "700")
        body += t.run(cx + width(num, lb) + 9, y_col_head, ti, title, "#ffffff", "700")
        for j, ln in enumerate(lines):
            plain_ln = ln.replace("&amp;", "&")
            assert width(plain_ln, bd) <= col_w, f"Slot 2 pillar line overflow: {ln}"
            body += t.run(cx, y_col_head + 22 + 18 * j, bd, ln, "#a1a1aa", "400")
        if i > 0:
            vx = cx - gap / 2
            body += f'  <line x1="{vx:.2f}" y1="52" x2="{vx:.2f}" y2="136" {HAIR}/>\n'

    body += f'  <line x1="{x0}" y1="148" x2="{x1}" y2="148" {HAIR}/>\n'
    chip_top = 165
    base = chip_top + 13.5
    lab = "works with:"
    body += t.run(x0, base, lb, lab, "#a1a1aa", "600")
    cx = x0 + width(lab, lb) + 10
    chips = ("github-cli", "20-topics", "readme-audit", "social-preview", "release-gate", "dataforseo", "claude")
    for ch in chips:
        cw = width(ch, lb) + 16
        body += f'  <rect x="{cx:.2f}" y="{chip_top}" width="{cw:.2f}" height="20" rx="3" {CHIP}/>\n'
        body += t.run(cx + cw / 2, base, lb, ch, "#e4e4e7", "600", "middle")
        cx += cw + 6
    right_foot = "clean-tree repo engine"
    assert cx + 10 <= x1 - width(right_foot, lb), "Slot 2 chip bar collision"
    body += t.run(x1, base, lb, right_foot, "#ff0000", "600", "end")

    (CARDS_DIR / "slot-2-three-pillars.svg").write_text(svg(f"0 0 886 {h}", body, t), encoding="utf-8")


def render_slot_3() -> None:
    """Slot 3: 4-row visual chain map ('Say the job in plain words')."""
    t = Typesetter()
    hd, ti, bd, lb = u("head", K_WIDE), u("title", K_WIDE), u("body", K_WIDE), u("label", K_WIDE)
    h = 208
    x0, x1 = 20, 866
    body = (
        panel_defs(h)
        + f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="#000000"/>\n'
        + f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="url(#sheen)" stroke="url(#edge)" stroke-width="1"/>\n'
        + f'  <rect x="1" y="1" width="4" height="{h - 2}" rx="2" fill="#ff0000"/>\n'
    )
    body += t.run(x0, 26, hd, "Say the job in plain words", "#ffffff", "700")
    body += t.run(
        x0 + width("Say the job in plain words", hd) + 12,
        26,
        lb,
        "// your agent audits, optimizes topics and verifies releases without dirtying git",
        "#ff0000",
        "600",
    )
    body += f'  <line x1="{x0}" y1="38" x2="{x1}" y2="38" {HAIR}/>\n'

    rows = [
        (
            "01",
            '"Audit our repo and release readiness"',
            'audit --offline <tspan fill="#ff0000">→</tspan> FINDINGS.json <tspan fill="#ff0000">→</tspan> external artifacts (clean git tree)',
        ),
        (
            "02",
            '"Rank 20 topics from search demand"',
            'research --execute <tspan fill="#ff0000">→</tspan> seo (strip build filler) <tspan fill="#ff0000">→</tspan> meta --apply',
        ),
        (
            "03",
            '"Score our README without overwriting"',
            'readme (preserve-existing) <tspan fill="#ff0000">→</tspan> discover <tspan fill="#ff0000">→</tspan> 14-day traffic baseline',
        ),
        (
            "04",
            '"Verify our 1280x640 social preview"',
            'social-preview <tspan fill="#ff0000">→</tspan> upload card <tspan fill="#ff0000">→</tspan> --verify (GraphQL pixel parity)',
        ),
    ]

    pill_x = 368
    pill_w = x1 - pill_x
    for i, (num, prompt_txt, chain_markup) in enumerate(rows):
        ry = 64 + i * 42
        if i > 0:
            div_y = ry - 25
            body += f'  <line x1="{x0}" y1="{div_y}" x2="{x1}" y2="{div_y}" {HAIR}/>\n'
        prompt_x = x0 + width(num, lb) + 10
        plain_prompt = prompt_txt.replace("&amp;", "&")
        plain_chain = re.sub(r"<[^>]+>", "", chain_markup).replace("&amp;", "&")
        assert prompt_x + width(plain_prompt, bd) + 14 <= pill_x - 16, f"Row {num} collides with arrow"
        assert 12 + width(plain_chain, lb) <= pill_w - 10, f"Row {num} chain overflows pill: {plain_chain}"
        body += t.run(x0, ry, lb, num, "#ff0000", "700")
        body += t.run(prompt_x, ry, bd, prompt_txt, "#ffffff", "700")
        body += t.run(pill_x - 16, ry, ti, "→", "#ff0000", "700", "middle")
        body += f'  <rect x="{pill_x}" y="{ry - 16.5:.1f}" width="{pill_w}" height="24" rx="3" fill="#090a0e" {RED_HAIR}/>\n'
        body += t.run(pill_x + 12, ry - 0.5, lb, chain_markup, "#ffffff", "600")

    (CARDS_DIR / "slot-3-plain-english-chains.svg").write_text(svg(f"0 0 886 {h}", body, t), encoding="utf-8")


def render_slot_4() -> None:
    """Slot 4: Two-chamber Repository Intelligence & 7-workflow Architectural Card."""
    t = Typesetter()
    hd, ti, bd, lb = u("head", K_WIDE), u("title", K_WIDE), u("body", K_WIDE), u("label", K_WIDE)
    x0, x1 = 20, 866
    h = 204
    body = (
        panel_defs(h)
        + f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="#000000"/>\n'
        + f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="url(#sheen)" stroke="url(#edge)" stroke-width="1"/>\n'
        + f'  <rect x="1" y="1" width="4" height="{h - 2}" rx="2" fill="#ff0000"/>\n'
    )
    body += t.run(x0, 26, hd, "How clean-tree evidence audits and live discovery work", "#ffffff", "700")
    body += t.run(x1, 26, lb, "// 13-workflow portable CLI architecture", "#a1a1aa", "400", "end")
    body += f'  <line x1="{x0}" y1="40" x2="{x1}" y2="40" {HAIR}/>\n'

    box_w = 412
    box_h = 92
    # Left chamber: 4-State Clean-Tree Audit
    body += f'  <rect x="{x0}" y="52" width="{box_w}" height="{box_h}" rx="3" fill="#090a0e" {BORDER}/>\n'
    gx, gy = x0 + 16, 68
    body += f'  <rect x="{gx}" y="{gy}" width="52" height="60" rx="3" fill="#000000" {BORDER}/>\n'
    body += t.run(gx + 26, gy + 24, ti, "CLEAN", "#ff0000", "700", "middle")
    body += t.run(gx + 26, gy + 41, lb, "TREE", "#a1a1aa", "600", "middle")
    body += f'  <rect x="{gx + 8}" y="{gy + 48}" width="36" height="4" rx="2" fill="#ff0000"/>\n'

    ltx = x0 + 82
    ltitle = "4-State Clean-Tree Audit"
    ltag = "// external artifacts"
    assert ltx + width(ltitle, ti) + 8 + width(ltag, lb) <= x0 + box_w - 10, "Left chamber title overflow"
    body += t.run(ltx, 73, ti, ltitle, "#ffffff", "700")
    body += t.run(ltx + width(ltitle, ti) + 8, 73, lb, ltag, "#ff0000", "600")
    llines = (
        ("Routes findings to ~/.legends-github/repos", "#d4d4d8"),
        ("or --artifacts-dir, preserves custom README", "#a1a1aa"),
        ("layouts, and never edits target .gitignore.", "#a1a1aa"),
    )
    for j, (lln, lcol) in enumerate(llines):
        assert ltx + width(lln, bd) <= x0 + box_w - 12, f"Left chamber line overflows: {lln}"
        body += t.run(ltx, 94 + 18 * j, bd, lln, lcol, "400")

    # Right chamber: Demand & Pixel Verification
    rx0 = x1 - box_w
    body += f'  <rect x="{rx0}" y="52" width="{box_w}" height="{box_h}" rx="3" fill="#0c0507" {RED_HAIR}/>\n'
    rgx, rgy = rx0 + 16, 68
    body += f'  <rect x="{rgx}" y="{rgy}" width="52" height="60" rx="3" fill="#000000" stroke="#ff0000" stroke-opacity="0.55" stroke-width="1"/>\n'
    body += t.run(rgx + 26, rgy + 24, ti, "20+OG", "#ffffff", "700", "middle")
    body += t.run(rgx + 26, rgy + 41, lb, "VERIFY", "#ff0000", "700", "middle")
    body += f'  <rect x="{rgx + 8}" y="{rgy + 48}" width="36" height="4" rx="2" fill="#ffffff"/>\n'

    rtx = rx0 + 82
    rtitle = "Demand &amp; Pixel Verification"
    rtitle_plain = "Demand & Pixel Verification"
    rtag = "// seo &amp; graphql"
    rtag_plain = "// seo & graphql"
    assert rtx + width(rtitle_plain, ti) + 8 + width(rtag_plain, lb) <= rx0 + box_w - 10, "Right chamber title overflow"
    body += t.run(rtx, 73, ti, rtitle, "#ffffff", "700")
    body += t.run(rtx + width(rtitle_plain, ti) + 8, 73, lb, rtag, "#ff0000", "600")
    rlines = (
        ("Ranks 20 GitHub topics from DataForSEO", "#d4d4d8"),
        ("volume &amp; CPC, strips build-tool noise, and", "#a1a1aa"),
        ("verifies 1280x640 Open Graph cards live.", "#a1a1aa"),
    )
    for j, (rln, rcol) in enumerate(rlines):
        plain_rln = rln.replace("&amp;", "&")
        assert rtx + width(plain_rln, bd) <= rx0 + box_w - 12, f"Right chamber line overflows: {rln}"
        body += t.run(rtx, 94 + 18 * j, bd, rln, rcol, "400")

    # Bottom bar with 7 workflow pills
    body += f'  <line x1="{x0}" y1="156" x2="{x1}" y2="156" {HAIR}/>\n'
    chip_top = 170
    base = chip_top + 13.5
    surfaces = (
        ("01", "Repo Audit"),
        ("02", "20-Topic SEO"),
        ("03", "README Score"),
        ("04", "Discovery Plan"),
        ("05", "Social Card"),
        ("06", "Legal/Health"),
        ("07", "Release Gate"),
    )
    total_slots = len(surfaces)
    slot_gap = 8
    slot_w = (x1 - x0 - (total_slots - 1) * slot_gap) / total_slots
    for idx, (num, sname) in enumerate(surfaces):
        px = x0 + idx * (slot_w + slot_gap)
        plain_pill = f"{num} {sname}"
        assert width(plain_pill, lb) <= slot_w - 8, f"Slot 4 pill overflow: {plain_pill}"
        body += f'  <rect x="{px:.2f}" y="{chip_top}" width="{slot_w:.2f}" height="21" rx="3" {CHIP}/>\n'
        label_markup = f'<tspan fill="#ff0000">{num}</tspan> {sname}'
        body += t.run(px + slot_w / 2, base, lb, label_markup, "#ffffff", "600", "middle")

    (CARDS_DIR / "slot-4-repo-intelligence.svg").write_text(svg(f"0 0 886 {h}", body, t), encoding="utf-8")


def render_slot_5() -> None:
    """Slot 5: Comparison table ('Ad-hoc repo scripts & LLM guesses' vs 'Evidence-backed repo engine // legends-github')."""
    t = Typesetter()
    ti, lb = u("title", K_WIDE), u("label", K_WIDE)
    rows = [
        ("GitHub topics &amp; metadata", "Guesses tags &amp; stuffs vite/eslint filler", "DataForSEO volume/CPC + 20 clean commercial topics"),
        ("README upgrades &amp; layout", "Overwrites custom banners &amp; embeds", "Preservation mode scores sections without clobbering"),
        ("Audit tree &amp; offline honesty", "Dirties repo root &amp; penalizes offline runs", "4-state findings in external cache; clean git tree"),
        ("Social preview Open Graph", "Assumes upload worked; serves stale avatar", "Verifies live 1280x640 GraphQL image pixel-for-pixel"),
    ]
    h = 198
    col0_x, col1_x, col2_x = 20, 206, 504
    body = (
        panel_defs(h)
        + f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="#000000"/>\n'
        + f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="url(#sheen)" stroke="url(#edge)" stroke-width="1"/>\n'
        + f'  <rect x="{col2_x - 12}" y="7" width="{880 - (col2_x - 12)}" height="{h - 14}" rx="3" fill="#0c0507" {RED_HAIR}/>\n'
    )
    y_hdr = 27
    hdr1_plain = "Ad-hoc repo scripts & LLM guesses"
    hdr2_plain = "Evidence-backed repo engine"
    assert col1_x + width(hdr1_plain, ti) <= col2_x - 18, "Slot 5 col1 header overflow"
    assert col2_x + width(hdr2_plain, ti) + 8 + width("// legends-github", lb) <= 870, "Slot 5 col2 header overflow"
    body += t.run(col0_x, y_hdr, lb, "comparison", "#8b8b94", "600")
    body += t.run(col1_x, y_hdr, ti, "Ad-hoc repo scripts &amp; LLM guesses", "#a1a1aa", "700")
    body += t.run(col2_x, y_hdr, ti, hdr2_plain, "#ffffff", "700")
    body += t.run(col2_x + width(hdr2_plain, ti) + 8, y_hdr, lb, "// legends-github", "#ff0000", "600")
    body += f'  <line x1="16" y1="39" x2="870" y2="39" {HAIR}/>\n'
    body += f'  <line x1="{col1_x - 12}" y1="12" x2="{col1_x - 12}" y2="{h - 12}" {HAIR}/>\n'

    for i, (label_txt, raw_txt, emp_txt) in enumerate(rows):
        ry = 64 + i * 38
        if i > 0:
            div_y = ry - 21
            body += f'  <line x1="16" y1="{div_y}" x2="870" y2="{div_y}" {HAIR}/>\n'
        plain_label = label_txt.replace("&amp;", "&")
        plain_raw = raw_txt.replace("&amp;", "&")
        plain_emp = emp_txt.replace("&amp;", "&")
        assert col0_x + width(plain_label, lb) <= col1_x - 18, f"Slot 5 col0 overflow: {plain_label}"
        assert col1_x + width(plain_raw, lb) <= col2_x - 24, f"Slot 5 col1 overflow: {plain_raw}"
        assert col2_x + width(plain_emp, lb) <= 870, f"Slot 5 col2 overflow: {plain_emp}"
        body += t.run(col0_x, ry, lb, label_txt, "#e4e4e7", "600")
        body += t.run(col1_x, ry, lb, raw_txt, "#a1a1aa", "400")
        body += t.run(col2_x, ry, lb, emp_txt, "#ffffff", "600")

    (CARDS_DIR / "slot-5-generic-vs-github.svg").write_text(svg(f"0 0 886 {h}", body, t), encoding="utf-8")


def render_slot_shrine() -> None:
    """Graphic shrine for the cto-legends GitHub Star List."""
    t = Typesetter()
    hd, bd, lb = u("head", K_WIDE), u("body", K_WIDE), u("label", K_WIDE)
    h = 96
    cx, cy = 58.0, 48.0
    r_out, r_in = 23.5, 9.8
    verts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        r = r_out if i % 2 == 0 else r_in
        verts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))

    facets = ""
    for i in range(10):
        x1, y1 = verts[i]
        x2, y2 = verts[(i + 1) % 10]
        tri = f"{cx:.2f},{cy:.2f} {x1:.2f},{y1:.2f} {x2:.2f},{y2:.2f}"
        facets += f'  <polygon points="{tri}" fill="#ff0000"/>\n'
        if i % 2 == 1:
            facets += f'  <polygon points="{tri}" fill="#000000" opacity="0.34"/>\n'
    star_outline = " ".join(f"{x:.2f},{y:.2f}" for x, y in verts)

    def mini_star(mx: float, my: float, ro: float = 4.2, ri: float = 1.6) -> str:
        pts = []
        for k in range(8):
            a = math.radians(-90 + k * 45)
            rk = ro if k % 2 == 0 else ri
            pts.append(f"{mx + rk * math.cos(a):.2f},{my + rk * math.sin(a):.2f}")
        return " ".join(pts)

    body = (
        "  <defs>\n"
        f'    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="{h}" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.05"/>'
        '<stop offset="0.65" stop-color="#ffffff" stop-opacity="0"/></linearGradient>\n'
        f'    <radialGradient id="star-aura" cx="{cx:.1f}" cy="{cy:.1f}" r="34" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="#ff0000" stop-opacity="0.32"/>'
        '<stop offset="0.65" stop-color="#ff0000" stop-opacity="0.08"/>'
        '<stop offset="1" stop-color="#ff0000" stop-opacity="0"/></radialGradient>\n'
        "  </defs>\n"
        + f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="#0c0507" {RED}/>\n'
        + f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="url(#sheen)"/>\n'
        + f'  <rect x="1" y="1" width="4" height="{h - 2}" rx="2" fill="#ff0000"/>\n'
        + '  <rect x="18" y="12" width="80" height="72" rx="4" fill="#000000" stroke="#ff0000" stroke-opacity="0.55" stroke-width="1"/>\n'
        + '  <rect x="22" y="16" width="72" height="64" rx="2" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1"/>\n'
        + f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="34" fill="url(#star-aura)"/>\n'
        + facets
        + f'  <polygon points="{star_outline}" fill="none" stroke="#ff0000" stroke-opacity="0.9" stroke-width="0.6"/>\n'
        + f'  <polygon points="{mini_star(29.5, 48.0)}" fill="#ff0000" opacity="0.75"/>\n'
        + f'  <polygon points="{mini_star(86.5, 48.0)}" fill="#ff0000" opacity="0.75"/>\n'
    )
    tx = 116
    sub = "Bookmark or star the router and every module from a single GitHub list."
    body += t.run(tx, 27, lb, "GITHUB STAR LIST", "#ff0000", "700")
    x_meta = tx + width("GITHUB STAR LIST", lb) + 10
    body += t.run(x_meta, 27, lb, "// github.com/stars/avalonreset/lists/cto-legends", "#a1a1aa", "400")
    body += t.run(tx, 52, hd, "The complete cto-legends collection on one page", "#ffffff", "700")
    body += t.run(tx, 74, bd, sub, "#d4d4d8", "400")

    btn_w = 216
    btn_x = 868 - btn_w
    assert tx + width(sub, bd) + 20 <= btn_x, "Shrine subline collides with button"
    body += f'  <rect x="{btn_x}" y="29" width="{btn_w}" height="38" rx="3" fill="#000000" {RED}/>\n'
    body += button(t, btn_x + btn_w / 2, 52.5, "#ffffff", 'OPEN GITHUB LIST <tspan fill="#ff0000">↗</tspan>', lb, "700")

    (CARDS_DIR / "slot-collection-star-shrine.svg").write_text(svg(f"0 0 886 {h}", body, t), encoding="utf-8")


def render_slot_7() -> None:
    """Slot 7: Closing message desk CTA card ('Message Avalon Reset')."""
    t = Typesetter()
    ti, bd, lb = u("title", K_WIDE), u("body", K_WIDE), u("label", K_WIDE)
    h = 68
    body = (
        f'  <rect x="1" y="1" width="884" height="{h - 2}" rx="4" fill="#0c0507" {RED}/>\n'
        f'  <rect x="1" y="1" width="4" height="{h - 2}" rx="2" fill="#ff0000"/>\n'
    )
    body += t.run(22, 28, ti, "Want this way of working applied to your own stack?", "#ffffff", "700")
    body += t.run(22, 48, bd, "Message Avalon Reset", "#ff0000", "700")
    x_note = 22 + width("Message Avalon Reset", bd) + 10
    body += t.run(x_note, 48, lb, "// async message desk at cto-legends.com/dm", "#a1a1aa", "400")

    btn_w = 228
    btn_x = 868 - btn_w
    body += f'  <rect x="{btn_x}" y="18" width="{btn_w}" height="32" rx="3" fill="#000000" {RED}/>\n'
    body += button(t, btn_x + btn_w / 2, 38.5, "#ffffff", 'MESSAGE AVALON RESET <tspan fill="#ff0000">↗</tspan>', lb, "700")

    (CARDS_DIR / "slot-7-message-avalon-reset.svg").write_text(svg(f"0 0 886 {h}", body, t), encoding="utf-8")


def validate() -> None:
    expected = [
        "slot-1-agent-handoff.svg",
        "slot-2-three-pillars.svg",
        "slot-3-plain-english-chains.svg",
        "slot-4-repo-intelligence.svg",
        "slot-5-generic-vs-github.svg",
        "slot-7-message-avalon-reset.svg",
        "slot-collection-star-shrine.svg",
    ]
    svgs = sorted(CARDS_DIR.glob("*.svg"))
    names = [p.name for p in svgs]
    assert names == expected, f"Expected {len(expected)} SVGs {expected}, found {names}"
    allowed_hex = {
        "#000000", "#ffffff", "#ff0000",
        "#e4e4e7", "#d4d4d8", "#a1a1aa", "#8b8b94", "#52525b",
        "#090a0e", "#0c0507",
    }
    for p in svgs:
        raw = p.read_bytes().replace(b"\r\n", b"\n")
        p.write_bytes(raw)
        s = raw.decode("utf-8")
        assert "\u2014" not in s and "\u2013" not in s, f"Dash found in {p.name}"
        assert "<text" not in s, f"Live <text> element found in {p.name}; all text must be outlined"
        ET.fromstring(s)
        colors = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}", s)}
        unexpected = colors - allowed_hex
        assert not unexpected, f"Unexpected color in {p.name}: {unexpected}"


def render_previews(preview_dir: Path) -> None:
    import fitz

    preview_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted(CARDS_DIR.glob("*.svg")):
        s = p.read_text(encoding="utf-8")
        m = re.search(r'viewBox="0 0 (\d+) (\d+)"', s)
        if m:
            w, h = m.group(1), m.group(2)
            s = s.replace('width="100%"', f'width="{w}" height="{h}"')
        doc = fitz.open(stream=s.encode("utf-8"), filetype="svg")
        pdf_doc = fitz.open("pdf", doc.convert_to_pdf())
        pdf_doc[0].get_pixmap(dpi=192).save(str(preview_dir / f"{p.stem}.png"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Render outlined Legends Font SVG cards (rev r1) for legends-github.")
    ap.add_argument("--preview-dir", type=Path, help="Optional directory to render 192 DPI PNG previews")
    args = ap.parse_args()
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    render_slot_1()
    render_slot_2()
    render_slot_3()
    render_slot_4()
    render_slot_5()
    render_slot_shrine()
    render_slot_7()
    validate()
    if args.preview_dir:
        render_previews(args.preview_dir)
    print(f"Rendered and validated 7 SVG cards in {CARDS_DIR.relative_to(ROOT)} (font={FONT}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
