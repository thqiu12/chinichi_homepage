"""够用的 Markdown → HTML(只支持文章里用到的写法):
# 标题、段落、**粗体**、*斜体*、`代码`、[链接](url)、- / 1. 列表、> 引用、| 表格 |、---、```代码块```。"""
import html
import re


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"~~(.+?)~~", r"<del>\1</del>", s)
    def link(m):
        text, url = m.group(1), html.unescape(m.group(2))
        ext = url.startswith("http") and "chinichi.com" not in url
        attr = ' rel="noopener" target="_blank"' if ext else ""
        return f'<a href="{html.escape(url)}"{attr}>{text}</a>'
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)
    return s


def _table(lines):
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines]
    head, body = rows[0], [r for r in rows[2:]]
    out = ['<div class="table-wrap"><table>', "<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
    for r in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def to_html(md, shift=0):
    """shift: 标题降级(文章 H1 交给页面模板时,把 # 当 h2 用就传 1)"""
    lines = md.replace("\r\n", "\n").split("\n")
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1; continue
        if l.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)", l)
        if m:
            lv = min(6, len(m.group(1)) + shift)
            txt = m.group(2).strip()
            out.append(f"<h{lv}>{inline(txt)}</h{lv}>")
            i += 1; continue
        if re.match(r"^\s*(---|\*\*\*)\s*$", l):
            out.append("<hr>"); i += 1; continue
        if l.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            j = i
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                j += 1
            out.append(_table(lines[i:j])); i = j; continue
        if l.startswith(">"):
            j = i; buf = []
            while j < len(lines) and lines[j].startswith(">"):
                buf.append(lines[j][1:].lstrip()); j += 1
            out.append("<blockquote>" + to_html("\n".join(buf)) + "</blockquote>"); i = j; continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+", l)
        if m:
            ordered = m.group(2)[0].isdigit()
            tag = "ol" if ordered else "ul"
            items, j = [], i
            while j < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s+", lines[j]):
                txt = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[j])
                # 续行(缩进、非新列表项)
                k = j + 1
                while k < len(lines) and lines[k].startswith("  ") and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[k]):
                    txt += " " + lines[k].strip(); k += 1
                # 子列表(缩进的 - )
                sub = []
                while k < len(lines) and re.match(r"^\s{2,}([-*]|\d+\.)\s+", lines[k]):
                    sub.append(re.sub(r"^\s{2,}([-*]|\d+\.)\s+", "", lines[k])); k += 1
                li = inline(txt)
                if sub:
                    li += "<ul>" + "".join(f"<li>{inline(x)}</li>" for x in sub) + "</ul>"
                items.append(f"<li>{li}</li>"); j = k
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>"); i = j; continue
        buf = [l.strip()]; j = i + 1
        while j < len(lines) and lines[j].strip() and not re.match(r"^(#{1,6}\s|>|\||```|\s*([-*]|\d+\.)\s|\s*---\s*$)", lines[j]):
            buf.append(lines[j].strip()); j += 1
        out.append("<p>" + "<br>".join(inline(b) for b in buf) + "</p>")
        i = j
    return "\n".join(out)
