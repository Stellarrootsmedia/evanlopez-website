# evanlopez.com

Static site (plain HTML/CSS/JS, no framework). Pages are generated from JSON by a small Python script.

## Edit content
| What | File |
|---|---|
| Bio, socials, FAQ, email, GA4 ID, sign-up link | `data/site.json` |
| Weekly shows + tour dates | `data/shows.json` |
| Merch products + store link | `data/merch.json` |
| Podcast episodes / YouTube clips | auto: `scripts/sync.py` writes `data/podcast.json`, `data/videos.json` |

Then rebuild:
```
python3 scripts/sync.py   # optional: pull latest episodes & clips (needs Pillow for thumbnails)
python3 scripts/build.py  # regenerates index.html, /podcast/, /austin-comedy/, /press/, 404, sitemap, llms.txt
```
A GitHub Action (`.github/workflows/refresh.yml`) runs both daily, so new episodes, bird clips and next show dates stay current on their own.

## Styling
All colors and fonts are CSS variables at the top of `css/styles.css`. After editing CSS/JS, bump `V` in `scripts/build.py` (cache-bust) and rebuild.

## Preview locally
```
python3 -m http.server 4322
```
