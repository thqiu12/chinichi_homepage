#!/usr/bin/env python3
"""一次性导入：从旧版 chinichi-edu.jp（抓取结果目录）取出老师、新闻/合格速报，存成 src/data/*.json。
图片下载到 static/img/edu/（压缩到最长边 1200 / 老师照片 480）。
用法：python3 tools/import_edu.py ~/chinichi-web/crawl-edu
"""
import hashlib, io, json, re, sys, urllib.request
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CRAWL = Path(sys.argv[1]).expanduser()
DATA, IMG = ROOT / "src" / "data", ROOT / "static" / "img" / "edu"
BASE = "https://chinichi-edu.jp"
DEPT = {"/team1/": "人文系大学院", "/team2/": "理工系大学院", "/team3/": "美術", "/team4/": "音楽", "/team5/": "日本語", "/team6/": "文理学部"}
POSTS = {"/news1/39.html": "進学情報", "/new2/40.html": "イベント", "/news3/41.html": "お知らせ",
         "/case5/81.html": "合格実績", "/case5/82.html": "合格実績", "/case6/35.html": "合格実績", "/case7/80.html": "合格実績"}
CASE_TITLE = {"/case5/81.html": "83枚！合格率95%！知日音楽 2024年度合格実績発表", "/case5/82.html": "221枚！知日美術 2024年度合格実績がまたも新記録",
              "/case6/35.html": "合格実績｜2023～2024年度 知日塾 文理合格総覧", "/case7/80.html": "181枚合格！知日塾文理大学院 2025年度夏季試験 合格速報"}
# 旧文面の明らかな誤字（中国語の字形・表記ゆれ）
FIX = [("知日音乐", "知日音楽"), ("SUG英語", "SGU英語"), ("早稻田", "早稲田"), ("大辉ビル", "大輝ビル")]
KEEP = {"p", "br", "img", "strong", "b", "em", "a", "h2", "h3", "h4", "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td", "blockquote", "figure", "figcaption"}
DROP = {"script", "style", "iframe", "noscript", "svg", "video", "audio", "form"}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def save_img(src, maxw=1200):
    url = src if src.startswith("http") else BASE + src
    name = hashlib.md5(url.encode()).hexdigest()[:12] + ".jpg"
    out = IMG / name
    if not out.exists():
        try:
            im = Image.open(io.BytesIO(fetch(url))).convert("RGB")
        except Exception as e:  # noqa: BLE001
            print("  ! 画像取得失敗", url, e)
            return None
        im.thumbnail((maxw, maxw))
        im.save(out, quality=80, optimize=True, progressive=True)
    return f"/static/img/edu/{name}"


class Clean(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in DROP:
            self.skip += 1
            return
        if self.skip or tag not in KEEP:
            return
        a = dict(attrs)
        if tag == "img":
            src = a.get("src") or a.get("data-src")
            if src:
                local = save_img(src)
                if local:
                    self.out.append(f'<img src="{local}" alt="{a.get("alt", "")}" loading="lazy">')
            return
        if tag == "a" and a.get("href", "").startswith("http"):
            self.out.append(f'<a href="{a["href"]}" rel="noopener">')
            return
        self.out.append(f"<{tag}>")

    def handle_endtag(self, tag):
        if tag in DROP:
            self.skip = max(0, self.skip - 1)
            return
        if not self.skip and tag in KEEP and tag not in ("img", "br"):
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data.replace("<", "&lt;"))


def tidy(h):
    p = Clean()
    p.feed(h)
    h = "".join(p.out)
    h = re.sub(r"<(p|strong|b|em|li|h\d)>\s*</\1>", "", h)
    h = re.sub(r"(<br>\s*){2,}", "<br>", h)
    h = re.sub(r"<p>\s*<br>\s*</p>", "", h)
    for a, b in FIX:
        h = h.replace(a, b)
    return h.strip()


def text(h):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)
    idx = json.loads((CRAWL / "index.json").read_text())
    teachers, seen = [], set()
    for path, dept in DEPT.items():
        h = (CRAWL / idx[path]["file"]).read_text()
        for li in re.findall(r'<li class="line[^"]*"[^>]*>(.*?)</li>', h, re.S):
            name = re.search(r"<strong>(.*?)</strong>", li, re.S)
            school = re.search(r'<span class="jy">(.*?)</span>', li, re.S)
            desc = re.search(r'<div class="sz_desc">(.*?)</div>', li, re.S)
            img = re.search(r'<img src="([^"]+)"', li)
            if not name:
                continue
            n = text(name.group(1)).replace("​", "")
            key = (n, text(school.group(1)) if school else "")
            if key in seen:
                continue
            seen.add(key)
            lines = [x.strip() for x in re.split(r"<br\s*/?>", desc.group(1)) if text(x)] if desc else []
            t = {"name": n, "school": key[1], "lines": [text(x) for x in lines][:3], "dept": dept,
                 "photo": save_img(img.group(1), 480) if img else None}
            for a, b in FIX:
                t["school"] = t["school"].replace(a, b)
                t["lines"] = [x.replace(a, b) for x in t["lines"]]
            teachers.append(t)
    (DATA / "teachers.json").write_text(json.dumps(teachers, ensure_ascii=False, indent=1))
    print("講師", len(teachers))
    posts = []
    for path, cat in POSTS.items():
        h = (CRAWL / idx[path]["file"]).read_text()
        t = re.search(r'id="lblTitle">(.*?)</span>', h, re.S)
        if t:
            title = text(t.group(1))
            date = text(re.search(r'id="lblPutdate">(.*?)</span>', h, re.S).group(1))
            m = re.search(r'<span id="lblContent">(.*?)</span>\s*</div>\s*(?:<div class="(?:fenye|page|xg)|</div>)', h, re.S)
            body = m.group(1) if m else re.search(r'id="lblContent">(.*)', h, re.S).group(1)[:200000]
        else:  # 合格実績の詳細ページはタイトル・日付欄がない → 一覧の見出しを使い、日付は本文画像のアップロード日
            title = CASE_TITLE[path]
            i = h.find('class="update_detail_con">')
            body = h[i + 26:h.find('<div class="fenye', i) if h.find('<div class="fenye', i) > 0 else i + 200000]
            body = body[:body.find("<!-- footer")] if "<!-- footer" in body else body
            date = ""  # 画像のアップロード日は掲載日と一致しないので使わない
        for a, b in FIX:
            title = title.replace(a, b)
        slug = re.sub(r"\D", "", path.split("/")[-1])
        posts.append({"id": slug, "old": path, "title": title, "date": date, "category": cat, "html": tidy(body), "path": f"/news/{slug}/"})
        print(" ", date, title[:40])
    posts.sort(key=lambda x: (x["category"] != "合格実績", x["date"]), reverse=False)
    (DATA / "posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
