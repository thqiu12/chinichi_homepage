#!/usr/bin/env python3
"""一次性导入：把旧版法人站（corporate/*.html, privacy.html）的正文区块转成片段 src/frag/*.json。

每个片段：{"kicker","h1","lead","cta":[text,href],"photo","sections":{id: html}, "order":[ids]}
- 去掉页头、面包屑、页脚、手机底栏；去掉 Tabler 图标(<i class="ti ...">)
- 链接改成新站路径（/corporate/…、/courses/…、/results/、/privacy/、/recruit/）
- 旧 page-hero 的文字和背景照片拿出来，交给新版页头（方案 G）
用法：python3 tools/import_corp.py   （导入后旧 html 可删除）
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "frag"
LINKS = [
    (r'(?:\.\./)?corporate/index\.html#', "/corporate/#"), (r'index\.html#', "/corporate/#"),
    (r'(?:\.\./)?corporate/index\.html', "/corporate/"),
    (r'university\.html', "/corporate/university/"), (r'recruit\.html', "/corporate/recruit/"), (r'training\.html', "/corporate/training/"),
    (r'results\.html', "/results/"), (r'bunri\.html', "/courses/undergraduate/"), (r'art\.html', "/courses/art/"),
    (r'acg\.html', "/courses/acg/"), (r'sports\.html', "/courses/sports/"),
    (r'\.\./privacy\.html', "/privacy/"), (r'privacy\.html', "/privacy/"), (r'\.\./index\.html', "/"),
    (r'https://chinichi-edu\.jp/job/', "/recruit/"), (r'https://chinichi-edu\.jp/', "/"),
]
PHOTO = {"bg-univ": "nyugaku-crowd", "bg-training": "chimusic", "bg-bunri": "bunri-hero", "bg-art": "chiart",
         "bg-acg": "acg-character", "bg-sports": "sports-hero", "bg-recruit": "nyugakushiki"}


def clean(h):
    h = re.sub(r"<i class=\"ti[^\"]*\"[^>]*></i>\s*", "", h)
    h = re.sub(r'<div class="ic">\s*</div>', "", h)
    h = re.sub(r'<span class="route__icon">\s*</span>', "", h)
    h = re.sub(r'<div class="flow__ic">\s*</div>', "", h)
    h = h.replace('src="../assets/', 'src="/assets/').replace('src="assets/', 'src="/assets/')
    h = h.replace("url(../assets/", "url(/assets/").replace("url(assets/", "url(/assets/")

    def fix(m):
        url = m.group(2)
        if url.startswith(("http", "/", "#", "tel:", "mailto:")) and not url.startswith("https://chinichi-edu.jp"):
            return m.group(0)
        for pat, rep in LINKS:
            new = re.sub("^" + pat, rep, url)
            if new != url:
                return f'{m.group(1)}"{new}"'
        return m.group(0)
    return re.sub(r'(href=)"([^"]*)"', fix, h)


def sections(body):
    out, order = {}, []
    for k, m in enumerate(re.finditer(r'<section([^>]*)>(.*?)</section>', body, re.S)):
        attrs = m.group(1)
        sid = (re.search(r'id="([^"]+)"', attrs) or [None, f"s{k}"])[1]
        out[sid] = f"<section{attrs}>{clean(m.group(2))}</section>"
        order.append(sid)
    return out, order


def page_hero(sec):
    kick = re.search(r'<span class="kicker">(.*?)</span>', sec, re.S)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", sec, re.S)
    lead = re.search(r"</h1>\s*<p[^>]*>(.*?)</p>", sec, re.S)
    btn = re.search(r'<a href="([^"]+)" class="btn[^"]*"[^>]*>(.*?)</a>', sec, re.S)
    bg = re.search(r'class="page-hero ([^"]+)"', sec) or re.search(r'class="page-hero\s*([^"]*)"', sec)
    strip = lambda s: re.sub(r"\s+", " ", re.sub(r"<(?!br)[^>]+>", "", s)).strip()
    return {"kicker": strip(kick.group(1)) if kick else "", "h1": strip(h1.group(1)) if h1 else "",
            "lead": strip(lead.group(1)) if lead else "", "cta": [strip(btn.group(2)), btn.group(1)] if btn else None,
            "photo": PHOTO.get((bg.group(1).split() or [""])[-1] if bg else "", "")}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for src in sorted((ROOT / "corporate").glob("*.html")) + [ROOT / "privacy.html"]:
        h = src.read_text()
        h = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S)
        start = h.find("<section")
        end = h.find("<footer")
        body = h[start:end]
        secs, order = sections(body)
        frag = {"source": str(src.relative_to(ROOT)), "sections": secs, "order": order}
        first = secs[order[0]] if order else ""
        if 'class="page-hero' in first:
            frag.update(page_hero(first))
            del secs[order[0]]; order = order[1:]; frag["order"] = order
        name = "corp-" + src.stem if src.parent.name == "corporate" else src.stem
        (OUT / f"{name}.json").write_text(json.dumps(frag, ensure_ascii=False, indent=1))
        print(f"{name}: {len(order)} sections, hero={'h1' in frag}")


if __name__ == "__main__":
    main()
