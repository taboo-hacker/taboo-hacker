#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 GitHub 个人主页用的自定义动画 SVG。

产出:
  assets/terminal.svg  —— 会「逐字打字」的终端卡片
  assets/divider.svg   —— 会「流光」的渐变分隔线

用法: python tools/make_terminal_svg.py
"""
import os
from pathlib import Path

# STATIC=1 时输出「已打完」的静态帧，方便本地预览 / 转 PNG 检查排版
STATIC = os.environ.get("STATIC") == "1"

OUT = Path(__file__).resolve().parents[1] / "assets"
OUT.mkdir(parents=True, exist_ok=True)

FONT = ("'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,"
        "Consolas,'Microsoft YaHei','PingFang SC','Noto Sans SC',monospace")

PANEL_W, PANEL_H = 620, 434
LEFT = 28
LINE_H = 26
FIRST_Y = 116
FS = 15.0

C = {
    "prompt": "#D9482F",
    "cmd": "#F5EFE6",
    "out": "#9AA0A6",
    "key": "#E8B04B",
    "str": "#F0664A",
    "punc": "#5A5F66",
    "num": "#E8B04B",
    "ok": "#E8B04B",
    "dim": "#6A6F76",
    "name": "#F5EFE6",
}

# (文本片段, 颜色)
LINES = [
    [("$ ", C["prompt"]), ("whoami", C["cmd"])],
    [("陆逸昊", C["name"]), ("  /  taboo-hacker", C["out"])],
    [("$ ", C["prompt"]), ("cat ~/.profile", C["cmd"])],
    [("{", C["punc"])],
    [('  "role"', C["key"]), (":  ", C["punc"]), ('"AI 应用开发者"', C["str"]), (",", C["punc"])],
    [('  "school"', C["key"]), (":  ", C["punc"]), ('"衢州职业技术学院 · 人工智能技术应用"', C["str"]), (",", C["punc"])],
    [('  "stack"', C["key"]), (":  ", C["punc"]), ('["Python", "TypeScript", "Go", "Vue 3", "FastAPI"]', C["str"]), (",", C["punc"])],
    [('  "belief"', C["key"]), (":  ", C["punc"]), ('"AI 不是替代思考，而是放大创造"', C["str"]), (",", C["punc"])],
    [('  "status"', C["key"]), (":  ", C["punc"]), ('"building · 持续迭代中"', C["str"])],
    [("}", C["punc"])],
    [("$ ", C["prompt"]), ('git commit -m "keep going"', C["cmd"])],
    [("[main 7c3aed] ", C["dim"]), ("保持热爱，持续交付", C["ok"]), ("\u2588", C["ok"])],
]


def adv(ch: str) -> float:
    """粗略等宽字宽估算: CJK 记 1em, 其余记 0.6em。"""
    return FS * (1.0 if ord(ch) > 0x2E7F else 0.6)


def line_width(segs) -> float:
    return sum(adv(c) for text, _ in segs for c in text)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---- 时间轴 ----------------------------------------------------------------
SPEED = 430.0          # px / s
GAP = 0.24             # 每行之间的停顿
HOLD = 4.2             # 全部打完后的停留
MIN_DUR = 0.30

timeline = []
t = 0.55
for segs in LINES:
    dur = max(MIN_DUR, line_width(segs) / SPEED)
    timeline.append((t, t + dur))
    t += dur + GAP
DUR = round(t + HOLD, 2)


def frac(sec: float) -> float:
    return round(sec / DUR, 4)


parts = []
parts.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{PANEL_W}" height="{PANEL_H}" '
    f'viewBox="0 0 {PANEL_W} {PANEL_H}" role="img" '
    f'aria-label="陆逸昊的终端名片">'
)
parts.append("<defs>")
parts.append(
    '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#0A0A0D"/><stop offset="0.55" stop-color="#120F11"/>'
    '<stop offset="1" stop-color="#1A1210"/></linearGradient>'
)
parts.append(
    '<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#D9482F"/><stop offset="0.5" stop-color="#E8B04B"/>'
    '<stop offset="1" stop-color="#D9482F"/></linearGradient>'
)
parts.append(
    '<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#E8B04B" stop-opacity="0"/>'
    '<stop offset="0.5" stop-color="#E8B04B" stop-opacity="0.55"/>'
    '<stop offset="1" stop-color="#E8B04B" stop-opacity="0"/></linearGradient>'
)
parts.append(
    '<radialGradient id="glow" cx="0.12" cy="0.0" r="0.9">'
    '<stop offset="0" stop-color="#D9482F" stop-opacity="0.30"/>'
    '<stop offset="1" stop-color="#D9482F" stop-opacity="0"/></radialGradient>'
)
parts.append(
    '<filter id="soft" x="-30%" y="-30%" width="160%" height="160%">'
    '<feGaussianBlur stdDeviation="6"/></filter>'
)
parts.append("</defs>")

# 面板
parts.append(f'<rect x="0.5" y="0.5" width="{PANEL_W-1}" height="{PANEL_H-1}" rx="16" fill="url(#bg)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{PANEL_W-1}" height="{PANEL_H-1}" rx="16" fill="url(#glow)"/>')
parts.append(f'<rect x="0.5" y="0.5" width="{PANEL_W-1}" height="{PANEL_H-1}" rx="16" fill="none" stroke="#2A1F1F"/>')

# 顶部高光扫过
parts.append(
    f'<rect x="-180" y="1" width="180" height="2.5" fill="url(#sweep)">'
    f'<animate attributeName="x" values="-180;{PANEL_W}" dur="5.5s" repeatCount="indefinite"/>'
    f"</rect>"
)
# 顶部渐变细线
parts.append(f'<rect x="16" y="1" width="{PANEL_W-32}" height="2" rx="1" fill="url(#edge)" opacity="0.85"/>')

# 标题栏
parts.append(f'<line x1="0" y1="48" x2="{PANEL_W}" y2="48" stroke="#2A1F1F"/>')
for i, color in enumerate(("#D9482F", "#E8B04B", "#F0664A")):
    parts.append(f'<circle cx="{30 + i*22}" cy="25" r="5.5" fill="{color}" opacity="0.9"/>')
parts.append(
    f'<text x="{PANEL_W/2}" y="30" text-anchor="middle" font-family="{FONT}" '
    f'font-size="12.5" fill="#6A6F76">陆逸昊 · ~/profile</text>'
)

# 每一行
for idx, (segs, (t0, t1)) in enumerate(zip(LINES, timeline)):
    y = FIRST_Y + idx * LINE_H
    w = line_width(segs) + 12
    k0, k1 = frac(t0), frac(t1)

    parts.append(f'<clipPath id="c{idx}"><rect x="{LEFT}" y="{y-16}" width="{w if STATIC else 0}" height="24">')
    if not STATIC:
        parts.append(
            f'<animate attributeName="width" values="0;0;{w:.1f};{w:.1f}" '
            f'keyTimes="0;{k0};{k1};1" dur="{DUR}s" repeatCount="indefinite"/>'
        )
    parts.append("</rect></clipPath>")

    parts.append(f'<g clip-path="url(#c{idx})">')
    # 只给 <text> 设起始 x，tspan 依次自然排版。
    # 之前给每个 tspan 都算绝对 x，估算字宽和浏览器实际字宽（Consolas 0.55em vs 估算 0.6em）
    # 有偏差，长行会累积出几格空隙 —— 现在交给浏览器排版，字体无关。
    parts.append(f'<text x="{LEFT}" y="{y}" font-family="{FONT}" font-size="{FS}" xml:space="preserve">')
    last_line = idx == len(LINES) - 1
    for j, (text, color) in enumerate(segs):
        if last_line and j == len(segs) - 1 and not STATIC:
            # 末尾的方块光标：跟着文字走，天然对齐，不用算字宽
            parts.append(
                f'<tspan fill="{color}">{esc(text)}'
                f'<animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/>'
                f"</tspan>"
            )
        else:
            parts.append(f'<tspan fill="{color}">{esc(text)}</tspan>')
    parts.append("</text></g>")

# 底部呼吸光点
parts.append(
    f'<circle cx="{PANEL_W-34}" cy="{PANEL_H-24}" r="3.5" fill="#E8B04B">'
    f'<animate attributeName="opacity" values="0.25;1;0.25" dur="2.4s" repeatCount="indefinite"/>'
    f"</circle>"
)
parts.append(
    f'<text x="{PANEL_W-48}" y="{PANEL_H-20}" text-anchor="end" font-family="{FONT}" '
    f'font-size="11.5" fill="#5A5048">在线</text>'
)

parts.append("</svg>")
(OUT / "terminal.svg").write_text("".join(parts), encoding="utf-8")


# ---- 分隔线 ---------------------------------------------------------------
DIV_W, DIV_H = 1000, 14
div = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{DIV_W}" height="{DIV_H}" viewBox="0 0 {DIV_W} {DIV_H}">',
    "<defs>",
    '<linearGradient id="d" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#D9482F" stop-opacity="0"/>'
    '<stop offset="0.5" stop-color="#E8B04B" stop-opacity="0.9"/>'
    '<stop offset="1" stop-color="#D9482F" stop-opacity="0"/></linearGradient>',
    '<linearGradient id="s" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#E8B04B" stop-opacity="0"/>'
    '<stop offset="0.5" stop-color="#FFF7E6" stop-opacity="1"/>'
    '<stop offset="1" stop-color="#E8B04B" stop-opacity="0"/></linearGradient>',
    "</defs>",
    f'<rect x="0" y="6" width="{DIV_W}" height="1.6" fill="url(#d)"/>',
    f'<rect x="-140" y="4.6" width="140" height="4.4" rx="2.2" fill="url(#s)">'
    f'<animate attributeName="x" values="-140;{DIV_W}" dur="4.2s" repeatCount="indefinite"/>'
    f"</rect>",
    "</svg>",
]
(OUT / "divider.svg").write_text("".join(div), encoding="utf-8")

print(f"terminal.svg -> {OUT/'terminal.svg'}  (loop {DUR}s, {len(LINES)} lines)")
print(f"divider.svg  -> {OUT/'divider.svg'}")
