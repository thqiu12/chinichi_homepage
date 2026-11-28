# chinichi-edu.jp を新サイトへ切り替える手順（Xserver の DNS 設定）

新しいサイトは GitHub Pages で公開済みです（確認用：https://thqiu12.github.io/chinichi_homepage/ ）。
Xserver の「サーバーパネル → DNSレコード設定」で、**次の順番どおりに**変更してください。

## ① 先に MX レコードを追加（メールを止めないため・最初に必ず）

いま chinichi-edu.jp には MX レコードがなく、メールはドメインの A レコード（Xserver）宛てに届いています。
A レコードを先に変えると、@chinichi-edu.jp のメールが届かなくなります。

| ホスト名 | 種別 | 内容 | 優先度 |
|---|---|---|---|
| chinichi-edu.jp | MX | sv13019.xserver.jp | 10 |

※ メールサーバー名はサーバーパネルの「サーバー情報」で確認してください（sv13019 でなければ表示どおりに）。

## ② A レコードを GitHub Pages に変更

既存の `chinichi-edu.jp  A  162.43.116.20` を削除し、次の4件を追加：

| ホスト名 | 種別 | 内容 |
|---|---|---|
| chinichi-edu.jp | A | 185.199.108.153 |
| chinichi-edu.jp | A | 185.199.109.153 |
| chinichi-edu.jp | A | 185.199.110.153 |
| chinichi-edu.jp | A | 185.199.111.153 |

## ③ www を CNAME に

既存の `www.chinichi-edu.jp  A  162.43.116.20` を削除し、次を追加：

| ホスト名 | 種別 | 内容 |
|---|---|---|
| www.chinichi-edu.jp | CNAME | thqiu12.github.io |

## 変更しないもの

- TXT レコード（SPF と Google の所有権確認 2件）はそのまま残してください。

## 変更後

設定が終わったら連絡してください。こちらで GitHub 側の独自ドメイン設定・HTTPS の有効化・確認用パスの解除を行い、全ページを確認します。
反映には数分〜数時間かかることがあります。

---

## 中文版（给负责改 DNS 的同事）

在 Xserver「サーバーパネル → DNSレコード設定」按顺序改：

1. **先加 MX**：`chinichi-edu.jp  MX  sv13019.xserver.jp  优先度10`（邮件服务器名以后台「サーバー情報」为准）。不先加这条，公司邮件会收不到。
2. **A 记录改成 GitHub**：删掉 `162.43.116.20`，加 4 条 A：`185.199.108.153`、`185.199.109.153`、`185.199.110.153`、`185.199.111.153`。
3. **www 改 CNAME**：删掉 www 的 A 记录，加 `www.chinichi-edu.jp  CNAME  thqiu12.github.io`。
4. TXT 记录（SPF、Google 验证）不要动。改完通知我们。
