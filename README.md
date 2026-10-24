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
   ```

3. Commit both `src/` and `site/`.

New screenshots go into `site/img/` and are referenced as `img/<name>.jpg` in the body files.
All names and figures in the screenshots are demo data from a local test deployment, never production.

## Deploying on the VPS

nginx serves `site/` directly from a clone of this repository. To update the VPS, run `git pull` in that clone; there is nothing to restart.

`deploy/nginx-manual.conf` has the nginx part, and `deploy/DEPLOY.md` has the steps.
