# sunset-manual

Staff manual for the Sunset hotel system, in English and Thai, with screenshots.
It is a static site: plain HTML and images, no build step and no backend.

- `site/`: what nginx serves (`index.html` picks the language, then `en/`, `th/` and `img/`).
- `src/`: the text of each language (`body-en.html`, `body-th.html`) and the shared styles (`style.css.part`).
- `src/tools/assemble.py`: rebuilds `site/en/index.html` and `site/th/index.html` from `src/`.

## Editing

1. Change `src/body-en.html` and/or `src/body-th.html`.
2. Rebuild both pages:

   ```
   cd src
   python3 tools/assemble.py en ../th/ site ../site
   python3 tools/assemble.py th ../en/ site ../site
   python3 tools/updates.py ../site
   ```

   (`assemble.py` needs Pillow, as before; `updates.py` builds the "What's new" pages, see below.)

3. Commit both `src/` and `site/`.

New screenshots go into `site/img/` and are referenced as `img/<name>.jpg` in the body files.
All names and figures in the screenshots are demo data from a local test deployment, never production.

## Adding a release note

There is **one note per hotel week** (Monday to Sunday, Asia/Bangkok), `src/updates/<date of that Monday>-week.<lang>.html`. A change staff will see is written into the file of the current week, under its area, as **New** or **Fixed**; if the week has no file yet, create it (copy `2026-11-16-week.*` as a model). Do not start a second note in the same week: merge duplicates into one item (a feature and its later fixes are one line in New plus lines in Fixed).

1. The file starts with a comment block, then the body. The title is "Week of 16 November 2026" (a week with one notable release may use its own title; the file is still one per week):

   ```
   <!--
   title: Week of 16 November 2026
   summary: One line for the list.
   -->
   <section data-area="front-desk">
   <h4>New</h4>
   <ul>
     <li><b>What staff do differently.</b> Who it is for (CASHIER and above). <a href="{manual}#booking-page">Booking page</a>.</li>
   </ul>
   <h4>Fixed</h4>
   <ul>
     <li>One line per fix, no link unless a manual section changed.</li>
   </ul>
   </section>
   ```

2. Sections follow the order of the admin menu: `front-desk`, `rooms`, `restaurant`, `spa`, `gym-lighting`, `staff`, `reports`, then `pos` (the phone) and `guest-site` only when they changed. Leave out an area with no changes. Inside a section: `<h4>New</h4>` first, then `<h4>Fixed</h4>`, each at most once (Thai: ใหม่ / แก้ไขแล้ว). The area heading is added by `updates.py`. Technical changes (code, tests) do not go in.
3. Every New item names the roles it is for and links the manual section with `{manual}#section-id` (the same-language manual); `{img}name.jpg` is a screenshot from `site/img/`. Only the English file is needed to publish; a week without the other language is listed marked "Thai only" / "English only" (the Thai is awaiting a native review in any case).
4. Rebuild (the three commands above). This writes `site/<lang>/updates/index.html` (the list, grouped by month, newest first, one row per week) and one page per week. `updates.py` stops with a clear message if a file is not named by a Monday, an area is unknown or out of menu order, or New/Fixed are missing or in the wrong order.
5. `src/updates/redirects.txt` keeps the addresses of earlier release pages alive (a stub page sends on to the week that holds them); add a line there only if you ever rename or merge a week file.
6. Commit `src/` and `site/`, push, then on the VPS `git pull && ./deploy/publish.sh`.

The pages sit under `/manual/` like the rest, so the staff-session check in nginx covers them; no nginx change is needed (links are relative).

## Deploying on the VPS

nginx serves `site/` directly from a clone of this repository. To update the VPS, run `git pull` in that clone; there is nothing to restart.

`deploy/nginx-manual.conf` has the nginx part, and `deploy/DEPLOY.md` has the steps.
