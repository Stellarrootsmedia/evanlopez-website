#!/usr/bin/env python3
"""Pull the latest podcast episodes (RSS) and YouTube videos into data/*.json,
and cache video thumbnails locally as WebP.

Run from the site root:  python3 scripts/sync.py && python3 scripts/build.py
(The GitHub Action in .github/workflows/refresh.yml runs both every day.)"""
import json, os, re, html, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = json.load(open(os.path.join(ROOT, "data/site.json")))
UA = {"User-Agent": "Mozilla/5.0 (evanlopez.com site sync)"}
NS = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
      "a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "m": "http://search.yahoo.com/mrss/"}
BIRD = re.compile(r"\bbird|birds\b|birding|birdwatch|cardinal|pigeon|crow|hawk|owl|sparrow|grackle|robin|blue ?jay|hummingbird|feathered|birdyverse", re.I)


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()


def clean_desc(raw):
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw or ""))
    text = re.split(r"🎤|Come see me live", text)[0]          # drop the link-dump footer
    return re.sub(r"\s+", " ", text).strip()


def norm(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def sync_videos():
    feed = ET.fromstring(get("https://www.youtube.com/feeds/videos.xml?channel_id=" + SITE["youtube_channel_id"]))
    out = []
    for e in feed.findall("a:entry", NS):
        vid = e.findtext("yt:videoId", namespaces=NS)
        title = e.findtext("a:title", namespaces=NS)
        link = e.find("a:link", NS).get("href")
        stats = e.find("m:group/m:community/m:statistics", NS)
        out.append({"id": vid, "title": title, "published": e.findtext("a:published", namespaces=NS)[:10],
                    "short": "/shorts/" in link or "#shorts" in title.lower(),
                    "bird": bool(BIRD.search(title)),
                    "views": int(stats.get("views")) if stats is not None else 0})
    # keep previously-seen bird clips so the section never empties when the feed rolls over
    path = os.path.join(ROOT, "data/videos.json")
    if os.path.exists(path):
        seen = {v["id"] for v in out}
        out += [v for v in json.load(open(path)) if v.get("bird") and v["id"] not in seen]
    json.dump(out, open(path, "w"), indent=1, ensure_ascii=False)
    return out


def thumbs(videos):
    try:
        from PIL import Image
    except ImportError:
        print("  (Pillow not installed: skipping thumbnails)"); return
    import io
    d = os.path.join(ROOT, "assets/video"); os.makedirs(d, exist_ok=True)
    for v in videos:
        dest = os.path.join(d, v["id"] + ".webp")
        if os.path.exists(dest):
            continue
        try:
            im = Image.open(io.BytesIO(get(f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg"))).convert("RGB")
        except Exception as ex:
            print("  thumb failed", v["id"], ex); continue
        w, h = im.size
        if v["short"]:                       # vertical clip sits pillar-boxed in the middle: crop 9:16
            cw = int(h * 9 / 16); im = im.crop(((w - cw) // 2, 0, (w + cw) // 2, h))
        else:                                # hqdefault is 4:3 letterboxed: crop to 16:9
            ch = int(w * 9 / 16); im = im.crop((0, (h - ch) // 2, w, (h + ch) // 2))
        im.save(dest, "WEBP", quality=78)


def sync_podcast(videos):
    ch = ET.fromstring(get(SITE["podcast"]["rss"])).find("channel")
    yt = {norm(v["title"]): v["id"] for v in videos if not v["short"]}
    eps = []
    for i in ch.findall("item")[:60]:
        title = (i.findtext("title") or "").strip()
        dur = i.findtext("itunes:duration", namespaces=NS) or ""
        parts = [int(p) for p in dur.split(":") if p.isdigit()]
        secs = sum(p * 60 ** k for k, p in enumerate(reversed(parts))) if parts else 0
        eps.append({"title": title, "date": parsedate_to_datetime(i.findtext("pubDate")).strftime("%Y-%m-%d"),
                    "minutes": round(secs / 60), "url": i.findtext("link"),
                    "youtube": yt.get(norm(title), ""), "desc": clean_desc(i.findtext("description"))[:420]})
    data = {"count": len(ch.findall("item")), "episodes": eps}
    json.dump(data, open(os.path.join(ROOT, "data/podcast.json"), "w"), indent=1, ensure_ascii=False)
    return data


if __name__ == "__main__":
    vids = sync_videos(); print(f"videos: {len(vids)} ({sum(v['bird'] for v in vids)} bird)")
    thumbs(vids)
    pod = sync_podcast(vids); print(f"podcast: {pod['count']} episodes, latest: {pod['episodes'][0]['title']}")
