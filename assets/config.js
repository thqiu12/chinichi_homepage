/* サイト共通設定
   法人問い合わせフォームの送信先。
   空のときは送信せず、画面には「届いていない」と出す（成功とは表示しない）。
   受け付ける想定は POST /api/public/corporate-inquiry（JSON）。
   本リポジトリだけでは実在する受付URLを確定できない。
   公開されている関連システムにも当該ルートは無いため、初期値は空のままにする。
   実在するURLが分かってから、空文字をそのURLへ置き換える。
   パスは /api/public/corporate-inquiry を想定する。
   成功と表示するのは、そのURLへの POST が HTTP 2xx で、
   本文が空または JSON、かつ ok / success が false でないときだけ。 */
window.CHINICHI_LEAD_ENDPOINT = "";
