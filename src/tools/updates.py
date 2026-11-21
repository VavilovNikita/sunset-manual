import re, sys, os, html, glob, datetime
# usage: updates.py <site dir>
# Builds the "What's new" pages from src/updates/<monday>-week.<lang>.html - ONE file per hotel week (Monday-Sunday,
# Asia/Bangkok), named by that week's Monday:
#   <site>/<lang>/updates/index.html          the list, grouped by month, newest first
#   <site>/<lang>/updates/<monday>-week.html  one page per week
# The body is made of <section data-area="..."> blocks in the order of the admin menu (front-desk, rooms, restaurant,
# spa, gym-lighting, staff, reports, then pos and guest-site); an empty area is simply left out. Each section has
# <h4>New</h4> (what staff do differently: role + {manual} link) and <h4>Fixed</h4> (one line per fix), New first. The
# area heading is added here, from the data-area. Anything after the sections (a note box) is kept as is.
# src/updates/redirects.txt ("old-slug -> <monday>-week" per line) keeps the addresses of earlier release pages alive.
# A release file starts with a comment block:
#   <!--
#   title: Week of 16 November 2026
#   summary: One line for the list.
#   -->
# and then the body. In the body, {manual} stands for the manual page of the same language
# (write {manual}#booking-tracker) and {img} for the screenshots folder (write {img}a-foo.jpg).
site = sys.argv[1]
d = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
LANGS = ("en", "th")
T = {
    "en": {"title": "Sunset Staff Manual", "new": "What's new", "back": "Back to the manual", "intro": "What changed in the system, one note per week, newest first. Inside a week the changes are grouped by area of the system, as New (what staff do differently, with who it is for and a link to the manual) and Fixed.",
           "only": {"en": "English only", "th": "Thai only"}, "prev": "Older", "next": "Newer", "other": "ภาษาไทย", "own": "English", "none": "No release notes yet.", "contents": "Releases", "weekof": "Week of", "moved": "This note moved to"},
    "th": {"title": "คู่มือระบบ Sunset", "new": "มีอะไรใหม่", "back": "กลับไปที่คู่มือ", "intro": "สิ่งที่เปลี่ยนในระบบ หนึ่งบันทึกต่อสัปดาห์ เรียงจากใหม่ไปเก่า ภายในสัปดาห์จัดกลุ่มตามส่วนของระบบ เป็น ใหม่ (สิ่งที่พนักงานทำต่างไป พร้อมบอกว่าเหมาะกับใครและลิงก์ไปยังคู่มือ) และ แก้ไขแล้ว",
           "only": {"en": "ภาษาอังกฤษเท่านั้น", "th": "ภาษาไทยเท่านั้น"}, "prev": "รุ่นก่อนหน้า", "next": "รุ่นถัดไป", "other": "ภาษาไทย", "own": "English", "none": "ยังไม่มีบันทึกรุ่น", "contents": "รุ่น", "weekof": "สัปดาห์ที่", "moved": "บันทึกนี้ย้ายไปที่"},
}
# data-area -> label per language, in the order they must appear (the admin menu, then the phone and the guest site).
AREAS = [
    ("front-desk", {"en": "Front desk", "th": "ฝ่ายต้อนรับ"}),
    ("rooms", {"en": "Rooms", "th": "ห้องพัก"}),
    ("restaurant", {"en": "Restaurant", "th": "ร้านอาหาร"}),
    ("spa", {"en": "Spa", "th": "สปา"}),
    ("gym-lighting", {"en": "Gym & lighting", "th": "ยิมและไฟ"}),
    ("staff", {"en": "Staff", "th": "พนักงาน"}),
    ("reports", {"en": "Reports", "th": "รายงาน"}),
    ("pos", {"en": "Phone (POS)", "th": "โทรศัพท์ (POS)"}),
    ("guest-site", {"en": "Guests", "th": "แขก"}),
]
SUBS = {"en": ("New", "Fixed"), "th": ("ใหม่", "แก้ไขแล้ว")}
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

def structure(path, lang, body):
    """Checks the area sections (known area, menu order, New before Fixed) and puts the area heading in each."""
    new_label, fixed_label = SUBS[lang]
    labels = dict(AREAS)
    names = [a for a, _ in AREAS]
    seen = -1
    def one(m):
        nonlocal seen
        area = m.group(1)
        if area not in labels:
            sys.exit(f"{path}: unknown data-area \"{area}\" (use one of: {', '.join(names)})")
        pos = names.index(area)
        if pos <= seen:
            sys.exit(f"{path}: area \"{area}\" is repeated or out of menu order (order: {', '.join(names)})")
        seen = pos
        inner = m.group(2)
        heads = re.findall(r"<h4>(.*?)</h4>", inner)
        if heads not in ([new_label], [fixed_label], [new_label, fixed_label]):
            sys.exit(f"{path}: section \"{area}\" needs <h4>{new_label}</h4> and/or <h4>{fixed_label}</h4> (New first, each once), nothing else as h4")
        return f'<section data-area="{area}"><h3 class="area">{html.escape(labels[area][lang])}</h3>{inner}</section>'
    out = re.sub(r'<section data-area="([^"]*)">(.*?)</section>', one, body, flags=re.S)
    if "<section" not in out:
        sys.exit(f"{path}: no <section data-area=...> block")
    return out

# release -> {lang: {title, summary, body}}
releases = {}
for path in sorted(glob.glob(d + "updates/*.html")):
    m = re.match(r"(\d{4}-\d{2}-\d{2})-week\.(en|th)\.html$", os.path.basename(path))
    if not m:
        sys.exit(f"bad release file name: {path} (want <monday>-week.en.html / .th.html, one file per hotel week)")
    day = datetime.date.fromisoformat(m.group(1))
    if day.weekday() != 0:
        monday = day - datetime.timedelta(days=day.weekday())
        sys.exit(f"{path}: {day} is not a Monday - the file of that week is named {monday}-week.{m.group(2)}.html")
    slug, lang = m.group(1) + "-week", m.group(2)
    text = open(path, encoding="utf-8").read()
    head = re.match(r"\s*<!--(.*?)-->", text, re.S)
    meta = dict(re.findall(r"^\s*(title|summary):\s*(.+?)\s*$", head.group(1), re.M)) if head else {}
    if "title" not in meta or "summary" not in meta:
        sys.exit(f"{path}: the comment block at the top needs title: and summary:")
    releases.setdefault(slug, {})[lang] = {"title": meta["title"], "summary": meta["summary"], "body": structure(path, lang, text[head.end():].strip())}
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
    months = []  # [(YYYY-MM, [li, ...])], newest first (order is already newest first)
    for slug in order:
        e, have = entry(slug, lang)
        li = f'<li><a class="rel" href="{link_to(slug, lang, lang)}"><span class="date">{t["weekof"]} {fmt_date(slug[:10], lang)}</span><span class="rt">{html.escape(e["title"])}{badge(slug, lang)}</span><span class="rs">{html.escape(e["summary"])}</span></a></li>'
        if not months or months[-1][0] != slug[:7]:
            months.append((slug[:7], []))
        months[-1][1].append(li)
    def month_title(key):
        y, mo = key.split("-")
        return f"{MONTHS[lang][int(mo) - 1]} {y}"
    listing = f'<h1>{t["new"]}</h1><p class="lead">{t["intro"]}</p>' + (
        "".join(f'<h2 class="month">{month_title(k)}</h2><ol class="releases">{"".join(lis)}</ol>' for k, lis in months) if months else f'<p>{t["none"]}</p>')
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
        main = (f'<article class="update"><p class="eyebrow">{t["weekof"]} {fmt_date(slug[:10], lang)}</p><h1>{html.escape(e["title"])}</h1>\n{sized(e["body"])}\n</article>'
                f'<div class="pn">{pn}</div><p class="top"><a href="../index.html">&larr; {t["back"]}</a> &middot; <a href="index.html">{t["new"]}</a></p>')
        other = "th" if lang == "en" else "en"
        def sw(code, slug=slug, lang=lang):
            if code == lang: return slug + ".html"
            return f"../../{code}/updates/" + (slug + ".html" if code in releases[slug] else "index.html")
        open(os.path.join(outdir, slug + ".html"), "w", encoding="utf-8").write(page(lang, main, sw, lang, current=slug))
        count += 1
# Earlier release pages (one per release, before the weekly notes) keep their address: a stub that sends on to the week.
redirects = os.path.join(d, "updates", "redirects.txt")
stubs = 0
if os.path.exists(redirects):
    for line in open(redirects, encoding="utf-8").read().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        old, _, new = (x.strip() for x in line.partition("->"))
        if new not in releases:
            sys.exit(f"redirects.txt: {old} -> {new}: there is no such week")
        for lang in LANGS:
            target, have = entry(new, lang)
            href = link_to(new, lang, lang)
            open(os.path.join(site, lang, "updates", old + ".html"), "w", encoding="utf-8").write(
                f'<!doctype html>\n<html lang="{lang}"><head><meta charset="utf-8"><meta name="robots" content="noindex, nofollow">'
                f'<meta http-equiv="refresh" content="0; url={href}"><link rel="canonical" href="{href}"><title>{html.escape(target["title"])}</title></head>'
                f'<body><p>{T[lang]["moved"]} <a href="{href}">{html.escape(target["title"])}</a>.</p></body></html>\n')
            stubs += 1
print(f"{len(order)} releases, {count} pages, {stubs} redirect stubs")
