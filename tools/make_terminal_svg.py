#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 GitHub 个人主页用的自定义动画 SVG。

产出:
  assets/terminal.svg  —— 会「逐字打字」的终端卡片
  assets/divider.svg   —— 会「流光」的渐变分隔线

动画规则（模拟真实终端）:
  · 提示符 `$ ` 在敲命令之前就已经在那一行了，而且旁边有个闪烁光标在等
  · 隔一小会儿，命令才开始逐字敲出来（光标跟着走）
  · 命令的输出整块瞬间出现，就像命令真的跑完了一样
  · 输出结束后，下一行的 `$ ` 立刻出现，光标继续闪

用法:
  python tools/make_terminal_svg.py            # 正常（带动画）
  STATIC=1 python tools/make_terminal_svg.py   # 输出「全部打完」的静态帧
  STATIC_AT=4 python tools/make_terminal_svg.py  # 输出动画在 4 秒时刻的静态取样帧
"""
import os
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "assets"
OUT.mkdir(parents=True, exist_ok=True)

STATIC = os.environ.get("STATIC") == "1"
STATIC_AT = float(os.environ["STATIC_AT"]) if os.environ.get("STATIC_AT") else None

FONT = ("'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,"
        "Consolas,'Microsoft YaHei','PingFang SC','Noto Sans SC',monospace")

PANEL_W, PANEL_H = 620, 468
LEFT = 28
LINE_H = 26
FIRST_Y = 116
FS = 15.0
PROMPT = "$ "

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

# 行类型:
#   ("cmd", "命令文本")          —— 提示符先出现（带闪烁光标），再逐字敲命令
#   ("out", [(片段, 颜色), ...]) —— 输出，整块瞬间出现（连续多行会同时出现）
LINES = [
    ("cmd", "whoami"),
    ("out", [("陆逸昊", C["name"]), ("  /  taboo-hacker", C["out"])]),
    ("cmd", "cat ~/.profile"),
    ("out", [("{", C["punc"])]),
    ("out", [('  "role"', C["key"]), (":  ", C["punc"]), ('"AI 应用开发者"', C["str"]), (",", C["punc"])]),
    ("out", [('  "school"', C["key"]), (":  ", C["punc"]), ('"衢州职业技术学院 · 人工智能技术应用"', C["str"]), (",", C["punc"])]),
    ("out", [('  "stack"', C["key"]), (":  ", C["punc"]), ('["Python", "TypeScript", "Go", "Vue 3", "FastAPI"]', C["str"]), (",", C["punc"])]),
    ("out", [('  "belief"', C["key"]), (":  ", C["punc"]), ('"AI 不是替代思考，而是放大创造"', C["str"]), (",", C["punc"])]),
    ("out", [('  "status"', C["key"]), (":  ", C["punc"]), ('"building · 持续迭代中"', C["str"])]),
    ("out", [("}", C["punc"])]),
    ("cmd", 'git commit -m "keep going"'),
    ("out", [("[main 7c3aed] ", C["dim"]), ("保持热爱，持续交付", C["ok"])]),
    ("out", [("$ ", C["prompt"]), ("\u2588", C["ok"])]),
]


def adv(ch: str) -> float:
    """粗略等宽字宽估算: CJK 记 1em, 其余记 0.6em。"""
    return FS * (1.0 if ord(ch) > 0x2E7F else 0.6)


def text_width(s: str) -> float:
    return sum(adv(c) for c in s)


def segs_width(segs) -> float:
    return sum(text_width(t) for t, _ in segs)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


PROMPT_W = text_width(PROMPT)

# ---- 时间轴 ----------------------------------------------------------------
SPEED = 190.0          # 打字速度 px / s
PROMPT_PAUSE = 0.65    # 提示符出现后，隔多久开始敲命令
CMD_GAP = 0.30         # 命令敲完后，隔多久出输出
READ_BASE = 0.70       # 输出出现后的基础停留
READ_PER_LINE = 0.22   # 每多一行输出，多停一会儿
HOLD = 4.0             # 全部结束后的停留
MIN_DUR = 0.35

timeline = []          # 与 LINES 一一对应
t_prompt = 0.6         # 当前这行提示符出现的时刻
wait = PROMPT_PAUSE    # 提示符出现后等多久开始敲（输出越长，等得越久，方便看完）
t_end = t_prompt
i = 0
while i < len(LINES):
    kind = LINES[i][0]
    if kind == "cmd":
        cmd = LINES[i][1]
        cmd_w = text_width(cmd)
        dur = max(MIN_DUR, cmd_w / SPEED)
        t_type0 = t_prompt + wait
        t_type1 = t_type0 + dur
        timeline.append({
            "kind": "cmd",
            "t_prompt": t_prompt,
            "t_type0": t_type0,
            "t_type1": t_type1,
            "cmd_w": cmd_w,
        })
        appear = t_type1 + CMD_GAP      # 输出出现的时刻
        i += 1
        n = 0
        while i < len(LINES) and LINES[i][0] == "out":
            timeline.append({"kind": "out", "t0": appear, "segs": LINES[i][1]})
            n += 1
            i += 1
        # 关键：下一行的 `$ ` 和输出同时出现，光标在那儿等着，等你看完再敲下一条
        t_prompt = appear
        t_end = appear
        wait = (READ_BASE + READ_PER_LINE * n) if n else PROMPT_PAUSE
    else:
        timeline.append({"kind": "out", "t0": t_prompt, "segs": LINES[i][1]})
        t_end = t_prompt
        i += 1
DUR = round(t_end + HOLD, 2)


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
parts.append(f'<rect x="16" y="1" width="{PANEL_W-32}" height="2" rx="1" fill="url(#edge)" opacity="0.85"/>')

# 标题栏
parts.append(f'<line x1="0" y1="48" x2="{PANEL_W}" y2="48" stroke="#2A1F1F"/>')
for i, color in enumerate(("#D9482F", "#E8B04B", "#F0664A")):
    parts.append(f'<circle cx="{30 + i*22}" cy="25" r="5.5" fill="{color}" opacity="0.9"/>')
parts.append(
    f'<text x="{PANEL_W/2}" y="30" text-anchor="middle" font-family="{FONT}" '
    f'font-size="12.5" fill="#6A6F76">陆逸昊 · ~/profile</text>'
)


def gate(shown, kp: float) -> str:
    """输出 / 提示符的「瞬间出现」开关。shown=None 表示生成动画。"""
    if shown is None:
        return (
            f'<animate attributeName="opacity" values="0;1;1" keyTimes="0;{kp};1" '
            f'dur="{DUR}s" repeatCount="indefinite" calcMode="discrete"/>'
        )
    return ""


# 每一行
for idx, item in enumerate(timeline):
    y = FIRST_Y + idx * LINE_H

    if item["kind"] == "cmd":
        cmd = LINES[idx][1]
        cmd_w, cmd_x = item["cmd_w"], LEFT + PROMPT_W
        t_prompt, t_type0, t_type1 = item["t_prompt"], item["t_type0"], item["t_type1"]
        kp, k0, k1 = frac(t_prompt), frac(t_type0), frac(t_type1)
        wclip = cmd_w + 4

        # --- 提示符：敲命令之前就已经在那一行了 ---
        if STATIC or (STATIC_AT is not None and STATIC_AT >= t_prompt):
            prompt_shown = True
        elif STATIC_AT is not None:
            prompt_shown = False
        else:
            prompt_shown = None
        parts.append(f'<g opacity="{1 if prompt_shown else 0}">')
        parts.append(gate(prompt_shown, kp))
        parts.append(
            f'<text x="{LEFT}" y="{y}" font-family="{FONT}" font-size="{FS}" xml:space="preserve" '
            f'textLength="{PROMPT_W:.1f}" lengthAdjust="spacing">'
            f'<tspan fill="{C["prompt"]}">{esc(PROMPT)}</tspan></text></g>'
        )

        # --- 命令：逐字敲出来 ---
        if STATIC:
            prog = 1.0
        elif STATIC_AT is not None:
            prog = 0.0 if STATIC_AT <= t_type0 else (1.0 if STATIC_AT >= t_type1 else (STATIC_AT - t_type0) / (t_type1 - t_type0))
        else:
            prog = None

        parts.append(
            f'<clipPath id="c{idx}"><rect x="{cmd_x}" y="{y-16}" '
            f'width="{wclip * prog if prog is not None else 0:.1f}" height="24">'
        )
        if prog is None:
            parts.append(
                f'<animate attributeName="width" values="0;0;{wclip:.1f};{wclip:.1f}" '
                f'keyTimes="0;{k0};{k1};1" dur="{DUR}s" repeatCount="indefinite"/>'
            )
        parts.append("</rect></clipPath>")

        parts.append(f'<g clip-path="url(#c{idx})">')
        parts.append(
            f'<text x="{cmd_x}" y="{y}" font-family="{FONT}" font-size="{FS}" xml:space="preserve" '
            f'textLength="{cmd_w:.1f}" lengthAdjust="spacing">'
            f'<tspan fill="{C["cmd"]}">{esc(cmd)}</tspan></text></g>'
        )

        # --- 等待时的闪烁光标（提示符右边）---
        if prog is None:
            parts.append(
                f'<g opacity="0">'
                f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{kp};{k0}" '
                f'dur="{DUR}s" repeatCount="indefinite" calcMode="discrete"/>'
                f'<rect x="{cmd_x}" y="{y-13}" width="8.5" height="17" rx="1.5" fill="{C["ok"]}">'
                f'<animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/>'
                f"</rect></g>"
            )
        elif STATIC_AT is not None and t_prompt <= STATIC_AT < t_type0:
            parts.append(
                f'<rect x="{cmd_x}" y="{y-13}" width="8.5" height="17" rx="1.5" fill="{C["ok"]}"/>'
            )

        # --- 打字时的光标（跟着走）---
        if prog is None:
            parts.append(
                f'<rect y="{y-13}" width="8.5" height="17" rx="1.5" fill="{C["ok"]}">'
                f'<animate attributeName="x" values="{cmd_x};{cmd_x};{cmd_x+cmd_w:.1f};{cmd_x+cmd_w:.1f}" '
                f'keyTimes="0;{k0};{k1};1" dur="{DUR}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{k0};{k1}" '
                f'dur="{DUR}s" repeatCount="indefinite" calcMode="discrete"/>'
                f"</rect>"
            )
        elif prog is not None and 0.0 < prog < 1.0:
            parts.append(
                f'<rect x="{cmd_x + cmd_w * prog:.1f}" y="{y-13}" width="8.5" height="17" '
                f'rx="1.5" fill="{C["ok"]}"/>'
            )

    else:
        # --- 输出：整块瞬间出现 ---
        segs, t0 = item["segs"], item["t0"]
        k0 = frac(t0)
        if STATIC or (STATIC_AT is not None and STATIC_AT >= t0):
            shown = True
        elif STATIC_AT is not None:
            shown = False
        else:
            shown = None
        parts.append(f'<g opacity="{1 if shown else 0}">')
        parts.append(gate(shown, k0))
        parts.append(f'<text x="{LEFT}" y="{y}" font-family="{FONT}" font-size="{FS}" xml:space="preserve">')
        for text, color in segs:
            if text == "\u2588" and shown is None:
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
