#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成个人主页的顶部 / 底部横幅（原创设计，不依赖 capsule-render）。

配色走「墨 + 朱砂 + 金」，和主站的「宣纸墨韵」呼应，也和别人的紫青渐变区分开。

产出:
  assets/banner-top.svg     (1200x230)
  assets/banner-bottom.svg  (1200x140)

用法: python tools/make_banner_svg.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "assets"
OUT.mkdir(parents=True, exist_ok=True)

FONT = ("'Segoe UI','Microsoft YaHei','PingFang SC','Noto Sans SC',"
        "-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif")

INK0 = "#0A0A0D"
INK1 = "#150F12"
INK2 = "#2A1512"
VERMILION = "#D9482F"
VERMILION_LIGHT = "#F0664A"
GOLD = "#E8B04B"
PAPER = "#F5EFE6"
MUTED = "#8A8F98"


def particles(seed: int, count: int, width: int, height: int) -> str:
    """一批缓慢上浮的墨点，确定性伪随机，避免每次生成都不一样。"""
    out = []
    for i in range(count):
        x = ((seed * 37 + i * 149) % width)
        r = 1.2 + ((seed + i * 7) % 5) * 0.55
        dur = 9 + ((seed + i * 13) % 9)
        delay = -((i * 1.7) % dur)
        y0 = height + 12
        y1 = -14
        op = 0.10 + ((i * 17) % 7) * 0.045
        color = GOLD if i % 3 else VERMILION_LIGHT
        out.append(
            f'<circle cx="{x}" cy="{y0}" r="{r:.1f}" fill="{color}" opacity="{op:.2f}">'
            f'<animate attributeName="cy" values="{y0};{y1}" dur="{dur}s" '
            f'begin="{delay:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;{op:.2f};0" dur="{dur}s" '
            f'begin="{delay:.1f}s" repeatCount="indefinite"/></circle>'
        )
    return "".join(out)


# ---------------------------------------------------------------- 顶部横幅
W, H = 1200, 230
top = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="taboo-hacker">',
    "<defs>",
    '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
    f'<stop offset="0" stop-color="{INK0}"/><stop offset="0.55" stop-color="{INK1}"/>'
    f'<stop offset="1" stop-color="{INK2}"/></linearGradient>',
    '<radialGradient id="glow" cx="0.5" cy="0.42" r="0.62">'
    f'<stop offset="0" stop-color="{VERMILION}" stop-opacity="0.30"/>'
    f'<stop offset="1" stop-color="{VERMILION}" stop-opacity="0"/></radialGradient>',
    '<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">'
    f'<stop offset="0" stop-color="{VERMILION}" stop-opacity="0"/>'
    f'<stop offset="0.35" stop-color="{VERMILION}"/>'
    f'<stop offset="0.65" stop-color="{GOLD}"/>'
    f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>',
    '<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">'
    f'<stop offset="0" stop-color="{VERMILION}" stop-opacity="0.15"/>'
    f'<stop offset="0.5" stop-color="{GOLD}"/>'
    f'<stop offset="1" stop-color="{VERMILION}" stop-opacity="0.15"/></linearGradient>',
    '<linearGradient id="title" x1="0" y1="0" x2="1" y2="0">'
    f'<stop offset="0" stop-color="{PAPER}"/><stop offset="0.55" stop-color="{PAPER}"/>'
    f'<stop offset="1" stop-color="{GOLD}"/></linearGradient>',
    "</defs>",
    f'<rect width="{W}" height="{H}" fill="url(#bg)"/>',
    f'<rect width="{W}" height="{H}" fill="url(#glow)"/>',
    f'<rect x="0" y="0" width="{W}" height="2.5" fill="url(#edge)"/>',
    # 墨点
    f'<g>{particles(3, 16, W, H)}</g>',
    # 主标题
    f'<text x="{W/2}" y="116" text-anchor="middle" font-family="{FONT}" font-size="66" '
    f'font-weight="700" letter-spacing="3" fill="url(#title)">taboo-hacker</text>',
    # 毛笔笔触（描边生长动画）
    f'<path d="M462 140 C 528 132, 596 148, 660 138 C 700 132, 726 140, 744 136" '
    f'stroke="url(#rule)" stroke-width="3.2" fill="none" stroke-linecap="round" pathLength="1" '
    f'stroke-dasharray="1" stroke-dashoffset="1">'
    f'<animate attributeName="stroke-dashoffset" values="1;0;0;1" keyTimes="0;0.16;0.92;1" '
    f'dur="7.5s" repeatCount="indefinite"/></path>',
    # 副标题
    f'<text x="{W/2}" y="180" text-anchor="middle" font-family="{FONT}" font-size="19" '
    f'letter-spacing="2" fill="{MUTED}">陆逸昊 · AI 应用开发者</text>',
    "</svg>",
]
(OUT / "banner-top.svg").write_text("".join(top), encoding="utf-8")

# ---------------------------------------------------------------- 底部横幅
W2, H2 = 1200, 140
wave = " ".join(
    f"{'M' if x == 0 else 'L'}{x} {28 + 9 * math.sin(x / 95.0):.1f}"
    for x in range(0, W2 + 1, 20)
)
bottom = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}" '
    f'role="img" aria-label="">',
    "<defs>",
    '<linearGradient id="bg2" x1="0" y1="1" x2="1" y2="0">'
    f'<stop offset="0" stop-color="{INK2}"/><stop offset="0.45" stop-color="{INK1}"/>'
    f'<stop offset="1" stop-color="{INK0}"/></linearGradient>',
    '<linearGradient id="edge2" x1="0" y1="0" x2="1" y2="0">'
    f'<stop offset="0" stop-color="{GOLD}" stop-opacity="0.15"/>'
    f'<stop offset="0.5" stop-color="{VERMILION}"/>'
    f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0.15"/></linearGradient>',
    '<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
    f'<stop offset="0" stop-color="{GOLD}" stop-opacity="0"/>'
    f'<stop offset="0.5" stop-color="{GOLD}" stop-opacity="0.75"/>'
    f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>',
    "</defs>",
    f'<rect width="{W2}" height="{H2}" fill="url(#bg2)"/>',
    f'<path d="{wave} L{W2} {H2} L0 {H2} Z" fill="{INK0}" opacity="0.85"/>',
    f'<rect x="0" y="0" width="{W2}" height="2" fill="url(#edge2)"/>',
    f'<rect x="-160" y="0" width="160" height="2.5" fill="url(#sweep)">'
    f'<animate attributeName="x" values="-160;{W2}" dur="6.5s" repeatCount="indefinite"/></rect>',
    f'<g>{particles(11, 10, W2, H2)}</g>',
    f'<circle cx="{W2/2}" cy="{H2*0.62:.0f}" r="3.4" fill="{VERMILION}">'
    f'<animate attributeName="opacity" values="0.25;1;0.25" dur="3s" repeatCount="indefinite"/>'
    f'</circle>',
    "</svg>",
]
(OUT / "banner-bottom.svg").write_text("".join(bottom), encoding="utf-8")

print(f"banner-top.svg    -> {OUT/'banner-top.svg'}")
print(f"banner-bottom.svg -> {OUT/'banner-bottom.svg'}")
