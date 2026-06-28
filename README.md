# chinichi_homepage

知日株式会社のコーポレートサイト。**1サイト・2入口**構成(学生の方へ / 法人の方へ)の
うち、まず**法人向け面**の初版を実装。

## 構成

```
index.html                  共通トップ(2入口スプラッシュ:学生 / 法人)
privacy.html                プライバシーポリシー
robots.txt / sitemap.xml    SEO
corporate/
  index.html                法人向けコーポレートトップ
  university.html           大学提携・留学生送り出し
  recruit.html              人材紹介・採用支援
  training.html             法人研修・語学
assets/
  style.css                 スタイル
  config.js                 リード送信先エンドポイント設定
  form.js                   問い合わせフォーム送信処理(共通)
  favicon*.png / .ico / apple-touch-icon.png   ファビコン
  img/logo.png              ロゴ(現行サイトから取得しローカル化)
  img/og.jpg                OGP用 1200x630 画像
  img/daihyou.jpg           代表写真
  img/photos/               校舎・スタジオ・沿革等の実写真
```

学生サイト本体は既存の chinichi-edu.jp(別CMS)を参照。スプラッシュの「学生の方へ」はそちらへ遷移します。
※ 中国進出・越境ECコンサルは未実施のため掲載していません。

## デザインの根拠(現行サイトから踏襲)

現行サイト [chinichi-edu.jp](https://chinichi-edu.jp/) の実データから抽出:

- 配色: navy `#002f7f`(主) / red `#e3360b`(差し色)
- フォント: Noto Sans JP
- ロゴ・法人窓口(03-6205-9570)・実績数値・拠点・ブランド群は実データを使用

## ローカル確認

```
python3 -m http.server 4178
# → http://localhost:4178
```

## 今後のTODO

- [x] ロゴをローカル化(`assets/img/logo.png`)
- [x] 各事業の詳細ページ(`corporate/university.html` 他)
- [x] 共通トップ(学生/法人の2入口スプラッシュ)
- [x] 問い合わせ通知 API を chinichi_OS に新設(`POST /api/public/corporate-inquiry`)
      DBには落とさず、新規問い合わせを站内通知＋企業微信で法人窓口(既定 ADMIN ロール)へ通知。
      メールは chinichi_OS にメール基盤が無いため未対応(後付け可)。
      → 接続するには `assets/config.js` の `CHINICHI_LEAD_ENDPOINT` にそのURLを設定するだけ。
- [x] 公式グループ資料に基づく情報の正確化(代表略歴・数字・拠点・ブランド)
- [x] 理念 / グループ全体像 / 沿革 / 現場写真ギャラリーの追加
- [x] SEO基盤(OGP/Twitter・favicon・JSON-LD・canonical・robots・sitemap)
- [x] モバイル固定CTA / 電話 tel: リンク / プライバシーポリシー
- [x] アクセシビリティ(skip-link・focus-visible・alt・label)
- [ ] 提携大学ウォールを実ロゴ/フルリストに差し替え(現状6校+「60校以上」)
- [ ] 中国の国際高校(上海博雅・南通)のクリーン写真追加
- [ ] Astro/Next.js への載せ替え(ヘッダー/フッター重複の解消・CMS連携)

## ⚠ デプロイ前チェックリスト(本番化に必須)

1. **ドメイン置換**: 仮ドメイン `https://corp.chinichi-edu.jp` を本番ドメインに一括置換
   （`*.html` の canonical/OGP、`sitemap.xml`、`robots.txt`）
2. **解析タグ有効化**: 各 `*.html` の `<head>` 末尾コメント内 GA4 (`G-XXXXXXXXXX`) と
   百度统计 (`BAIDU_SITE_ID`) を実IDに置換し、コメントを外す
3. **フォーム接続**: `assets/config.js` の `CHINICHI_LEAD_ENDPOINT` に
   `https://<chinichi_OSドメイン>/api/public/corporate-inquiry` を設定
4. **CORS**: chinichi_OS 側で `CORPORATE_INQUIRY_ALLOW_ORIGIN` を本番ドメインに設定
5. **（任意）パフォーマンス**: Noto Sans JP のサブセット自前ホスト、Tabler を使用アイコンのみに、
   画像の WebP 化(現状は jpg/png でローカル最適化済み)

## リード連携の設計メモ

法人問い合わせフォームの payload(`assets/form.js`):

```json
{
  "source": "website-corporate",
  "page": "/corporate/index.html",
  "company": "", "dept": "", "name": "", "email": "", "tel": "",
  "topic": "大学提携・留学生送り出し | 人材紹介・採用支援 | 法人研修・語学 | その他",
  "message": ""
}
```

chinichi_OS の `Lead` は学生向け(顧問/SALES・JLPT・学校 等)の形のため、B2B 問い合わせをそのまま入れると意味が崩れる。
公開受付APIでは「source=官網法人」でタグ付けし、未割当(プール)として作成 → 站内通知/企業微信で通知、等の設計を推奨(要相談)。
