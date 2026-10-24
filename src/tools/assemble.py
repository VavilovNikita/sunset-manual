import re, sys, html
# usage: assemble.py <lang en|th> <other_url_or_empty>
lang, other = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
standalone = len(sys.argv) > 3 and sys.argv[3] == "site"
import os
d = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"
body = open(d + f"body-{lang}.html", encoding="utf-8").read()
css = open(d + "style.css.part", encoding="utf-8").read()
title = {"en": "Sunset Staff Manual", "th": "คู่มือระบบ Sunset"}[lang]
toc_label = {"en": "Contents", "th": "สารบัญ"}[lang]
items, cur = [], None
for m in re.finditer(r'<h([23])[^>]*id="([^"]+)"[^>]*>(.*?)</h\1>', body, re.S):
    lvl, i, t = m.group(1), m.group(2), m.group(3)
    t = re.sub(r'<span class="num">(.*?)</span>', r'\1. ', t)
    t = re.sub(r'<[^>]+>', '', t).strip()
    if lvl == "2":
        cur = [i, t, []]; items.append(cur)
    elif cur: cur[2].append((i, t))
toc = []
for i, t, subs in items:
    s = f'<li><a href="#{i}">{t}</a>'
    if subs: s += "<ol>" + "".join(f'<li><a href="#{a}">{b}</a></li>' for a, b in subs) + "</ol>"
    toc.append(s + "</li>")
def langlink(code, label):
    if code == lang: return f'<a aria-current="page">{label}</a>'
    return f'<a href="{other}" target="_blank" rel="noopener">{label}</a>' if other else ""
switch = langlink("en", "English") + langlink("th", "ภาษาไทย")
fonts = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400..600;1,9..144,400..600&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+Thai:wght@400;500;600;700&family=Noto+Serif+Thai:wght@400;500;600&family=Work+Sans:wght@400;500;600;700&display=swap">'
out = f'''<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
{fonts}
{css}
<style>.wrap[lang="th"] h1, .wrap[lang="th"] h3, .wrap[lang="th"] .num, .wrap[lang="th"] i {{ font-style: normal; }} .wrap[lang="th"] h3 {{ font-weight: 600; }}</style>
<div class="wrap" lang="{lang}">
<nav class="toc" aria-label="{toc_label}">
<div class="lang">{switch}</div>
<details open><summary>{toc_label}</summary><ol>{"".join(toc)}</ol></details>
</nav>
<main>
{body}
</main>
</div>
<script>try{{if(window.matchMedia('(max-width: 900px)').matches){{var d=document.querySelector('nav.toc details');if(d)d.open=false;}}}}catch(e){{}}</script>
'''
if standalone:
    out = out.replace('src="img/', 'src="../img/').replace(' target="_blank" rel="noopener"', '').replace('</style>', 'body { margin: 0; } img { max-width: 100%; }\n</style>', 1)
    out = f'<!doctype html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="robots" content="noindex, nofollow">\n' + out.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '', 1).replace('\n<div class="wrap"', '\n</head>\n<body>\n<div class="wrap"', 1) + '</body>\n</html>\n'
    import os; os.makedirs(sys.argv[4] + f"/{lang}", exist_ok=True)
    open(sys.argv[4] + f"/{lang}/index.html", "w", encoding="utf-8").write(out)
else:
    open(d + f"manual-{lang}.html", "w", encoding="utf-8").write(out)
used = sorted(set(re.findall(r'src="(img/[^"]+)"', body)))
pass
print(len(out), len(used))
