/* サイト共通設定
   法人問い合わせフォームの送信先(chinichi_OS の公開受付API)。
   設定すると、新規問い合わせが站内通知＋企業微信で法人窓口(既定: ADMIN ロール)に届きます。
   未設定の間は「成功表示のみ」のフォールバック動作になります。

   エンドポイント: POST /api/public/corporate-inquiry
   - ローカル開発: "http://localhost:3000/api/public/corporate-inquiry"
   - 本番:         "https://<chinichi_OSのドメイン>/api/public/corporate-inquiry"
                   (例: https://os.chinichi.com/... ／ 実ドメインに合わせて設定)
   ※ chinichi_OS 側で CORPORATE_INQUIRY_ALLOW_ORIGIN を官網ドメインに設定推奨。 */
window.CHINICHI_LEAD_ENDPOINT = "";
