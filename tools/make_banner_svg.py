#!/usr/bin/env python3
"""Generate self-contained profile artwork. Run from any working directory."""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parents[1] / "assets"
FONT = "'Segoe UI','Noto Sans CJK SC','Microsoft YaHei',sans-serif"
MONO = "'DejaVu Sans Mono',Consolas,monospace"


def text(x, y, value, size=18, color="#F5EFE6", weight=400, mono=False):
    return (f'<text x="{x}" y="{y}" font-family="{MONO if mono else FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>')


def frame(width, height, label, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">
<title>{escape(label)}</title>
<defs>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#0A0A0D"/><stop offset="1" stop-color="#191416"/></linearGradient>
  <linearGradient id="gold"><stop stop-color="#F3D69C"/><stop offset="1" stop-color="#B88436"/></linearGradient>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#F3D69C" stroke-opacity=".045"/></pattern>
</defs>
<rect width="{width}" height="{height}" rx="18" fill="url(#bg)"/>
<rect width="{width}" height="{height}" rx="18" fill="url(#grid)"/>
<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="18" fill="none" stroke="#3B3025"/>
{body}</svg>'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hero = '<rect x="48" y="48" width="38" height="3" fill="url(#gold)"/>'
    hero += text(100, 55, "INDEPENDENT DEVELOPER / PERSONAL ARCHIVE", 13, "#CBA56D", mono=True)
    hero += text(48, 139, "TABOO", 76, weight=750)
    hero += text(48, 218, "HACKER_", 76, "#E8B04B", 750)
    hero += text(52, 265, "BUILD SYSTEMS. SHIP IDEAS.", 19, "#D7C8B4", mono=True)
    hero += text(52, 304, "LU YIHAO / AI APPLICATIONS / FULL STACK / AUTOMATION", 15, "#AAA29A", mono=True)
    hero += '<path d="M52 338H1148" stroke="#3B3025"/>'
    hero += text(52, 368, "TURN IDEAS INTO EVERYDAY TOOLS.", 16, "#D7C8B4", mono=True)
    hero += text(909, 368, "ALWAYS BUILDING", 15, "#E8B04B", mono=True)
    hero += '<g fill="none"><circle cx="960" cy="180" r="113" stroke="#655032"/><circle cx="960" cy="180" r="86" stroke="#3B3025" stroke-dasharray="3 9"/><path d="M808 180H1112M960 28V332" stroke="#3B3025"/><path d="M870 113L960 61L1050 113V247L960 299L870 247Z" stroke="url(#gold)" stroke-width="1.5"/></g>'
    hero += text(904, 202, "TH", 63, "#F3D69C", 600, mono=True)
    hero += '<circle cx="1073" cy="180" r="5" fill="#E8B04B"/><circle cx="960" cy="67" r="4" fill="#D9482F"/>'
    (OUT / "banner-top.svg").write_text(frame(1200, 400, "TABOO HACKER — 陆逸昊，AI 应用开发者。把想法写成代码，把代码做成日常。", hero), encoding="utf-8")
    bottom = text(48, 58, "TH /", 27, "#E8B04B", 700, mono=True)
    bottom += text(170, 56, "MAKE IT WORK. MAKE IT BETTER.", 23, "#F5EFE6", 600, mono=True)
    bottom += text(170, 89, "IDEAS EVOLVE. THE COMMITS REMAIN.", 15, "#AAA29A", mono=True)
    (OUT / "banner-bottom.svg").write_text(frame(1200, 130, "MAKE IT WORK. MAKE IT BETTER.", bottom), encoding="utf-8")


if __name__ == "__main__":
    main()
