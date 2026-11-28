/* サイト共通設定
   法人問い合わせフォームの送信先（chinichi_OS の公開受付口）。
   POST /api/public/corporate-inquiry（JSON）。受け付けたリードは CRM の資源公海に入る。
   空にすると送信せず、画面には「届いていない」と出す（成功とは表示しない）。
   成功と表示するのは、このURLへの POST が HTTP 2xx で、
   本文が空または JSON、かつ ok / success が false でないときだけ。
   2026-11-28 chinichi_OS 側の受付口が本番稼働したので設定した。 */
window.CHINICHI_LEAD_ENDPOINT = "https://chinichi-os.com/api/public/corporate-inquiry";
