# chinichi_homepage — 知日塾 日本サイト（chinichi-edu.jp）

知日株式会社・知日塾の日本向けサイト。**学生向け（日本語）＋法人の方へ＋中国語版（/zh/）**を1サイトにまとめた静的サイトです。
デザインは中国語サイト www.chinichi.com と共通の「方案 G」（首屏は写真の自動切替）。

- 公開中（確認用）：https://thqiu12.github.io/chinichi_homepage/ （noindex）
- 本番予定：https://chinichi-edu.jp/ （現行サイトは Xserver 上の旧 CMS。切り替え手順は下記）

## 構成

```
build.py               サイト生成（python3 build.py → _site/）
src/ja/*.md|*.html     日本語ページ（1行目 <!--meta {...}-->。トップは 00-home.html）
src/zh/*               中国語ページ（/zh/）
src/frag/*.json        旧法人サイトの本文ブロック（tools/import_corp.py で取り込み済み）
src/data/teachers.json 講師（旧 chinichi-edu.jp から取り込み・写真は static/img/edu/）
src/data/posts.json    ニュース・合格速報（同上）
src/data/old_paths.json 旧 chinichi-edu.jp のURL一覧（新ページへ転送するページを生成）
static/                site.css / site.js（方案 G）、corp.css（法人ブロック用・tools/scope_css.py で生成）、写真
assets/                ロゴ・ファビコン・問い合わせフォーム（form.js / config.js）・reveal.js・旧 style.css（corp.css の元）
tools/                 取り込み・チェック用スクリプト
tests/                 フォーム送信のテスト（node --test tests/form-inquiry.test.js）
```

ページ一覧：トップ、知日について、コース一覧＋8コース（学部・大学院・美術・ACG・音楽・スポーツ・EJU・SGU）、合格実績、講師紹介、拠点・アクセス、
ニュース（7件）、採用情報、お問い合わせ、プライバシーポリシー、法人の方へ（トップ・大学提携・人材紹介・法人研修）、中国語トップ・中国語アクセス。

旧 chinichi-edu.jp のURL（/course1/、/team/、/xiaoqu/ など119件）と旧法人ページ（corporate/*.html）は、新しいページへ転送するページを自動生成します
（GitHub Pages ではサーバー側の301が使えないため meta refresh ＋ canonical）。

## 更新のしかた

1. `src/ja/` の md を直す、または `src/frag/*.json` の該当ブロックを直す
2. `python3 build.py && python3 tools/check_site.py`（リンク切れと簡体字の混入を確認）
3. main にマージすると GitHub Actions が生成・公開します（PR ではテストと生成だけ実行）

日本語ページに中国語由来の言い方（校内考・班主任・〜枚の合格など）が入らないよう、`build.py` の `JA_TEXT_FIX` で直しています。

## 独自ドメイン（chinichi-edu.jp）への切り替え

**注意：現在 chinichi-edu.jp には MX レコードがなく、メールはドメインの A レコード（Xserver）宛てに届いています。
A レコードを GitHub に向ける前に、必ず MX レコードを追加してください。追加しないと @chinichi-edu.jp のメールが届かなくなります。**

1. Xserver の DNS 設定で、まず MX を追加：`chinichi-edu.jp  MX  10  sv13019.xserver.jp`（Xserver のメールサーバー名は管理画面で確認）
2. A レコードを GitHub Pages に変更（4本）：`185.199.108.153` / `185.199.109.153` / `185.199.110.153` / `185.199.111.153`
3. `www` は CNAME `thqiu12.github.io.`
4. このリポジトリで `static/CNAME`（中身 `chinichi-edu.jp`）を追加し、リポジトリ変数 `SITE_PREFIX` を空文字に設定、Pages の Custom domain に `chinichi-edu.jp` を入れて HTTPS を有効化
5. Google Search Console（TXT の確認コードは残っています）でサイトマップ `https://chinichi-edu.jp/sitemap.xml` を送信

## 未確定・要確認

- 問い合わせフォームの送信先（`assets/config.js` の `CHINICHI_LEAD_ENDPOINT`）は未設定。空のままだと「届いていない」と表示され、成功とは表示しません。
- 解析タグ（GA4・百度统计）は未設定。
- 拠点の住所で中国語サイトと食い違う箇所（上海の部屋番号、京都のビル名）は、確認が取れるまで記載していません。
- 学生の写真（学部コースの見出し、トップの写真帯「日本での生活」）は本人の掲載同意を確認すること。
