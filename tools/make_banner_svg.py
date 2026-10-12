#!/usr/bin/env python3
"""Generate the profile's compact, theme-aware masthead using only stdlib."""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "assets"
FONT = "'Segoe UI','Noto Sans CJK SC','Microsoft YaHei',sans-serif"
THEMES = {
    "dark": {"ink": "#E6EDF3", "muted": "#9DA7B3", "accent": "#65CDBB", "line": "#30363D"},
    "light": {"ink": "#1F2328", "muted": "#59636E", "accent": "#167D70", "line": "#D1D9E0"},
}


def masthead(theme):
    """Transparent artwork blends into GitHub's native README background."""
    colors = THEMES[theme]
    title = "TABOO HACKER — 把日常里的小问题，做成顺手的工具。"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="228" viewBox="0 0 960 228" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">陆逸昊的个人开发记录。AI 应用、全栈开发与自动化。</desc>
  <g font-family="{FONT}">
    <path d="M2 19V43" stroke="{colors['accent']}" stroke-width="4"/>
    <text x="18" y="37" font-size="17" font-weight="600" letter-spacing="3" fill="{colors['muted']}">PERSONAL NOTES / 陆逸昊</text>
    <text x="0" y="110" font-size="64" font-weight="700" letter-spacing="-2" fill="{colors['ink']}">TABOO HACKER<tspan fill="{colors['accent']}">.</tspan></text>
    <text x="2" y="163" font-size="28" fill="{colors['muted']}">把日常里的小问题，做成顺手的工具。</text>
  </g>
  <path d="M0 215H960" stroke="{colors['line']}"/>
  <path d="M0 215H64" stroke="{colors['accent']}" stroke-width="3"/>
</svg>
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        filename = "banner-top.svg" if theme == "dark" else "banner-top-light.svg"
        (OUT / filename).write_text(masthead(theme), encoding="utf-8")


if __name__ == "__main__":
    main()
