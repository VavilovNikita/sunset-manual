import re, sys, os, html, glob
# usage: updates.py <site dir>
# Builds the "What's new" pages from src/updates/<date>-<slug>.<lang>.html:
#   <site>/<lang>/updates/index.html          the list, newest first
#   <site>/<lang>/updates/<date>-<slug>.html  one page per release
# A release file starts with a comment block:
#   <!--
#   title: Booking tracker
#   summary: One line for the list.
#   -->
# and then the body. In the body, {manual} stands for the manual page of the same language
# (write {manual}#booking-tracker) and {img} for the screenshots folder (write {img}a-foo.jpg).
site = sys.argv[1]
d = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
LANGS = ("en", "th")
T = {
    "en": {"title": "Sunset Staff Manual", "new": "What's new", "back": "Back to the manual", "intro": "What changed in each release of the system, newest first. Each note says who it is for and links to the manual section it changes.",
           "only": {"en": "English only", "th": "Thai only"}, "prev": "Older", "next": "Newer", "other": "ภาษาไทย", "own": "English", "none": "No release notes yet.", "contents": "Releases"},
    "th": {"title": "คู่มือระบบ Sunset", "new": "มีอะไรใหม่", "back": "กลับไปที่คู่มือ", "intro": "สิ่งที่เปลี่ยนในแต่ละรุ่นของระบบ เรียงจากใหม่ไปเก่า แต่ละหัวข้อบอกว่าเหมาะกับใคร และลิงก์ไปยังส่วนของคู่มือที่เปลี่ยน",
           "only": {"en": "ภาษาอังกฤษเท่านั้น", "th": "ภาษาไทยเท่านั้น"}, "prev": "รุ่นก่อนหน้า", "next": "รุ่นถัดไป", "other": "ภาษาไทย", "own": "English", "none": "ยังไม่มีบันทึกรุ่น", "contents": "รุ่น"},
}
MONTHS = {"en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
          "th": ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]}
# Same Google Fonts link as assemble.py.
fonts = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..600;1,9..144,400..600&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+Thai:wght@400;500;600;700&family=Noto+Serif+Thai:wght@400;500;600&family=Work+Sans:wght@400;500;600;700&display=swap">'
css = open(d + "style.css.part", encoding="utf-8").read() + "\n" + open(d + "updates.css.part", encoding="utf-8").read()
try:
    from PIL import Image
except ImportError:
    Image = None
imgdir = os.path.join(site, "img")

def fmt_date(iso, lang):
    y, m, dd = (int(x) for x in iso.split("-"))
    return f"{dd} {MONTHS[lang][m - 1]} {y}"

# release -> {lang: {title, summary, body}}
releases = {}
for path in sorted(glob.glob(d + "updates/*.html")):
    m = re.match(r"(\d{4}-\d{2}-\d{2}-[a-z0-9-]+)\.(en|th)\.html$", os.path.basename(path))
    if not m:
        sys.exit(f"bad release file name: {path} (want YYYY-MM-DD-slug.en.html / .th.html)")
    slug, lang = m.group(1), m.group(2)
    text = open(path, encoding="utf-8").read()
    head = re.match(r"\s*<!--(.*?)-->", text, re.S)
    meta = dict(re.findall(r"^\s*(title|summary):\s*(.+?)\s*$", head.group(1), re.M)) if head else {}
    if "title" not in meta or "summary" not in meta:
        sys.exit(f"{path}: the comment block at the top needs title: and summary:")
    releases.setdefault(slug, {})[lang] = {"title": meta["title"], "summary": meta["summary"], "body": text[head.end():].strip()}
order = sorted(releases, reverse=True)  # newest first; the date is the start of the slug

def link_to(slug, lang, from_lang):
    """href from a page under <from_lang>/updates/ to the release as shown in lang (falls back to the other language)."""
    have = lang if lang in releases[slug] else next(iter(releases[slug]))
    return ("" if have == from_lang else f"../../{have}/updates/") + slug + ".html"

def entry(slug, lang):
    """The release as read in lang: its own text, or the other language's text when there is none."""
    have = lang if lang in releases[slug] else next(iter(releases[slug]))
    return releases[slug][have], have

def badge(slug, lang):
    have = entry(slug, lang)[1]
    return f' <span class="only">{T[lang]["only"][have]}</span>' if have != lang else ""

def page(lang, main, switch_href, switch_label_lang, current=None):
    t = T[lang]
    toc = "".join(
        f'<li><a href="{link_to(s, lang, lang)}"' + (' aria-current="page"' if s == current else "") + f'>{html.escape(entry(s, lang)[0]["title"])}</a></li>'
        for s in order) or f'<li>{t["none"]}</li>'
    # The language switch goes to the same release in the other language, or to that language's list.
    switch = ""
    for code in LANGS:
        label = T[code]["own"] if code == "en" else T[code]["other"]
        switch += f'<a aria-current="page">{label}</a>' if code == lang else f'<a href="{switch_href(code)}">{label}</a>'
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<title>{t["new"]} - {t["title"]}</title>
{fonts}
{css}
<style>.wrap[lang="th"] h1, .wrap[lang="th"] h3, .wrap[lang="th"] .num, .wrap[lang="th"] i {{ font-style: normal; }} .wrap[lang="th"] h3 {{ font-weight: 600; }} body {{ margin: 0; }} img {{ max-width: 100%; }}</style>
</head>
<body>
<div class="wrap" lang="{lang}">
<nav class="toc" aria-label="{t["contents"]}">
<div class="lang">{switch}</div>
<p class="back"><a href="../index.html">&larr; {t["back"]}</a></p>
<details open><summary><a href="index.html">{t["new"]}</a></summary><ol>{toc}</ol></details>
</nav>
<main>
{main}
</main>
</div>
</body>
</html>
'''

def sized(body):
    def dims(m):
        if Image:
            try:
                w, h = Image.open(os.path.join(imgdir, m.group(1))).size
                return f'src="../../img/{m.group(1)}" width="{w}" height="{h}"'
            except OSError:
                pass
        return f'src="../../img/{m.group(1)}"'
    body = re.sub(r'src="\{img\}([^"]+)"', dims, body)
    return body.replace("{manual}", "../index.html")

count = 0
for lang in LANGS:
    t = T[lang]
    outdir = os.path.join(site, lang, "updates")
    os.makedirs(outdir, exist_ok=True)
    for stale in glob.glob(outdir + "/*.html"):
        os.remove(stale)  # a removed release note disappears from the site too
    items = []
    for slug in order:
        e, have = entry(slug, lang)
        items.append(f'<li><a class="rel" href="{link_to(slug, lang, lang)}"><span class="date">{fmt_date(slug[:10], lang)}</span><span class="rt">{html.escape(e["title"])}{badge(slug, lang)}</span><span class="rs">{html.escape(e["summary"])}</span></a></li>')
    listing = f'<h1>{t["new"]}</h1><p class="lead">{t["intro"]}</p>' + (f'<ol class="releases">{"".join(items)}</ol>' if items else f'<p>{t["none"]}</p>')
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(
        page(lang, listing, lambda code: f"../../{code}/updates/index.html" if code != lang else "index.html", lang))
    for i, slug in enumerate(order):
        if lang not in releases[slug]:
            continue  # the other language's page is the one that exists
        e = releases[slug][lang]
        newer = order[i - 1] if i > 0 else None
        older = order[i + 1] if i + 1 < len(order) else None
        pn = ""
        if older: pn += f'<a class="prev" href="{link_to(older, lang, lang)}">&larr; {t["prev"]}: {html.escape(entry(older, lang)[0]["title"])}</a>'
        if newer: pn += f'<a class="next" href="{link_to(newer, lang, lang)}">{t["next"]}: {html.escape(entry(newer, lang)[0]["title"])} &rarr;</a>'
        main = (f'<article class="update"><p class="eyebrow">{fmt_date(slug[:10], lang)}</p><h1>{html.escape(e["title"])}</h1>\n{sized(e["body"])}\n</article>'
                f'<div class="pn">{pn}</div><p class="top"><a href="../index.html">&larr; {t["back"]}</a> &middot; <a href="index.html">{t["new"]}</a></p>')
        other = "th" if lang == "en" else "en"
        def sw(code, slug=slug, lang=lang):
            if code == lang: return slug + ".html"
            return f"../../{code}/updates/" + (slug + ".html" if code in releases[slug] else "index.html")
        open(os.path.join(outdir, slug + ".html"), "w", encoding="utf-8").write(page(lang, main, sw, lang, current=slug))
        count += 1
print(f"{len(order)} releases, {count} pages")
