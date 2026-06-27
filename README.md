# chinichi_homepage

知日株式会社のコーポレートサイト。**1サイト・2入口**構成(学生の方へ / 法人の方へ)の
うち、まず**法人向け面**の初版を実装。

## 構成

```
index.html                  共通トップ(2入口スプラッシュ:学生 / 法人)
corporate/
  index.html                法人向けコーポレートトップ
  university.html           大学提携・留学生送り出し
  recruit.html              人材紹介・採用支援
  training.html             法人研修・語学
  consulting.html           中国進出・越境ECコンサル
assets/
  style.css                 スタイル
  config.js                 リード送信先エンドポイント設定
  form.js                   問い合わせフォーム送信処理(共通)
  img/logo.png              ロゴ(現行サイトから取得しローカル化)
```

学生サイト本体は既存の chinichi-edu.jp(別CMS)を参照。スプラッシュの「学生の方へ」はそちらへ遷移します。

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
- [ ] 提携大学・取引企業のロゴウォール素材差し替え
- [ ] ヒーロー/事業の写真素材を追加(現状はテキスト中心)
- [ ] Next.js への載せ替え検討(SSG/ISR・CMS連携)

## リード連携の設計メモ

法人問い合わせフォームの payload(`assets/form.js`):

```json
{
  "source": "website-corporate",
  "page": "/corporate/index.html",
  "company": "", "dept": "", "name": "", "email": "", "tel": "",
  "topic": "大学提携・留学生送り出し | 人材紹介・採用支援 | 法人研修・語学 | 中国進出・ECコンサル | その他",
  "message": ""
}
```

chinichi_OS の `Lead` は学生向け(顧問/SALES・JLPT・学校 等)の形のため、B2B 問い合わせをそのまま入れると意味が崩れる。
公開受付APIでは「source=官網法人」でタグ付けし、未割当(プール)として作成 → 站内通知/企業微信で通知、等の設計を推奨(要相談)。
