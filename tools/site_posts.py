"""chinichi_OS「官网动态」から、日本の校舎（東京・大阪・京都）の公開済み記事を取得する（サイト生成時に毎回）。

- 取得先：https://chinichi-os.com/api/public/site-posts（公開済みのみ。投稿者などの内部情報は含まない）
- 記事は各校舎のスタッフが中国語で書き、校舎の責任者が承認したもの → このサイトでは /zh/ 以下に載せる
  （日本語ページは中国語の本文を載せず、/zh/news/ へのリンクだけ。tools/check_site.py の簡体字チェックとも整合）
- 中国の6校舎の記事は中国語サイト www.chinichi.com の各校区ページに載る（ここには載せない）
- 画像は署名付きURL（1時間で失効）なので、生成時にダウンロードして _site/static/img/posts/ に置く
環境変数
  SITE_POSTS_API       取得先を変える（ローカル確認用）
  SITE_POSTS_FILE      API の代わりに JSON ファイルを読む（見本データで画面確認するとき。画像はダウンロードしない）
  SITE_POSTS_REQUIRED  1 のとき取得失敗でビルドを止める（本番デプロイ用：失敗したまま公開すると記事が一時的に消えるため）
"""
import io, json, os, re, sys, urllib.request
from pathlib import Path

API = os.environ.get("SITE_POSTS_API", "https://chinichi-os.com/api/public/site-posts")
JP_CAMPUSES = {"tokyo": "东京", "osaka": "大阪", "kyoto": "京都"}

try:
    from PIL import Image
except ImportError:
    Image = None


def _fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "chinichi-edu-build/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _save_image(data, out_dir, base):
    if Image is None:
        for w in (800, 1600):
            (out_dir / f"{base}-{w}.jpg").write_bytes(data)
        return True
    try:
        im = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:  # noqa: BLE001
        return False
    for w in (1600, 800):
        x = im.copy()
        x.thumbnail((w, w))
        x.save(out_dir / f"{base}-{w}.jpg", quality=80, optimize=True, progressive=True)
    return True


def load(dist: Path):
    """日本の校舎の公開済み記事（新しい順）。画像は dist/static/img/posts/ に保存し、src を書き換えて返す。"""
    local = os.environ.get("SITE_POSTS_FILE")
    try:
        data = json.loads(Path(local).read_text()) if local else json.loads(_fetch(API))
    except Exception as e:  # noqa: BLE001
        if os.environ.get("SITE_POSTS_REQUIRED") == "1":
            sys.exit(f"官网动态の取得に失敗したため中止します（公開中のサイトはそのまま）：{e}")
        print(f"  ! 官网动态を取得できませんでした（記事なしで生成）：{e}")
        return []
    out_dir = dist / "static" / "img" / "posts"
    out_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for p in data.get("items", []):
        if p.get("campusSlug") not in JP_CAMPUSES:
            continue
        pid = re.sub(r"[^a-z0-9]", "", p["id"].lower())
        imgs = []
        for k, im in enumerate(p.get("images") or []):
            if local:  # 見本データ：src にサイト内の写真パス（-800/-1600 を除いた形）が入っている
                imgs.append({"src": im["src"], "alt": im.get("alt", "")})
                continue
            try:
                ok = _save_image(_fetch(im["url"]), out_dir, f"{pid}-{k}")
            except Exception as e:  # noqa: BLE001
                print("  ! 画像の取得に失敗", p["id"], e)
                ok = False
            if ok:
                imgs.append({"src": f"/static/img/posts/{pid}-{k}", "alt": im.get("alt", "")})
        x = {k: p.get(k) for k in ("id", "campus", "campusSlug", "division", "kind", "kindLabel", "title", "summary", "body",
                                    "eventAt", "publishedAt", "updatedAt", "titleJa", "summaryJa", "bodyJa")}
        x.update(images=imgs, date=(p.get("publishedAt") or "")[:10], path=f"/zh/news/{pid}/", ja_path=None)
        # 日文版：標題と本文がそろい、Shift_JIS にない漢字（簡体字など）がないときだけ日本語ページを出す
        ja = f'{x.get("titleJa") or ""}{x.get("summaryJa") or ""}{x.get("bodyJa") or ""}'
        if x.get("titleJa") and x.get("bodyJa"):
            bad = sorted({c for c in ja if "一" <= c <= "鿿" and not c.encode("shift_jis", errors="ignore")})
            if bad:
                print(f"  ! 日文版に日本で使わない漢字 {''.join(bad)} があるため日本語ページは出しません：{p['id']}")
            else:
                x["ja_path"] = f"/news/s-{pid}/"
        items.append(x)
    return sorted(items, key=lambda x: x.get("publishedAt") or "", reverse=True)
