#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 GitHub 公开 REST API 生成「用得最多的编程语言」卡片（全中文标签）。

为什么不用 github-readme-stats 的 top-langs？
  —— 它的标题写死成 "Most Used Languages"，改不动；这里自己画，标题、单位、脚注
     全部是中文，配色也和统计卡保持一致。

用法:
  GITHUB_TOKEN=xxx USERNAME=taboo-hacker python3 tools/make_langs_svg.py
"""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

USER = os.environ.get("USERNAME", "taboo-hacker")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = Path(__file__).resolve().parents[1] / "assets" / "top-langs.svg"

FONT = ("'Segoe UI',Ubuntu,'Microsoft YaHei','PingFang SC','Noto Sans SC',"
        "-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif")

W, H = 400, 208
PAD = 22
TOP_N = 6

# GitHub linguist 常用配色
COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178C6", "JavaScript": "#F1E05A",
    "Go": "#00ADD8", "HTML": "#E34F26", "CSS": "#563D7C", "Vue": "#41B883",
    "C": "#555555", "C++": "#F34B7D", "C#": "#178600", "Java": "#B07219",
    "Shell": "#89E051", "Rust": "#DEA584", "PHP": "#4F5D95", "Ruby": "#701516",
    "Kotlin": "#A97BFF", "Swift": "#F05138", "Dart": "#00B4AB", "SCSS": "#C6538C",
    "Less": "#1D365D", "Dockerfile": "#384D54", "Makefile": "#427819",
    "Batchfile": "#C1F12E", "PowerShell": "#012456", "Lua": "#000080",
    "Jupyter Notebook": "#DA5B0B", "Cython": "#FEDF5B", "Assembly": "#6E4C13",
    "Objective-C": "#438EFF", "Vim Script": "#199F4B", "EJS": "#A91E50",
    "Handlebars": "#F7931E", "Svelte": "#FF3E00", "Roff": "#ECDEBE",
}
FALLBACK = ["#7C3AED", "#22D3EE", "#A855F7", "#06B6D4", "#8B5CF6", "#0EA5E9"]


def gh(path: str):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "dsh-profile-langs",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def safe(fn, default=None):
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001
        print(f"  ! {exc}", file=sys.stderr)
        return default


repos = safe(lambda: gh(f"/users/{USER}/repos?per_page=100&type=owner"), []) or []
repos = [r for r in repos if not r.get("fork")]

bytes_by_lang: dict[str, int] = {}
for r in repos:
    langs = safe(lambda r=r: gh(f"/repos/{r['full_name']}/languages"), {}) or {}
    for lang, n in langs.items():
        bytes_by_lang[lang] = bytes_by_lang.get(lang, 0) + int(n)

total = sum(bytes_by_lang.values()) or 1
top = sorted(bytes_by_lang.items(), key=lambda kv: kv[1], reverse=True)[:TOP_N]
if not top:
    top = [("暂无数据", 1)]
max_share = max(n for _, n in top)

updated = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M (UTC+8)")

# ---- 画卡片 ----------------------------------------------------------------
p = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="用得最多的编程语言">',
    "<defs>",
    '<linearGradient id="line" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#22D3EE"/><stop offset="1" stop-color="#7C3AED"/></linearGradient>',
    '<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#22D3EE" stop-opacity="0"/>'
    '<stop offset="0.5" stop-color="#22D3EE" stop-opacity="0.6"/>'
    '<stop offset="1" stop-color="#22D3EE" stop-opacity="0"/></linearGradient>',
    "</defs>",
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="#0D1117" stroke="#1E293B"/>',
    f'<rect x="{PAD}" y="1" width="{W-PAD*2}" height="2" rx="1" fill="url(#line)" opacity="0.85"/>',
    f'<rect x="-140" y="1" width="140" height="2.5" fill="url(#sweep)">'
    f'<animate attributeName="x" values="-140;{W}" dur="6s" repeatCount="indefinite"/></rect>',
    f'<text x="{PAD}" y="36" font-family="{FONT}" font-size="16" font-weight="700" fill="#22D3EE">'
    f'用得最多的编程语言</text>',
    f'<text x="{W-PAD}" y="36" text-anchor="end" font-family="{FONT}" font-size="12" fill="#64748B">'
    f'@{USER}</text>',
    f'<line x1="{PAD}" y1="50" x2="{W-PAD}" y2="50" stroke="#1E293B"/>',
]

BAR_X, BAR_W = 140, 190
ROWS = len(top)
SPACING = min(32.0, 110.0 / max(1, ROWS - 1))
Y0 = 70.0

for i, (lang, n) in enumerate(top):
    y = Y0 + i * SPACING
    share = n / total * 100
    color = COLORS.get(lang) or FALLBACK[i % len(FALLBACK)]
    filled = max(6.0, BAR_W * (n / max_share))
    p += [
        f'<circle cx="{PAD + 4}" cy="{y - 4}" r="4" fill="{color}"/>',
        f'<text x="{PAD + 14}" y="{y}" font-family="{FONT}" font-size="12" fill="#CBD5E1">{lang}</text>',
        f'<rect x="{BAR_X}" y="{y - 9.5}" width="{BAR_W}" height="7" rx="3.5" fill="#161B22"/>',
        f'<rect x="{BAR_X}" y="{y - 9.5}" width="{filled:.1f}" height="7" rx="3.5" fill="{color}"/>',
        f'<text x="{W - PAD}" y="{y}" text-anchor="end" font-family="{FONT}" font-size="11.5" '
        f'fill="#94A3B8">{share:.1f}%</text>',
    ]

p.append(
    f'<text x="{PAD}" y="{H-12}" font-family="{FONT}" font-size="10" fill="#475569">'
    f'统计 {len(repos)} 个仓库 · 按代码字节数计算 · 更新于 {updated}</text>'
)
p.append("</svg>")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("".join(p), encoding="utf-8")
print(f"top-langs.svg -> {OUT}")
print("  " + ", ".join(f"{k}={v}" for k, v in top))
