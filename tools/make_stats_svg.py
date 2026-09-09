#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 GitHub 公开 REST API 生成一张自定义的「数据总览」SVG 卡片。

为什么不直接用 github-readme-stats？
  —— Actions 里的 GITHUB_TOKEN 是安装令牌，读不到用户级 GraphQL 数据，
     第三方卡片会直接渲染成 "Something went wrong"。
     这里只用公开 REST 端点，稳定且配色可控。

用法:
  GITHUB_TOKEN=xxx USERNAME=taboo-hacker python3 tools/make_stats_svg.py
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

USER = os.environ.get("USERNAME", "taboo-hacker")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = Path(__file__).resolve().parents[1] / "assets" / "stats.svg"

FONT = ("'Segoe UI',Ubuntu,'Microsoft YaHei','PingFang SC','Noto Sans SC',"
        "-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif")

W, H = 460, 208
PAD = 22


def gh(path: str):
    """返回 (json, headers)。失败抛异常。"""
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "dsh-profile-stats",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r), dict(r.headers)


def safe(fn, default=None):
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 - 统计失败不该让工作流挂掉
        print(f"  ! {exc}", file=sys.stderr)
        return default


# ---- 数据 ------------------------------------------------------------------
user = safe(lambda: gh(f"/users/{USER}")[0], {}) or {}
repos = safe(lambda: gh(f"/users/{USER}/repos?per_page=100&type=owner")[0], []) or []
repos = [r for r in repos if not r.get("fork")]

total_stars = sum(r.get("stargazers_count", 0) for r in repos)
total_forks = sum(r.get("forks_count", 0) for r in repos)


def commits_in(full_name: str) -> int:
    _, headers = gh(f"/repos/{full_name}/commits?author={USER}&per_page=1")
    link = headers.get("Link") or headers.get("link") or ""
    m = re.search(r'[?&]page=(\d+)>;\s*rel="last"', link)
    if m:
        return int(m.group(1))
    # 没有 Link 头说明只有 0/1 条
    data, _ = gh(f"/repos/{full_name}/commits?author={USER}&per_page=1")
    return len(data)


total_commits = 0
for r in repos:
    n = safe(lambda r=r: commits_in(r["full_name"]), 0)
    total_commits += n or 0

prs = safe(lambda: gh(f"/search/issues?q=author:{USER}+type:pr&per_page=1")[0]["total_count"], None)
issues = safe(lambda: gh(f"/search/issues?q=author:{USER}+type:issue&per_page=1")[0]["total_count"], None)


def fmt(v):
    return "—" if v is None else f"{v:,}"


STATS = [
    (fmt(len(repos)), "公开仓库"),
    (fmt(total_stars), "获得星标"),
    (fmt(total_commits), "公开提交"),
    (fmt(prs), "拉取请求"),
    (fmt(issues), "议题"),
    (fmt(user.get("followers")), "关注者"),
]

updated = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M (UTC+8)")

# ---- 画卡片 ----------------------------------------------------------------
col_w = (W - PAD * 2) / 3
rows_y = (86, 142)      # 数字基线
label_dy = 20           # 标签相对数字的偏移

p = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="GitHub 数据总览">',
    "<defs>",
    '<linearGradient id="line" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#D9482F"/><stop offset="1" stop-color="#E8B04B"/></linearGradient>',
    '<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#E8B04B" stop-opacity="0"/>'
    '<stop offset="0.5" stop-color="#E8B04B" stop-opacity="0.6"/>'
    '<stop offset="1" stop-color="#E8B04B" stop-opacity="0"/></linearGradient>',
    "</defs>",
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="#0A0A0D" stroke="#2A1F1F"/>',
    f'<rect x="{PAD}" y="1" width="{W-PAD*2}" height="2" rx="1" fill="url(#line)" opacity="0.85"/>',
    f'<rect x="-140" y="1" width="140" height="2.5" fill="url(#sweep)">'
    f'<animate attributeName="x" values="-140;{W}" dur="6s" repeatCount="indefinite"/></rect>',
    f'<text x="{PAD}" y="36" font-family="{FONT}" font-size="16" font-weight="700" fill="#E8B04B">'
    f'GitHub 数据总览</text>',
    f'<text x="{W-PAD}" y="36" text-anchor="end" font-family="{FONT}" font-size="12" fill="#8A8F98">'
    f'@{USER}</text>',
    f'<line x1="{PAD}" y1="50" x2="{W-PAD}" y2="50" stroke="#2A1F1F"/>',
]

for i, (value, label) in enumerate(STATS):
    col, row = i % 3, i // 3
    cx = PAD + col * col_w + col_w / 2
    y = rows_y[row]
    p.append(
        f'<text x="{cx:.1f}" y="{y}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="24" font-weight="700" fill="#F5EFE6">{value}</text>'
    )
    p.append(
        f'<text x="{cx:.1f}" y="{y + label_dy}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="11.5" fill="#8A8F98">{label}</text>'
    )

p.append(
    f'<text x="{PAD}" y="{H-12}" font-family="{FONT}" font-size="10" fill="#5A5F66">'
    f'更新于 {updated} · 数据来自 GitHub 公开接口</text>'
)
p.append("</svg>")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("".join(p), encoding="utf-8")
print(f"stats.svg -> {OUT}")
print(f"  repos={len(repos)} stars={total_stars} commits={total_commits} prs={prs} issues={issues}")
