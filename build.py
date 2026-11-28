#!/usr/bin/env python3
"""知日塾 日本サイト（chinichi-edu.jp）静的サイト生成。デザインは方案 G（中国語サイト www.chinichi.com と共通）。

入力
  src/ja/*.md|*.html   日本語ページ（1行目 <!--meta {...}-->。.md は tools/md.py で変換）
  src/zh/*.md|*.html   中国語ページ（/zh/ 以下）
  src/frag/*.json      旧法人サイトから取り込んだ本文ブロック（tools/import_corp.py）
  src/data/*.json      講師・ニュース・旧URL一覧（tools/import_edu.py）
  static/ assets/      そのまま _site/ にコピー
出力 _site/
環境変数
  SITE_PREFIX=/chinichi_homepage   github.io のプロジェクトURLで確認するとき（内部リンクに前置。noindex になる）
使い方：python3 build.py
"""
import html, json, os, re, shutil, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import md  # noqa: E402
import site_posts  # noqa: E402

SRC, DIST = ROOT / "src", ROOT / "_site"
BASE = "https://chinichi-edu.jp"
PREFIX = os.environ.get("SITE_PREFIX", "").rstrip("/")
NOINDEX = bool(PREFIX) or os.environ.get("NOINDEX") == "1"  # 確認用（github.io のプロジェクトURL など）は検索に出さない
UPDATED = date.today().isoformat()
esc = lambda s: html.escape(str(s), quote=True)

TEL_JP, TEL_CN, TEL_CORP, TEL_SGG = "080-4340-9963", "400-0987-929", "03-6205-9570", "03-6233-9963"
NAV = {
    "ja": [("/about/", "知日について"), ("/courses/", "コース"), ("/results/", "合格実績"), ("/teachers/", "講師"),
           ("/access/", "アクセス"), ("/news/", "ニュース"), ("/corporate/", "法人の方へ")],
    "zh": [("/zh/", "首页"), ("https://www.chinichi.com/courses/", "课程"), ("https://www.chinichi.com/results/", "合格实绩"),
           ("/zh/access/", "日本校区"), ("https://www.chinichi.com/", "中国官网")],
}
L = {
    "ja": {"home": "ホーム", "cta": "無料相談 →", "cta_href": "/contact/", "lang": ("/zh/", "中文"), "skip": "本文へ移動",
           "menu": "メニューを開く", "updated": "更新"},
    "zh": {"home": "首页", "cta": "电话咨询 →", "cta_href": "tel:08043409963", "lang": ("/", "日本語"), "skip": "跳到正文",
           "menu": "打开菜单", "updated": "更新"},
}
PAGE_IMG = {"/courses/": "class-lecture", "/courses/graduate/": "tutoring", "/courses/music/": "music-studio", "/courses/eju/": "teacher-board",
            "/courses/sgu/": "class-lecture", "/access/": "takadanobaba", "/recruit/": "storefront", "/contact/": "lounge-blue",
            "/zh/access/": "takadanobaba", "/about/": "storefront", "/teachers/": "class-lecture"}
PAGE_COLOR = {"/courses/graduate/": "#C8643B", "/courses/art/": "#12A6CF", "/courses/acg/": "#12A6CF", "/courses/music/": "#15171C",
              "/courses/sports/": "#2FA4E7"}
SECTION_TAG = [("/courses/", "COURSE"), ("/results/", "RESULTS"), ("/teachers/", "TEACHERS"), ("/access/", "ACCESS"), ("/zh/access/", "CAMPUS"), ("/zh/news/", "NEWS"),
               ("/about/", "ABOUT"), ("/news/", "NEWS"), ("/recruit/", "RECRUIT"), ("/contact/", "CONTACT"), ("/corporate/", "FOR BUSINESS"),
               ("/privacy/", "PRIVACY")]
ORG = {"@context": "https://schema.org", "@type": "EducationalOrganization", "@id": BASE + "/#org", "name": "知日株式会社",
       "alternateName": ["知日塾", "知日教育グループ", "CHINICHI Inc.", "知日美術 CHIART", "知日音楽 CHIMUSIC", "元気体育"],
       "url": BASE + "/", "logo": BASE + "/assets/img/logo.png", "foundingDate": "2013-12", "telephone": "+81-3-6205-9570",
       "address": {"@type": "PostalAddress", "streetAddress": "高田馬場1-34-6", "addressLocality": "新宿区", "addressRegion": "東京都", "addressCountry": "JP"},
       "sameAs": ["https://www.chinichi.com/"]}


# ───────── 共通の外枠 ─────────
def head(lang, title, desc, path, extra="", corp=False):
    full = title if "知日" in title else f"{title}｜知日塾"
    links = "".join(f'<a href="{u}"{" class=on aria-current=page" if u != "/zh/" and path.startswith(u) or u == path else ""}>{t}</a>' for u, t in NAV[lang])
    lu, lt = L[lang]["lang"]
    big = "".join(f'<a href="{u}">{t}</a>' for u, t in NAV[lang]) + f'<a href="{L[lang]["cta_href"]}">{L[lang]["cta"]}</a><a href="{lu}">{lt}</a>'
    fonts = ""  # 日本語は端末のフォント（ヒラギノ・游ゴシック・メイリオ・Noto Sans CJK）を使う。Web フォントはスマホで表示が遅くなるため使わない
    robots = '<meta name="robots" content="noindex">' if NOINDEX else ""
    alt = (f'<link rel="alternate" hreflang="ja" href="{BASE}/"><link rel="alternate" hreflang="zh-CN" href="{BASE}/zh/">' if path in ("/", "/zh/") else "")
    return f"""<!doctype html>
<html lang="{'ja' if lang == 'ja' else 'zh-CN'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(full)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{BASE}{path}">{alt}{robots}
<meta property="og:title" content="{esc(full)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website"><meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{BASE}/assets/img/og.jpg">
<link rel="icon" href="/assets/favicon-32.png"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
{fonts}<link rel="stylesheet" href="/static/site.css?v={UPDATED}">{'<link rel="stylesheet" href="/static/corp.css?v=' + UPDATED + '">' if corp else ''}
<script src="/static/site.js?v={UPDATED}" defer></script>
{extra}
</head>
<body>
<a class="skip" href="#main">{L[lang]['skip']}</a>
<header class="g"><a class="lg" href="{'/' if lang == 'ja' else '/zh/'}"><img src="/assets/img/logo.png" alt="知日塾 CHINICHI" width="88" height="34" loading="eager"></a><nav aria-label="メイン">{links}<a class="lang" href="{lu}" hreflang="{'zh' if lang == 'ja' else 'ja'}">{lt}</a><a class="c" href="{L[lang]['cta_href']}">{L[lang]['cta']}</a><button class="mbtn" type="button" aria-label="{L[lang]['menu']}" aria-expanded="false"><i></i><i></i></button></nav></header>
<div class="ov" aria-label="menu"><div>{big}</div><p>{'入塾相談' if lang == 'ja' else '在日咨询'} {TEL_JP} · {'法人' if lang == 'ja' else '国内'} {TEL_CORP if lang == 'ja' else TEL_CN}</p></div>
"""


def foot(lang):
    if lang == "zh":
        cta = (f'<section class="cta" id="cta"><div class="w"><h2>说出你的<br>目标学校。</h2><p>在日本的同学：{TEL_JP}（中文、日语都可以）· 国内：{TEL_CN} · 公众号 @知日塾日本留学</p>'
               f'<a class="b" href="tel:08043409963">电话咨询 →</a></div></section>')
        cols = [("课程（中文官网）", [("https://www.chinichi.com/courses/undergraduate/", "学部（本科）"), ("https://www.chinichi.com/courses/graduate/", "大学院（修士）"),
                                  ("https://www.chinichi.com/courses/art/", "知日美术"), ("https://www.chinichi.com/courses/music/", "知日音乐")]),
                ("在日本", [("/zh/access/", "日本校区"), ("/", "日本語サイト"), ("/corporate/", "法人の方へ（日语）")]),
                ("联系", [("tel:08043409963", f"日本 {TEL_JP}"), ("tel:4000987929", f"国内 {TEL_CN}"), ("/privacy/", "隐私政策（日语）")])]
    else:
        cta = (f'<section class="cta" id="cta"><div class="w"><h2>目標の大学を、<br>教えてください。</h2><p>志望校・専攻・いまの日本語力をうかがい、書面でプランをお出しします。'
               f'入塾相談 {TEL_JP}（日本）／{TEL_CN}（中国）</p><a class="b" href="/contact/">無料の進学相談 →</a></div></section>')
        cols = [("コース", [("/courses/undergraduate/", "学部進学"), ("/courses/graduate/", "大学院進学"), ("/courses/art/", "知日美術 CHIART"),
                          ("/courses/acg/", "ACG 学部"), ("/courses/music/", "知日音楽 CHIMUSIC"), ("/courses/sports/", "元気体育"), ("/courses/eju/", "EJU・日本語")]),
                ("知日塾", [("/about/", "知日について"), ("/results/", "合格実績"), ("/teachers/", "講師紹介"), ("/access/", "拠点・アクセス"),
                          ("/news/", "ニュース"), ("/recruit/", "採用情報"), ("/contact/", "お問い合わせ")]),
                ("法人の方へ", [("/corporate/", "法人トップ"), ("/corporate/university/", "大学提携・送り出し"), ("/corporate/recruit/", "人材紹介・採用支援"),
                             ("/corporate/training/", "法人研修・語学"), ("/privacy/", "プライバシーポリシー")])]
    c = "".join(f"<div><p class=\"fh\">{h}</p><ul>{''.join(f'<li><a href=\"{u}\">{t}</a></li>' for u, t in items)}</ul></div>" for h, items in cols)
    return f"""{cta}
<footer><div class="w">
<div><img src="/assets/img/logo.png" alt="知日塾" width="88" height="34">
<p>知日株式会社<br>〒169-0075 東京都新宿区高田馬場1-34-6<br>TEL {TEL_CORP}（{'法人窓口' if lang == 'ja' else '公司'}）<br>{'入塾相談' if lang == 'ja' else '升学咨询'} {TEL_JP}</p></div>
{c}
<div class="copy"><span>© 2013–{date.today().year} 知日株式会社 CHINICHI Inc.</span><a href="https://www.chinichi.com/">{'中国語サイト' if lang == 'ja' else '中文官网'} www.chinichi.com</a></div>
</div></footer>
</body></html>
"""


def crumb(lang, items):
    home = "/" if lang == "ja" else "/zh/"
    parts = [f'<a href="{home}">{L[lang]["home"]}</a>'] + [f'<a href="{u}">{esc(t)}</a>' if u else esc(t) for u, t in items]
    return '<div class="crumb">' + " › ".join(parts) + "</div>"


def ld(*objs):
    return "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>' for o in objs)


def bc(lang, items):
    li = [{"@type": "ListItem", "position": 1, "name": L[lang]["home"], "item": BASE + ("/" if lang == "ja" else "/zh/")}]
    for i, (u, t) in enumerate(items, 2):
        d = {"@type": "ListItem", "position": i, "name": re.sub(r"<[^>]+>", "", t)}
        if u:
            d["item"] = BASE + u
        li.append(d)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": li}


def pagehead(lang, path, items, h1, lead="", meta="", img=None, cta=None):
    if img is None and path in PAGE_IMG:
        img = f"/static/img/site/{PAGE_IMG[path]}-1600.jpg"
    tag = next((t for k, t in SECTION_TAG if path.startswith(k)), "")
    color = PAGE_COLOR.get(path)
    btn = f'<p style="margin-top:22px"><a class="btn" href="{cta[1]}">{esc(cta[0])} →</a></p>' if cta else ""
    return (f'<section class="pagehead{" has-img" if img else ""}"{f" style=--c:{color}" if color else ""}>'
            f'{f"<img src={chr(34)}{img}{chr(34)} alt={chr(34)}{chr(34)} fetchpriority=high loading=eager>" if img else ""}<div class="w">{crumb(lang, items)}'
            f'{f"<em class=tag>{tag}</em>" if tag else ""}<h1>{h1}</h1>{f"<p class=lead>{esc(lead)}</p>" if lead else ""}{meta}{btn}</div></section>')


SIDE = {"ja": f"""<aside class="side">
<div class="card"><h3>無料の進学相談</h3><p>志望校・専攻・いまの日本語力を教えてください。書面でプランをお出しします。</p>
<p><a class="btn" href="/contact/">相談する</a></p><p>日本 {TEL_JP}<br>中国 {TEL_CN}</p></div>
<div class="card"><h3>よく見られるページ</h3><ul>
<li><a href="/courses/">コース一覧</a></li><li><a href="/results/">合格実績</a></li><li><a href="/teachers/">講師紹介</a></li>
<li><a href="/access/">拠点・アクセス</a></li><li><a href="/corporate/">法人の方へ</a></li></ul></div>
</aside>""", "zh": f"""<aside class="side"><div class="card"><h3>升学咨询</h3><p>在日本的同学请直接打电话，中文、日语都可以。</p>
<p><a class="btn" href="tel:08043409963">{TEL_JP}</a></p><p>国内 {TEL_CN}</p></div></aside>"""}


PAGES, SITEMAP = [], []


IMG_RE = re.compile(r'<img\b[^>]*>')


def optimize_imgs(text):
    """写真の srcset（400/800/1600）、首屏以下の遅延読み込み、首屏切替の2枚目以降の後読み。"""
    def srcset(tag):
        m = re.search(r'src="(/static/img/site/[\w-]+)-(800|1600)\.jpg"', tag)
        if not m or "srcset=" in tag:
            return tag
        b = m.group(1)
        if m.group(2) == "1600":
            add = f' srcset="{b}-800.jpg 800w, {b}-1600.jpg 1600w" sizes="100vw"'
        else:
            add = f' srcset="{b}-400.jpg 400w, {b}-800.jpg 800w" sizes="(max-width: 900px) 50vw, 400px"'
        return tag[:-1] + add + ">"
    text = IMG_RE.sub(lambda m: srcset(m.group(0)), text)
    # 首屏の写真切替：1枚目は最優先、2枚目以降は data-src にして load 後に取得
    def ss(block):
        n = [0]
        def one(m):
            tag = m.group(0)
            n[0] += 1
            if n[0] == 1:
                return tag[:-1] + ' fetchpriority="high" loading="eager">'
            return tag.replace(' src="', ' data-src="').replace(' srcset="', ' data-srcset="')
        return IMG_RE.sub(one, block.group(0))
    text = re.sub(r'<div class="ss">.*?</div></section>', ss, text, flags=re.S)
    # それ以外で loading 指定のない画像は遅延読み込み
    return IMG_RE.sub(lambda m: m.group(0) if "loading=" in m.group(0) else m.group(0)[:-1] + ' loading="lazy" decoding="async">', text)


def write(path, text):
    text = optimize_imgs(text)
    if PREFIX:
        text = re.sub(r'((?:href|src|action)=["\']?)/(?!/)', r"\1" + PREFIX + "/", text)
        text = re.sub(r"(url=)/(?!/)", r"\1" + PREFIX + "/", text)  # 旧URL転送の meta refresh
        text = re.sub(r'((?:data-srcset|srcset)="[^"]*)', lambda m: re.sub(r'(^|=")/|(, )/', lambda k: (k.group(1) or k.group(2) or "") + PREFIX + "/", m.group(1)), text)
        text = text.replace("url(/assets/", f"url({PREFIX}/assets/").replace("url(/static/", f"url({PREFIX}/static/")
    out = DIST / path.lstrip("/") / "index.html" if path.endswith("/") else DIST / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)


# 旧サイト・旧法人サイトの文面に残っていた中国語由来の表現・簡体字を日本語に直す（日本語ページだけに適用）
JA_TEXT_FIX = [
    ("源自熱愛・根植専門・通往世界のスポーツ教育プラットフォーム", "情熱から始まり、専門に根ざし、世界へつながるスポーツ教育プラットフォーム"),
    ("スポーツの「全生態」を支える6領域", "スポーツを多面的に支える6つの領域"), ("双拠点体制", "2拠点体制"),
    ("全方位 N対1 の進学指導", "複数の講師で一人を支える進学指導"), ("全方位で", "あらゆる面で"), ("高品質なトレーニング", "質の高いトレーニング"),
    ("宣传册「美術 合格采访」の全インタビュー", "パンフレット「美術 合格インタビュー」掲載の全インタビュー"),
    ("宣传册「文理学部 合格経験談」", "パンフレット「文理学部 合格体験記」"),
    ("研究计划书 研究计划书开题、写作全程指导", "研究計画書 テーマ設定から執筆まで一貫して指導"),
    ("教研グループ", "指導研究グループ"), ("教研チーム", "指導研究チーム"), ("教学経験", "指導経験"), ("班主任", "担任"),
    ("研究计划书开题、写作全程指导", "テーマ設定から執筆まで一貫して指導"), ("开题、写作全程指导", "テーマ設定から執筆まで一貫して指導"), ("研究计划书", "研究計画書"),
    ("丨", "｜"), ("苏 先生", "蘇 先生"),
]


def ja_fix(text):
    for a, b in JA_TEXT_FIX:
        text = text.replace(a, b)
    # 合格数を「枚」で数えるのは中国語の言い方 → 「件」
    return re.sub(r"(\d)((?:\s|<[^>]+>)*)枚", r"\1\2件", text)


def emit(lang, path, title, desc, body, extra="", corp=False, priority="0.7", scripts=""):
    if lang == "ja":
        body, title, desc, extra = ja_fix(body), ja_fix(title), ja_fix(desc), ja_fix(extra)
    write(path, head(lang, title, desc, path, extra, corp) + f'<main id="main">{body}</main>{scripts}' + foot(lang))
    SITEMAP.append((path, UPDATED, priority))


# ───────── ページ種別 ─────────
def read_page(p, lang):
    t = p.read_text()
    m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->\s*", t, re.S)
    meta = json.loads(m.group(1))
    body = t[m.end():]
    meta["body"] = md.to_html(body, shift=0) if p.suffix == ".md" else body
    meta.setdefault("lang", lang)
    return meta


def render_page(p, latest):
    lang, path = p["lang"], p["path"]
    if p.get("raw"):
        body = p["body"].replace("<!--LATEST_NEWS-->", latest.get(lang, ""))
        extra = ld(ORG, {"@context": "https://schema.org", "@type": "WebSite", "name": "知日塾", "url": BASE + path, "inLanguage": "ja" if lang == "ja" else "zh-CN"})
        emit(lang, path, p["title"], p["description"], body, extra, priority=p.get("priority", "1.0"))
        return
    items = [(None, p.get("h1", p["title"]))]
    inner = f'<div class="prose">{p["body"]}</div>'
    if p.get("side", True):
        inner = f'<div class="layout">{inner}{SIDE[lang]}</div>'
    body = pagehead(lang, path, items, esc(p.get("h1", p["title"])), p.get("lead", "")) + f'<div class="w content">{inner}</div>'
    emit(lang, path, p["title"], p["description"], body, ld(bc(lang, items)))
    PAGES.append(p)


STUDENT_FIX = [('href="/corporate/#contact"', 'href="/contact/"'), ("提携・送り出しを相談する", "入塾について相談する"),
               ("ACGについて相談する", "ACG コースについて相談する")]
JA_FIX = [("校内考", "個別試験")]  # 中国語由来の言い方を日本語に


def frag(name):
    f = json.loads((SRC / "frag" / f"{name}.json").read_text())
    for sid in f["order"]:
        for a, b in JA_FIX:
            f["sections"][sid] = f["sections"][sid].replace(a, b)
    return f


def frag_body(f, ids=None, student=False):
    out = []
    for sid in ids or f["order"]:
        s = f["sections"].get(sid, "")
        if 'class="cta-band' in s[:80]:
            continue
        if student:
            for a, b in STUDENT_FIX:
                s = s.replace(a, b)
        out.append(s)
    return '<div class="corp">' + "".join(out) + "</div>"


FRAG_PAGES = [  # (片段, 路径, 标题, 描述, 学生向け)
    ("corp-bunri", "/courses/undergraduate/", "学部（文系・理系）進学コース", "知日塾・知日理工の学部進学コース：EJU 対策から個別試験の小論文・面接まで。国公立・早慶上理・MARCH・関関同立への合格実績。", True),
    ("corp-art", "/courses/art/", "知日美術 CHIART｜美術・芸術系大学への進学", "知日美術（CHIART）：美術・芸術系大学・大学院への進学指導。ポートフォリオ、実技、研究計画書。主な美大別の合格数。", True),
    ("corp-acg", "/courses/acg/", "ACG 学部（アニメ・漫画・ゲーム）｜知日美術", "知日美術 ACG 学部：アニメ・漫画・ゲーム・イラスト・キャラクターデザインの進学と作品づくり。", True),
    ("corp-sports", "/courses/sports/", "元気体育 GENKI SPORTS｜スポーツ系の進学", "元気体育（GENKI SPORTS）：スポーツ系の大学・大学院への進学、競技と進路の両立、日中のスポーツ交流。", True),
    ("corp-results", "/results/", "合格実績", "知日塾の合格実績：知日美術の美大別合格数、文理の合格実績と合格体験記。", True),
    ("corp-university", "/corporate/university/", "大学提携・留学生送り出し", "知日株式会社の大学提携：中国での募集・選抜から日本語・専門教育、出願指導、入学後の定着まで一貫支援。", False),
    ("corp-recruit", "/corporate/recruit/", "人材紹介・採用支援", "知日株式会社の人材紹介：育成段階から把握した中国人材を日本企業へ。入社後の定着まで支援。", False),
    ("corp-training", "/corporate/training/", "法人研修・語学", "知日株式会社の法人研修：ビジネス中国語と異文化対応力の研修を、対面・オンラインで。", False),
]
CORP_SCRIPTS = '<script src="/assets/reveal.js" defer></script>'


def render_frags():
    for name, path, title, desc, student in FRAG_PAGES:
        f = frag(name)
        items = [("/courses/", "コース"), (None, title)] if path.startswith("/courses/") else (
            [("/corporate/", "法人の方へ"), (None, title)] if path.startswith("/corporate/") else [(None, title)])
        cta = f.get("cta")
        if cta and student:
            cta = ["入塾について相談する", "/contact/"] if "提携" in cta[0] or "送り出し" in cta[0] else [cta[0], cta[1].replace("/corporate/#contact", "/contact/")]
        photo = f"/assets/img/photos/{f['photo']}.jpg" if f.get("photo") else None
        body = pagehead("ja", path, items, f["h1"] or esc(title), f.get("lead", ""), img=photo, cta=cta) + frag_body(f, student=student)
        emit("ja", path, title, desc, body, ld(bc("ja", items)), corp=True, scripts=CORP_SCRIPTS)
    # 法人トップ・知日について
    f = frag("corp-index")
    top = f["sections"]["top"]
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", top, re.S).group(1).strip()
    lead = re.sub(r"<[^>]+>", "", (re.search(r"</h1>\s*<p[^>]*>(.*?)</p>", top, re.S) or [None, ""])[1]).strip()
    items = [(None, "法人の方へ")]
    body = pagehead("ja", "/corporate/", items, h1, lead, img="/assets/img/photos/nyugakushiki.jpg", cta=["お問い合わせ・資料請求", "#contact"]) + \
        frag_body(f, ["routes", "services", "proof", "cases", "foundation", "dx", "pathway", "contact"])
    emit("ja", "/corporate/", "法人の方へ｜知日株式会社", "知日株式会社の法人向けサービス：大学提携・留学生の送り出し、中国人材の紹介・定着支援、法人研修・語学。",
         body, ld(ORG, bc("ja", items)), corp=True, priority="0.8",
         scripts='<script src="/assets/config.js"></script><script src="/assets/form.js"></script>' + CORP_SCRIPTS)
    items = [(None, "知日について")]
    body = pagehead("ja", "/about/", items, "知日について", "中国と日本の架け橋として、留学生一人ひとりの可能性を広げます。") + \
        frag_body(f, ["philosophy", "representative", "company", "history", "growth", "group", "campuses"])
    emit("ja", "/about/", "知日について", "知日株式会社・知日塾について：理念、代表メッセージ、会社概要、沿革、知日教育グループの全体像、拠点。",
         body, ld(ORG, bc("ja", items)), corp=True, priority="0.8", scripts=CORP_SCRIPTS)
    # プライバシーポリシー
    f = frag("privacy")
    items = [(None, "プライバシーポリシー")]
    body = pagehead("ja", "/privacy/", items, "プライバシーポリシー") + frag_body(f)
    emit("ja", "/privacy/", "プライバシーポリシー", "知日株式会社の個人情報の取り扱いについて。", body, ld(bc("ja", items)), corp=True, priority="0.3")


def render_teachers():
    ts = json.loads((SRC / "data" / "teachers.json").read_text())
    order = ["文理学部", "人文系大学院", "理工系大学院", "美術", "音楽", "日本語"]
    blocks = []
    for d in order:
        g = [t for t in ts if t["dept"] == d]
        if not g:
            continue
        cards = "".join(
            f'<article class="tcard rv"><div class="ph">{f"<img src={chr(34)}{t["photo"]}{chr(34)} alt={chr(34)}{esc(t["name"])}{chr(34)} loading=lazy>" if t.get("photo") else ""}</div>'
            f'<div class="b"><b>{esc(t["name"])}</b><span class="sc">{esc(t["school"])}</span><ul>{"".join(f"<li>{esc(x)}</li>" for x in t["lines"])}</ul></div></article>' for t in g)
        blocks.append(f'<div class="tdept rv"><h2>{d}</h2><span>{len(g)}</span></div><div class="tgrid">{cards}</div>')
    items = [(None, "講師紹介")]
    body = pagehead("ja", "/teachers/", items, "講師紹介", "常勤講師が中心。志望する専攻と同じ分野を修めた講師が担当します。") + f'<div class="w content">{"".join(blocks)}</div>'
    emit("ja", "/teachers/", "講師紹介", "知日塾の講師紹介：文理学部・大学院（文系・理系）・美術・音楽・日本語の講師。出身大学と担当科目。", body, ld(bc("ja", items)))


def render_news(extra=()):
    posts = json.loads((SRC / "data" / "posts.json").read_text())
    lis = "".join(f'<li><a href="{x["ja_path"]}"><span>{esc(x["titleJa"])}</span><time>{x["date"]}</time></a></li>' for x in extra) + "".join(f'<li><a href="{x["path"]}"><span>{esc(x["title"])}</span><time>{x["date"] or x["category"]}</time></a></li>' for x in posts)
    items = [(None, "ニュース")]
    body = pagehead("ja", "/news/", items, "ニュース・合格速報", "合格実績、進学情報、イベントのお知らせ。") + f'<div class="w content"><ul class="list">{lis}</ul></div>'
    emit("ja", "/news/", "ニュース・合格速報", "知日塾のニュース：合格実績、進学情報、イベントのお知らせ。", body, ld(bc("ja", items)), priority="0.6")
    for i, x in enumerate(posts):
        items = [("/news/", "ニュース"), (None, x["title"])]
        when = f'<time>{x["date"]}</time>　' if x["date"] else ""
        meta = f'<p class="meta">{when}{esc(x["category"])}</p>'
        pn = '<div class="prevnext">' + (f'<a href="{posts[i - 1]["path"]}">← {esc(posts[i - 1]["title"])}</a>' if i else "<span></span>") + \
             (f'<a href="{posts[i + 1]["path"]}">{esc(posts[i + 1]["title"])} →</a>' if i + 1 < len(posts) else "") + "</div>"
        body = pagehead("ja", "/news/", items, esc(x["title"]), "", meta, img=False) + \
            f'<div class="w content"><div class="layout"><article class="prose">{x["html"]}{pn}</article>{SIDE["ja"]}</div></div>'
        art = {"@context": "https://schema.org", "@type": "Article", "headline": x["title"], "publisher": {"@id": BASE + "/#org"}, "mainEntityOfPage": BASE + x["path"]}
        if x["date"]:
            art["datePublished"] = x["date"]
        desc = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x["html"]))[:100]
        emit("ja", x["path"], x["title"], desc, body, ld(bc("ja", items), art), priority="0.5")
    return posts


# ───────── 日本の校舎の「官网动态」（chinichi_OS で各校舎が書き、責任者が承認したもの。中国語 → /zh/news/） ─────────
JP_CAMPUS_ZH = {
    "tokyo": ("知日塾 东京本部（高田马场）", "东京都新宿区高田马场1-34-8 大辉ビル2F", "高田马场站周边", TEL_JP),
    "osaka": ("知日塾 大阪校", "大阪府大阪市中央区南本町3-4-7 第一住建御堂筋本町ビル", "本町站约 150 米", TEL_JP),
    "kyoto": ("知日塾 京都校", "京都府京都市中京区河原町通蛸薬师下る塩屋町327-3", "阪急京都河原町站步行约 170 米", TEL_JP),
}


def _paras(text):
    return "".join("<p>" + esc(p.strip()).replace("\n", "<br>") + "</p>" for p in re.split(r"\n\s*\n", text or "") if p.strip())


def _post_img(im, cls=""):
    return (f'<img src="{im["src"]}-800.jpg" srcset="{im["src"]}-800.jpg 800w, {im["src"]}-1600.jpg 1600w" '
            f'sizes="(max-width: 900px) 100vw, 760px" width="800" height="600" alt="{esc(im.get("alt", ""))}" class="{cls}" loading="lazy">')


def post_cards(items, limit=12):
    out = []
    for x in items[:limit]:
        label = x.get("kindLabel") or ""
        when = f'活动时间 {x["eventAt"][:16].replace("T", " ")}' if x["kind"] == "EVENT" and x.get("eventAt") else x["date"]
        thumb = _post_img(x["images"][0], "pc-img") if x.get("images") else f'<div class="pc-img pc-noimg" aria-hidden="true"><span>{esc(label)}</span></div>'
        out.append(f'<a class="pcard rv" href="{x["path"]}">{thumb}<div class="pc-b"><span class="pc-k">{esc(label)}'
                   f'{" · " + esc(x["division"]) if x.get("division") else ""}</span><b>{esc(x["title"])}</b>'
                   f'<span class="pc-d">{esc(x["campus"])} · {when}</span></div></a>')
    return f'<div class="pcards">{"".join(out)}</div>' if out else ""


JA_KIND = {"NEWS": "校舎ニュース", "EVENT": "イベント・説明会", "RESULT": "合格速報", "VOICE": "合格者の声", "TEACHER": "講師紹介"}
JA_DIV = {"文理学部": "学部（文系・理系）", "大学院": "大学院", "美术": "美術", "音乐": "音楽", "体育": "スポーツ", "EJU·日语": "EJU・日本語"}
JP_CAMPUS_JA = {
    "tokyo": ("知日塾 東京本部（高田馬場）", "東京都新宿区高田馬場1-34-8 大輝ビル2F", "高田馬場駅周辺"),
    "osaka": ("知日塾 大阪校", "大阪府大阪市中央区南本町3-4-7 第一住建御堂筋本町ビル3F", "本町駅から約150m"),
    "kyoto": ("知日塾 京都校", "京都府京都市中京区河原町通蛸薬師下る塩屋町327-3 3F", "河原町駅から徒歩170m"),
}


def hreflang(x):
    return (f'<link rel="alternate" hreflang="ja" href="{BASE}{x["ja_path"]}"><link rel="alternate" hreflang="zh-CN" href="{BASE}{x["path"]}">'
            if x.get("ja_path") else "")


def render_site_posts_ja(posts):
    """日文版のある記事 → /news/s-<id>/（日本語）。一覧は /news/ に混ぜる（render_news）。"""
    for x in [p for p in posts if p.get("ja_path")]:
        name, addr, access = JP_CAMPUS_JA[x["campusSlug"]]
        items = [("/news/", "ニュース"), (None, x["titleJa"])]
        label = JA_KIND.get(x["kind"], "") + (f'・{JA_DIV[x["division"]]}' if x.get("division") in JA_DIV else "")
        ev = f'　開催：{x["eventAt"][:16].replace("T", " ")}' if x.get("eventAt") else ""
        meta = f'<p class="meta"><time datetime="{x["date"]}">{x["date"]}</time>　{esc(name)}　{esc(label)}{esc(ev)}</p>'
        # 配图说明は中国語なので、日本語ページでは日本語の標題を代替テキストにする（簡体字を載せない）
        figs = "".join(f"<figure>{_post_img({**im, 'alt': x['titleJa']})}</figure>" for im in x["images"])
        body = (pagehead("ja", "/news/", items, esc(x["titleJa"]), x.get("summaryJa") or "", meta, img=False) +
                f'<div class="w content"><div class="layout"><article class="prose">{_paras(x["bodyJa"])}{figs}'
                f'<h2>{esc(name)}</h2><p>所在地：{esc(addr)}（{esc(access)}）<br>入塾相談：{TEL_JP}</p>'
                f'<p><a href="{x["path"]}">中国語版を読む</a>　<a href="/news/">← ニュース一覧</a></p></article>{SIDE["ja"]}</div></div>')
        art = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": x["titleJa"], "inLanguage": "ja",
               "datePublished": x.get("publishedAt"), "dateModified": x.get("updatedAt"), "author": {"@id": BASE + "/#org"},
               "publisher": {"@id": BASE + "/#org"}, "mainEntityOfPage": BASE + x["ja_path"],
               "contentLocation": {"@type": "Place", "name": name, "address": addr}}
        if x["images"]:
            art["image"] = [BASE + im["src"] + "-1600.jpg" for im in x["images"]]
        desc = (x.get("summaryJa") or re.sub(r"\s+", " ", x["bodyJa"]))[:120]
        emit("ja", x["ja_path"], x["titleJa"], desc, body, ld(bc("ja", items), art) + hreflang(x), priority="0.6")


def render_site_posts(posts):
    items = [(None, "日本校区动态")]
    lead = "东京、大阪、京都校区的活动、讲座、合格喜报和学员故事，由各校区老师撰写、校区负责人审核后发布。"
    body = (pagehead("zh", "/zh/news/", items, "日本校区动态", lead) +
            f'<div class="w content">{post_cards(posts, 60) or "<p>各校区的动态正在整理中。</p>"}'
            f'<p class="note" style="margin-top:28px">中国国内校区（成都、上海、杭州、广州、西安、武汉）的动态见 <a href="https://www.chinichi.com/campus/">中国官网</a>。</p></div>')
    emit("zh", "/zh/news/", "日本校区动态", "知日塾东京、大阪、京都校区的最新动态：活动讲座、合格喜报、学员故事。", body, ld(bc("zh", items)), priority="0.7")
    for x in posts:
        name, addr, access, tel = JP_CAMPUS_ZH[x["campusSlug"]]
        ja_link = f'<a href="{x["ja_path"]}" lang="ja">日本語版</a>　' if x.get("ja_path") else ""
        items = [("/zh/news/", "日本校区动态"), (None, x["title"])]
        ev = f'　活动时间：{x["eventAt"][:16].replace("T", " ")}' if x.get("eventAt") else ""
        meta = (f'<p class="meta">{esc(x["campus"])} · {esc(x.get("kindLabel") or "")}{" · " + esc(x["division"]) if x.get("division") else ""}'
                f' · <time datetime="{x["date"]}">{x["date"]}</time>{esc(ev)}</p>')
        figs = "".join(f"<figure>{_post_img(im)}" + (f"<figcaption>{esc(im['alt'])}</figcaption>" if im.get("alt") else "") + "</figure>"
                       for im in x["images"])
        art_body = (pagehead("zh", "/zh/news/", items, esc(x["title"]), x.get("summary") or "", meta, img=False) +
                    f'<div class="w content"><div class="layout"><article class="prose">{_paras(x["body"])}{figs}'
                    f'<h2>{esc(name)}</h2><p>地址：{esc(addr)}（{esc(access)}）<br>电话：{esc(tel)}</p>'
                    f'<p>{ja_link}<a href="/zh/news/">← 日本校区动态</a></p></article>{SIDE["zh"]}</div></div>')
        art = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": x["title"], "inLanguage": "zh-CN",
               "datePublished": x.get("publishedAt"), "dateModified": x.get("updatedAt"), "author": {"@id": BASE + "/#org"},
               "publisher": {"@id": BASE + "/#org"}, "mainEntityOfPage": BASE + x["path"],
               "contentLocation": {"@type": "Place", "name": name, "address": addr}}
        if x["images"]:
            art["image"] = [BASE + im["src"] + "-1600.jpg" for im in x["images"]]
        desc = (x.get("summary") or re.sub(r"\s+", " ", x["body"]))[:120]
        emit("zh", x["path"], x["title"], desc, art_body, ld(bc("zh", items), art) + hreflang(x), priority="0.6")


# ───────── 旧URLの転送（GitHub Pages はサーバー側301が使えないので、meta refresh + canonical） ─────────
def old_target(p, posts):
    for x in posts:
        if x["old"] == p:
            return x["path"]
    rules = [(r"^/course/?$", "/courses/"), (r"^/course1/", "/courses/undergraduate/"), (r"^/course2/", "/courses/graduate/"), (r"^/course3/", "/courses/art/"),
             (r"^/course4/", "/courses/music/"), (r"^/course5/", "/courses/sgu/"), (r"^/course6/", "/courses/eju/"), (r"^/case", "/results/"),
             (r"^/(news\d|new2)/", "/news/"), (r"^/team", "/teachers/"), (r"^/job", "/recruit/"), (r"^/xiaoqu", "/access/"),
             (r"^/(dingzhi|dzdetail)", "/courses/")]
    for pat, to in rules:
        if re.match(pat, p):
            return to
    return None


def render_redirects(posts):
    new = {x[0] for x in SITEMAP}
    olds = json.loads((SRC / "data" / "old_paths.json").read_text())
    olds += ["/corporate/index.html", "/corporate/university.html", "/corporate/recruit.html", "/corporate/training.html", "/corporate/results.html",
             "/corporate/bunri.html", "/corporate/art.html", "/corporate/acg.html", "/corporate/sports.html", "/privacy.html", "/index.html"]
    repo = {"/corporate/index.html": "/corporate/", "/corporate/university.html": "/corporate/university/", "/corporate/recruit.html": "/corporate/recruit/",
            "/corporate/training.html": "/corporate/training/", "/corporate/results.html": "/results/", "/corporate/bunri.html": "/courses/undergraduate/",
            "/corporate/art.html": "/courses/art/", "/corporate/acg.html": "/courses/acg/", "/corporate/sports.html": "/courses/sports/", "/privacy.html": "/privacy/"}
    n = 0
    for p in olds:
        if p in new or p in ("/", "/index.html") or (p.endswith("/index.html") and p[:-10] in new):
            continue  # 新しいページと同じファイルになるものは書かない（上書きすると自分自身へ転送してしまう）
        to = repo.get(p) or old_target(p, posts)
        if not to:
            continue
        dest = p if p.endswith(".html") else (p.rstrip("/") + "/")
        write(dest, f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><title>移動しました｜知日塾</title>'
                    f'<link rel="canonical" href="{BASE}{to}"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={to}">'
                    f'</head><body><p>このページは移動しました：<a href="{to}">{BASE}{to}</a></p></body></html>')
        n += 1
    return n


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "static", DIST / "static")
    shutil.copytree(ROOT / "assets", DIST / "assets", ignore=shutil.ignore_patterns("style.css"))
    (DIST / ".nojekyll").write_text("")
    jp_posts = site_posts.load(DIST)
    ja_posts = [x for x in jp_posts if x.get("ja_path")]
    posts = render_news(ja_posts)
    render_site_posts_ja(jp_posts)
    if jp_posts:
        NAV["zh"].insert(2, ("/zh/news/", "校区动态"))
    ja_feed = [{"path": x["ja_path"], "title": x["titleJa"], "date": x["date"], "category": ""} for x in ja_posts] + posts
    latest = {"ja": '<ul class="list">' + "".join(f'<li><a href="{x["path"]}"><span>{esc(x["title"])}</span><time>{x["date"] or x["category"]}</time></a></li>' for x in ja_feed[:6]) + "</ul>",
              "zh": ('<ul class="list">' + "".join(f'<li><a href="{x["path"]}"><span>【{esc(x["campus"])}】{esc(x["title"])}</span><time>{x["date"]}</time></a></li>' for x in jp_posts[:6]) + "</ul>") if jp_posts else ""}
    for lang in ("ja", "zh"):
        for p in sorted((SRC / lang).glob("*")):
            if p.suffix in (".md", ".html"):
                page = read_page(p, lang)
                if jp_posts and page["path"] == "/zh/access/":
                    page["body"] += f'<h2>日本校区最新动态</h2>{post_cards(jp_posts, 6)}<p><a href="/zh/news/">看全部日本校区动态 →</a></p>'
                if jp_posts and page["path"] == "/access/":
                    ja_list = "".join(f'<li><a href="{x["ja_path"]}"><span>{esc(x["titleJa"])}</span><time>{x["date"]}</time></a></li>' for x in ja_posts[:6])
                    page["body"] += ('<h2>各校舎からのお知らせ</h2>' + (f'<ul class="list">{ja_list}</ul>' if ja_list else "") +
                                     '<p>東京・大阪・京都の各校舎のイベント、説明会、合格のお知らせは、留学生向けに中国語でも掲載しています。</p>'
                                     '<p><a href="/zh/news/">校舎のお知らせ（中国語）を見る →</a></p>')
                render_page(page, latest)
    render_site_posts(jp_posts)
    render_frags()
    render_teachers()
    n = render_redirects(posts)
    urls = "".join(f"<url><loc>{BASE}{p}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>" for p, d, pr in SITEMAP)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n" if NOINDEX else f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
    write("/404.html", head("ja", "ページが見つかりません", "ページが見つかりません。", "/404.html", '<meta name="robots" content="noindex">') +
          '<main id="main"><section class="pagehead"><div class="w"><em class="tag">404</em><h1>ページが見つかりません</h1>'
          '<p class="lead">サイトをリニューアルしたため、ページの場所が変わった可能性があります。</p>'
          '<p style="margin-top:24px"><a class="btn" href="/">ホームへ</a>　<a href="/courses/">コース一覧</a>　<a href="/contact/">お問い合わせ</a></p></div></section></main>' + foot("ja"))
    print(f"完了：{len(SITEMAP)} ページ（日本の校舎の官网动态 {len(jp_posts)} 件）、旧URL転送 {n} 件 → {DIST}{'（SITE_PREFIX=' + PREFIX + '）' if PREFIX else ''}")


if __name__ == "__main__":
    main()
