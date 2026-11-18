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

Every change staff will see gets a "What's new" entry for its release, next to the update of the manual section it changes.

1. Create two files in `src/updates/`, one per language, named `YYYY-MM-DD-slug.en.html` and `YYYY-MM-DD-slug.th.html` (the date is the release's hotel date; copy `2026-11-18-booking-tracker.*` as a model). Each starts with a comment block, then the body:

   ```
   <!--
   title: Short title
   summary: One line for the list.
   -->
   <p>What is new, who it is for (roles), and links into the manual.</p>
   ```

   In the body write `{manual}#section-id` for a link into the manual of the same language and `{img}name.jpg` for a screenshot from `site/img/`. Only the English file is needed to publish; a release without the other language is still listed there, marked "Thai only" / "English only" (the Thai is awaiting a native review in any case).
2. Rebuild (the three commands above). This writes `site/<lang>/updates/index.html` (the list, newest first) and one page per release.
3. Commit `src/` and `site/`, push, then on the VPS `git pull && ./deploy/publish.sh`.

The pages sit under `/manual/` like the rest, so the staff-session check in nginx covers them; no nginx change is needed (links are relative).

## Deploying on the VPS

nginx serves `site/` directly from a clone of this repository. To update the VPS, run `git pull` in that clone; there is nothing to restart.

`deploy/nginx-manual.conf` has the nginx part, and `deploy/DEPLOY.md` has the steps.
