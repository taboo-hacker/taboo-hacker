#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把本地文件通过 GitHub Git Data API 一次性提交到指定仓库（单次 commit）。

用法:
  python tools/push_to_github.py "commit message" README.md assets/terminal.svg ...

依赖: 已登录的 gh CLI（用于取 token）。
"""
import base64
import json
import subprocess
import sys
import urllib.error
import urllib.request

OWNER, REPO, BRANCH = "taboo-hacker", "taboo-hacker", "main"
API = "https://api.github.com"
TOKEN = subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def api(method: str, path: str, body=None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "dsh-profile-agent",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        print(f"!! HTTP {e.code} {method} {path}\n{e.read().decode()[:1200]}")
        raise


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    message, paths = sys.argv[1], sys.argv[2:]

    ref = api("GET", f"/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}")
    head = ref["object"]["sha"]
    base_tree = api("GET", f"/repos/{OWNER}/{REPO}/git/commits/{head}")["tree"]["sha"]

    entries = []
    for p in paths:
        with open(p, "rb") as fh:
            content = base64.b64encode(fh.read()).decode()
        blob = api("POST", f"/repos/{OWNER}/{REPO}/git/blobs", {"content": content, "encoding": "base64"})
        entries.append({"path": p.replace("\\", "/"), "mode": "100644", "type": "blob", "sha": blob["sha"]})
        print(f"  blob  {p}  -> {blob['sha'][:10]}")

    tree = api("POST", f"/repos/{OWNER}/{REPO}/git/trees", {"base_tree": base_tree, "tree": entries})
    commit = api(
        "POST",
        f"/repos/{OWNER}/{REPO}/git/commits",
        {"message": message, "tree": tree["sha"], "parents": [head]},
    )
    api("PATCH", f"/repos/{OWNER}/{REPO}/git/refs/heads/{BRANCH}", {"sha": commit["sha"], "force": False})
    print(f"OK {commit['sha']}  {commit['html_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
