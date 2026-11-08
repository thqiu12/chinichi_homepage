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
node --test tests/form-inquiry.test.js
```

## 今後のTODO

- [x] ロゴをローカル化(`assets/img/logo.png`)
- [x] 各事業の詳細ページ(`corporate/university.html` 他)
- [x] 共通トップ(学生/法人の2入口スプラッシュ)
- [ ] 問い合わせの受信先を接続する
      フォームは `POST /api/public/corporate-inquiry`（JSON）を想定する。
      `assets/config.js` の `CHINICHI_LEAD_ENDPOINT` は空。
      公開されている Graduate-student_CHINICHI_OS の main と既存ブランチに、このルートは無い。
      未設定・通信失敗・2xx 以外では成功と表示しない。入力は残し、ボタンを戻して再送できる。
      実在する受付URLが確定してから config に設定する。メール基盤は別途。
- [x] 公式グループ資料に基づく情報の正確化(代表略歴・数字・拠点・ブランド)
- [x] 理念 / グループ全体像 / 沿革 / 現場写真ギャラリーの追加
- [x] SEO基盤(OGP/Twitter・favicon・JSON-LD・canonical・robots・sitemap)
- [x] モバイル固定CTA / 電話 tel: リンク / プライバシーポリシー
- [x] アクセシビリティ(skip-link・focus-visible・alt・label)
- [ ] 提携大学ウォールを実ロゴ/フルリストに差し替え(現状6校+「60校以上」)
- [ ] 中国の国際高校(上海博雅・南通)のクリーン写真追加
- [ ] Astro/Next.js への載せ替え(ヘッダー/フッター重複の解消・CMS連携)

## ⚠ デプロイ前チェックリスト(本番化に必須)

1. **ドメイン置換**: 現在は公開URL `https://thqiu12.github.io/chinichi_homepage` で
   canonical/OGP/sitemap/robots を整合済み。独自ドメイン確定時に同URLを一括置換し、
   `CNAME` ファイル追加＋DNS設定（github.io へ CNAME）
2. **解析タグ有効化**: 各 `*.html` の `<head>` 末尾コメント内 GA4 (`G-XXXXXXXXXX`) と
   百度统计 (`BAIDU_SITE_ID`) を実IDに置換し、コメントを外す
3. **フォーム接続**: 実在する受付URLが分かってから `assets/config.js` の
   `CHINICHI_LEAD_ENDPOINT` に `https://<受付のドメイン>/api/public/corporate-inquiry` を設定する。
   空のまま公開しても成功とは表示されない。URLを決めるまでは法人窓口の電話を案内する。
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

受付側の保存形式はこのリポジトリからは確定できない。学生向けの項目へ B2B の問い合わせをそのまま入れないこと。

成功とみなす応答（このリポジトリで確認できる範囲）:

- HTTP ステータスが 2xx
- 本文が空、または JSON
- JSON オブジェクトの場合、`ok` と `success` が `false` ではない

本文の項目一覧は受付実装がこのリポジトリに無いため、それ以上は要求しない。
4xx / 5xx、通信失敗、HTML、壊れた JSON、`ok: false` / `success: false` は未達とし、成功とは表示しない。
