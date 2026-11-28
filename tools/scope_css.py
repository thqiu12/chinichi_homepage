#!/usr/bin/env python3
"""把旧法人站的 assets/style.css 限定到 .corp 容器内，生成 static/corp.css。
页头、页脚、面包屑、手机底栏、旧 page-hero 这些外壳样式不要（新站用方案 G 的外壳）。
最后追加方案 G 的配色和粗框风格覆盖。用法：python3 tools/scope_css.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "assets" / "style.css", ROOT / "static" / "corp.css"
DROP = re.compile(r"^\s*(\.(topbar|site-header|brand|nav|burger|breadcrumb|site-footer|mobile-cta|page-hero|skip-link|splash|cta-band)\b|body\.|\.hero\b)")


def scope_sel(sel):
    out = []
    for s in sel.split(","):
        s = s.strip()
        if not s or DROP.match(s):
            continue
        if s in (":root", "html", "body"):
            out.append(".corp")
        elif s.startswith(("html ", "body ")):
            out.append(".corp " + s.split(" ", 1)[1])
        else:
            out.append(".corp " + s)
    return ", ".join(out)


def scope_block(css):
    res, i = [], 0
    while i < len(css):
        j = css.find("{", i)
        if j < 0:
            break
        head = css[i:j].strip()
        if head.startswith("@media") or head.startswith("@supports"):
            depth, k = 1, j + 1
            while depth and k < len(css):
                depth += {"{": 1, "}": -1}.get(css[k], 0)
                k += 1
            inner = scope_block(css[j + 1:k - 1])
            if inner.strip():
                res.append(f"{head}{{{inner}}}")
            i = k
            continue
        k = css.find("}", j)
        body = css[j + 1:k]
        if head.startswith("@"):
            if head.startswith("@keyframes"):
                depth, k2 = 1, j + 1
                while depth and k2 < len(css):
                    depth += {"{": 1, "}": -1}.get(css[k2], 0)
                    k2 += 1
                res.append(css[i:k2].strip())
                i = k2
                continue
            res.append(f"{head}{{{body}}}")
        else:
            sel = scope_sel(head)
            if sel:
                res.append(f"{sel}{{{body.strip()}}}")
        i = k + 1
    return "\n".join(res)


G_OVERRIDE = """
/* ── 方案 G 覆盖：配色、粗框、错位阴影 ── */
.corp{--faint:#6B7280;--muted:#4B5563;--navy:#093D90;--navy-deep:#071A3F;--navy-soft:#EEF2F8;--red:#E94E14;--red-soft:#FDEBE3;--ink:#0B0F19;--text:#262B36;
  --line:#E3E6EC;--bg-alt:#F4F6F9;--radius:0px;--shadow:none;font-family:inherit;font-size:16px;color:var(--text);background:transparent;line-height:1.85}
.corp h1,.corp h2,.corp h3,.corp h4{color:var(--ink);font-weight:900}
.corp .section{padding:96px 0 0}.corp .section--alt{background:transparent}
.corp .section__title{font-size:clamp(30px,4.2vw,56px);letter-spacing:-.03em;line-height:1.15}
.corp .eyebrow,.corp .eyebrow--c,.corp .eyebrow--g{color:#C2410C;font-weight:800;letter-spacing:.2em;background:none;padding:0}
.corp .section__lead{color:#3b4150}
.corp .mini,.corp .case,.corp .proof,.corp .stat,.corp .gcard,.corp .course__card,.corp .coach,.corp .dir,.corp .rep__card,.corp .campus,
.corp .form-card,.corp .found,.corp .svc,.corp .route,.corp .grp__item,.corp .uni-tier,.corp .compgrp,.corp .step,.corp .flow__step{
  border:3px solid var(--ink)!important;border-radius:0!important;box-shadow:6px 6px 0 var(--red)!important;background:#fff}
.corp .case:nth-child(3n+2),.corp .mini:nth-child(3n+2),.corp .proof:nth-child(3n+2){box-shadow:6px 6px 0 #FFD23F!important}
.corp .case:nth-child(3n),.corp .mini:nth-child(3n),.corp .proof:nth-child(3n){box-shadow:6px 6px 0 var(--navy)!important}
.corp .big,.corp .num,.corp .gcard__big{font-family:"DIN Alternate","Bahnschrift","Avenir Next","Segoe UI",sans-serif;font-weight:800;color:var(--red)}
.corp .btn{border-radius:0;font-weight:900}
.corp .btn--primary{background:#C2410C;color:#fff;box-shadow:5px 5px 0 var(--ink)}
.corp .btn--white,.corp .xlink .btn{background:#fff;color:var(--ink)!important;box-shadow:5px 5px 0 #FFD23F}
.corp .btn--ghost{border:3px solid var(--ink);color:var(--ink);background:#fff}
.corp .faq details{border:3px solid var(--ink);border-radius:0;background:#fff}.corp .faq details[open]{background:#FFD23F}
.corp table{border:3px solid var(--ink)}.corp th{background:var(--ink)!important;color:#fff!important}
.corp .map-note h3{color:#fff;font-size:17px;margin-bottom:14px}
.corp .philo__venn .circle small{opacity:1}
.corp img{border-radius:0}
.corp .container{max-width:1240px}
.corp .route__icon,.corp .ic,.corp .flow__ic{display:none!important}
"""


def main():
    css = SRC.read_text()
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"@import[^;]+;", "", css)
    scoped = scope_block(css)
    scoped = scoped.replace("url(img/", "url(/assets/img/")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("/* 自动生成：tools/scope_css.py（旧法人站样式限定在 .corp 内 + 方案 G 覆盖）。不要手改，改脚本。 */\n" + scoped + G_OVERRIDE)
    print(OUT, len(scoped))


if __name__ == "__main__":
    main()
