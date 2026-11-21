#!/usr/bin/env python3
"""生成後のチェック（CI でも実行）：
1. サイト内リンク・画像の参照先が _site にあるか
2. 日本語ページに簡体字（Shift_JIS にない漢字）が残っていないか
用法：python3 tools/check_site.py   （問題があれば終了コード 1）
"""
import glob, os, re, sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_site"))
prefix = os.environ.get("SITE_PREFIX", "").rstrip("/")
errors = []
for f in glob.glob("**/*.html", recursive=True):
    h = open(f, encoding="utf-8").read()
    for u in re.findall(r'(?:href|src)="(/[^"#?]*)', h):
        if u.startswith("//"):
            continue
        p = u[len(prefix):] if prefix and u.startswith(prefix) else u
        p = p.lstrip("/")
        if not any(os.path.isfile(c) for c in ([p, os.path.join(p, "index.html")] if p else ["index.html"])):
            errors.append(f"リンク切れ {u}  ← {f}")
    if not f.startswith("zh/") and 'http-equiv="refresh"' not in h:
        bad = sorted({c for c in h if "一" <= c <= "鿿" and not c.encode("shift_jis", errors="ignore")})
        if bad:
            errors.append(f"簡体字 {''.join(bad)}  ← {f}")
for e in errors[:50]:
    print(e)
print(f"チェック完了：問題 {len(errors)} 件")
sys.exit(1 if errors else 0)
