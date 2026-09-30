#!/usr/bin/env python3
"""Build every page of evanlopez.com from data/*.json.

Run from anywhere:  python3 scripts/build.py
Edit content in data/site.json, data/shows.json, data/merch.json.
data/podcast.json and data/videos.json are refreshed by scripts/sync.py."""
import json, os, re, html, datetime as dt
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = ZoneInfo("America/Chicago")
V = "11"  # cache-bust: bump when css/js change


def load(name):
    return json.load(open(os.path.join(ROOT, "data", name)))


S, SHOWS, MERCH, POD, VIDS = (load(n) for n in ("site.json", "shows.json", "merch.json", "podcast.json", "videos.json"))
BASE = S["url"]
NOW = dt.datetime.now(TZ)
e = html.escape


def untag(t):
    return re.sub(r"\s*#\w+", "", t).strip()


def has(path):
    return os.path.exists(os.path.join(ROOT, path))


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(text)


# ---------------------------------------------------------------- icons
def icon(name, size=20):
    p = {
        "Instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r=".6" fill="currentColor"/>',
        "TikTok": '<path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5"/><path d="M14 3c.4 2.6 2.2 4.4 5 4.6"/>',
        "YouTube": '<rect x="2.5" y="5.5" width="19" height="13" rx="4"/><path d="M10 9.2v5.6l4.8-2.8z" fill="currentColor"/>',
        "Facebook": '<path d="M14.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.6-1.5h1.6V4.4a21 21 0 0 0-2.4-.1c-2.4 0-4 1.4-4 4.1v2.1H8.7v3h2.6V21"/>',
        "Threads": '<path d="M16.5 11.2c-.4-2.3-2-3.5-4.3-3.5-2.6 0-4.1 1.8-4.1 4.3s1.6 4.3 4.1 4.3c2 0 3.7-1.1 3.7-3 0-1.6-1.4-2.5-3.3-2.5-1.5 0-2.6.7-2.6 1.8 0 1 .9 1.6 2 1.6 2.5 0 3.4-2.3 3.4-4.9"/><path d="M19.6 7.3C18.3 4.6 15.6 3 12.2 3 6.9 3 4 6.8 4 12s2.9 9 8.2 9c3.3 0 6-1.5 7.3-4.2"/>',
        "Spotify": '<circle cx="12" cy="12" r="9.5"/><path d="M7 9.3c3.6-1 7.4-.7 10.3.9M7.6 12.4c3-.8 6-.5 8.4.8M8.2 15.3c2.4-.6 4.6-.4 6.5.6"/>',
        "Apple Podcasts": '<circle cx="12" cy="10" r="2.2"/><path d="M11 21l-.5-5.5a1.5 1.5 0 0 1 3 0L13 21z" fill="currentColor"/><path d="M7.8 15.2a6 6 0 1 1 8.4 0"/><path d="M5.3 18a9.4 9.4 0 1 1 13.4 0"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6 8.5 7 8.5-7"/>',
        "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
        "play": '<path d="M8 5.5v13l10.5-6.5z" fill="currentColor"/>',
        "bird": '<path d="M3 15.5c3.2.4 6-.6 8-3.1 1-1.3 1.6-3 3.3-4 1.4-.8 3.2-.6 4.4.4l2.3-.3-1.8 1.6c.2 3.8-2.6 7.2-7 7.6-3.4.3-6.8-.4-9.2-2.2z" fill="currentColor" stroke="none"/><path d="M11 12.4 7.5 7.5c2.6.2 4.7 1.4 5.8 3" fill="currentColor" stroke="none"/>',
        "ticket": '<path d="M3 8a2 2 0 0 0 0 4v0a2 2 0 0 1 0 4v2h18v-2a2 2 0 0 1 0-4 2 2 0 0 0 0-4V6H3z"/><path d="M14 6v12" stroke-dasharray="2 2"/>',
        "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21"/>',
        "shirt": '<path d="M8 3.5 3 6.5l2 4 2-1V20.5h10V9.5l2 1 2-4-5-3c-.5 1.5-2 2.5-4 2.5s-3.5-1-4-2.5z"/>',
    }[name]
    return (f'<svg class="ico" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>')


def socials_row(cls="socials"):
    return f'<ul class="{cls}">' + "".join(
        f'<li><a href="{s["url"]}" target="_blank" rel="noopener me" aria-label="{s["name"]} {e(s["handle"])}">{icon(s["name"])}</a></li>'
        for s in S["socials"]) + "</ul>"


# ---------------------------------------------------------------- shows
def weekly_dates(show, n=4):
    h, m = map(int, show["time"].split(":"))
    d = NOW.replace(hour=h, minute=m, second=0, microsecond=0)
    d += dt.timedelta(days=(show["weekday"] - d.weekday()) % 7)
    if d < NOW:
        d += dt.timedelta(days=7)
    return [d + dt.timedelta(weeks=i) for i in range(n)]


def one_offs():
    out = []
    for x in SHOWS["dates"]:
        if not x.get("date"):
            continue
        h, m = map(int, (x.get("time") or "20:00").split(":"))
        d = dt.datetime.fromisoformat(x["date"]).replace(hour=h, minute=m, tzinfo=TZ)
        if d.date() >= NOW.date():
            out.append((d, x))
    return sorted(out, key=lambda t: t[0])


def ftime(d):
    return d.strftime("%-I:%M %p").replace(":00", "")


def show_row(d, x):
    where = e(x["venue"]) + (f' · {e(x["city"])}, {e(x["region"])}' if x.get("city") else "")
    return (f'<li class="date-row"><time class="date-chip" datetime="{d.isoformat()}"><span>{d.strftime("%a")}</span>'
            f'<b>{d.strftime("%b")} {d.day}</b></time><div class="date-info"><strong>{e(x.get("name") or S["name"])}</strong>'
            f'<span>{where} · {ftime(d)}</span></div><a class="btn btn-sm" href="{e(x["tickets"])}" target="_blank" rel="noopener">Tickets</a></li>')


def events_ld():
    ev = []
    for w in SHOWS["weekly"]:
        for d in weekly_dates(w, 4):
            ev.append((d, w, True))
    for d, x in one_offs():
        ev.append((d, x, False))
    out = []
    for d, x, weekly in ev:
        out.append({"@type": "ComedyEvent", "name": (x.get("presenter", "") + " presents " if x.get("presenter") else "") + x["name"],
                    "startDate": d.isoformat(), "eventStatus": "https://schema.org/EventScheduled",
                    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                    "location": {"@type": "Place", "name": x["venue"], "address": {"@type": "PostalAddress",
                                 "streetAddress": x.get("address", ""), "addressLocality": x.get("city", ""),
                                 "addressRegion": x.get("region", ""), "postalCode": x.get("postal", ""), "addressCountry": "US"}},
                    "performer": {"@id": BASE + "#evan"},
                    "organizer": {"@id": BASE + "#topflight"} if weekly else {"@id": BASE + "#evan"},
                    "offers": {"@type": "Offer", "url": x["tickets"], "availability": "https://schema.org/InStock"},
                    "image": BASE + "assets/og-image.jpg"})
    return out


# ---------------------------------------------------------------- shared bits
def signup_form(fid, big=False):
    su = S["signup"]
    if su["signup_url"]:
        return (f'<a class="btn btn-primary{" btn-lg" if big else ""}" href="{su["signup_url"]}" target="_blank" rel="noopener">'
                f'Get show alerts {icon("arrow", 18)}</a>')
    return f'''<form class="signup" id="{fid}" data-endpoint="https://formsubmit.co/ajax/{S["email"]}">
          <input type="hidden" name="_subject" value="New fan sign-up (evanlopez.com)">
          <input type="hidden" name="_template" value="table">
          <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
          <input type="hidden" name="list" value="fan alerts">
          <label class="sr" for="{fid}-email">Email</label>
          <input id="{fid}-email" type="email" name="email" placeholder="Email" autocomplete="email" required>
          <label class="sr" for="{fid}-phone">Phone (optional)</label>
          <input id="{fid}-phone" type="tel" name="phone" placeholder="Phone (optional)" autocomplete="tel">
          <label class="sr" for="{fid}-city">City</label>
          <input id="{fid}-city" type="text" name="city" placeholder="Your city" autocomplete="address-level2">
          <button class="btn btn-primary" type="submit">Get alerts</button>
          <p class="form-note" role="status">Tickets, merch drops and new episodes. Unsubscribe anytime.</p>
        </form>'''


NAV = [("Shows", "/#shows"), ("Videos", "/#videos"), ("Podcast", "/#podcast"), ("Merch", "/#merch"), ("About", "/#about")]

MARK = ('<svg class="mark" width="30" height="30" viewBox="0 0 32 32" fill="none" aria-hidden="true">'
        '<circle cx="16" cy="16" r="7.2" fill="currentColor"/>'
        '<ellipse cx="16" cy="16" rx="14.5" ry="5" transform="rotate(-24 16 16)" stroke="currentColor" stroke-width="1.4"/>'
        '<circle cx="28.4" cy="10.6" r="1.6" fill="currentColor"/></svg>')


def header():
    links = "".join(f'<li><a href="{h}">{t}</a></li>' for t, h in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="/" aria-label="Evan Lopez home">{MARK}<span><b>Evan Lopez</b><small>Comedian · Austin, TX</small></span></a>
      <nav class="nav" aria-label="Main">
        <ul id="nav-list">{links}<li class="nav-social">{socials_row("socials socials-sm")}</li></ul>
      </nav>
      <a class="btn btn-primary btn-sm header-cta" href="/#alerts"><span class="lbl-lg">Get show alerts</span><span class="lbl-sm">Alerts</span></a>
      <button class="menu-btn" aria-expanded="false" aria-controls="nav-list" aria-label="Menu"><span></span><span></span></button>
    </div>
  </header>'''


def footer():
    return f'''<footer class="site-footer">
    <div class="wrap footer-grid">
      <div>
        <a class="brand brand-lg" href="/">{MARK}<span><b>Evan Lopez</b><small>Comedian · Austin, TX</small></span></a>
        <p class="muted">Stand-up comedian in {S["city"]}, {S["region"]}. Host of <a href="/podcast/">{S["podcast"]["name"]}</a>. Founder of <a href="{S["topflight"]["url"]}" target="_blank" rel="noopener">{S["topflight"]["name"]}</a>.</p>
        {socials_row()}
      </div>
      <div>
        <p class="kicker">Explore</p>
        <ul class="flist"><li><a href="/#shows">Shows</a></li><li><a href="/#videos">Videos</a></li><li><a href="/podcast/">Podcast</a></li><li><a href="/#merch">Merch</a></li><li><a href="/austin-comedy/">Austin comedy guide</a></li></ul>
      </div>
      <div>
        <p class="kicker">Work with Evan</p>
        <ul class="flist"><li><a href="/press/">Press kit</a></li><li><a href="/#book">Booking</a></li><li><a href="mailto:{S["email"]}">{S["email"]}</a></li><li><a href="{S["topflight"]["url"]}" target="_blank" rel="noopener">Top Flight Comedy</a></li></ul>
      </div>
    </div>
    <div class="wrap footer-base"><span>© <span data-year>{NOW.year}</span> Evan Lopez · Austin, Texas</span><span class="coords">30.2672° N · 97.7431° W</span><a href="#top">Back to top ↑</a></div>
  </footer>'''


def ld_tags(objs):
    return "\n".join('  <script type="application/ld+json">' + json.dumps(o, ensure_ascii=False, separators=(",", ":")) + "</script>" for o in objs)


def gtag():
    g = S.get("ga4_id")
    if not g:
        return ""
    return f'''  <script async src="https://www.googletagmanager.com/gtag/js?id={g}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{g}');</script>
'''


def page(path, title, desc, body, ld=(), noindex=False, og_type="website", preload=""):
    url = BASE + path
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{gtag()}  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#090f17">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Evan Lopez">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{BASE}assets/og-image.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Evan Lopez, stand-up comedian in Austin, Texas">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/favicon-64.png" sizes="64x64" type="image/png">
  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="preload" href="/assets/fonts/space-grotesk-500-700.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/inter-400-600.woff2" as="font" type="font/woff2" crossorigin>{preload}
  <link rel="stylesheet" href="/css/styles.css?v={V}">
{ld_tags(ld)}
</head>
<body id="top">
  <div class="starlayer" aria-hidden="true"></div>
  {header()}
  <main id="main">
{body}
  </main>
  {footer()}
  <script src="/js/main.js?v={V}" defer></script>
</body>
</html>
'''


def faq_block(faqs, heading="Questions people ask"):
    items = "".join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in faqs)
    return f'''<section class="section" id="faq"><div class="wrap narrow">
      <p class="eyebrow">FAQ</p><h2>{heading}</h2><div class="faqs">{items}</div></div></section>'''


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def person_ld():
    img = BASE + ("assets/photos/about-1200.webp" if has("assets/photos/about-1200.webp") else "assets/og-image.jpg")
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "Person", "@id": BASE + "#evan", "name": "Evan Lopez", "url": BASE, "image": img,
         "jobTitle": "Stand-up comedian", "description": S["bio_short"], "email": "mailto:" + S["email"],
         "homeLocation": {"@type": "City", "name": "Austin", "containedInPlace": {"@type": "State", "name": "Texas"}},
         "knowsAbout": ["Stand-up comedy", "Comedy podcasting", "Comedy show production", "Bird watching"],
         "founder": {"@id": BASE + "#topflight"},
         "sameAs": [s["url"] for s in S["socials"]] + [S["podcast"]["spotify"], S["podcast"]["apple"]]},
        {"@type": "Organization", "@id": BASE + "#topflight", "name": "Top Flight Comedy", "url": S["topflight"]["url"],
         "founder": {"@id": BASE + "#evan"}, "sameAs": [S["topflight"]["instagram"]],
         "areaServed": {"@type": "City", "name": "Austin"}},
        {"@type": "PodcastSeries", "@id": BASE + "podcast/#series", "name": S["podcast"]["name"], "url": BASE + "podcast/",
         "description": S["podcast"]["tagline"], "author": {"@id": BASE + "#evan"}, "webFeed": S["podcast"]["rss"],
         "image": BASE + "assets/photos/podcast-600.webp", "sameAs": [S["podcast"]["spotify"], S["podcast"]["apple"]]},
        {"@type": "WebSite", "@id": BASE + "#site", "url": BASE, "name": "Evan Lopez", "publisher": {"@id": BASE + "#evan"}},
    ]}


DIMS = json.load(open(os.path.join(ROOT, "assets/photos/dims.json"))) if has("assets/photos/dims.json") else {}


def photo(name, alt, sizes, cls="", eager=False, widths=(800, 1200)):
    """<img> for a processed photo (scripts/photos.py), or '' if it doesn't exist."""
    ws = [w for w in widths if has(f"assets/photos/{name}-{w}.webp")]
    if not ws:
        return ""
    w, h = DIMS.get(name, [800, 1000])
    load_attr = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    srcset = ", ".join(f"/assets/photos/{name}-{x}.webp {x}w" for x in ws)
    return (f'<img class="{cls}" src="/assets/photos/{name}-{ws[0]}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{e(alt)}" {load_attr}>')


def pod_cover(sizes, eager=False):
    return photo("podcast", "Seven Minutes in Evan podcast cover art", sizes, "pod-img", eager, (600, 1200))


LIVE = [("live-1", "On stage", "Evan Lopez performing stand-up in Austin"),
        ("live-2", "The crowd", "Audience laughing at an Evan Lopez comedy show"),
        ("live-3", "Packed room", "A full comedy room during Evan Lopez's set"),
        ("live-4", "Mic check", "Evan Lopez on stage in front of a red curtain"),
        ("live-5", "Off stage", "Evan Lopez in a pool float under a neon sign")]


def home():
    pod = POD["episodes"]
    latest = pod[0]
    weekly = SHOWS["weekly"]
    offs = one_offs()
    nxt = weekly_dates(weekly[0], 1)[0] if weekly else None


    # shows
    tour = "".join(show_row(d, x) for d, x in offs[:12])
    if tour:
        tour = f'<ul class="dates">{tour}</ul>'
    else:
        tour = '''<div class="empty-tour">
            <p class="eyebrow">Tour dates</p>
            <h3>New cities incoming</h3>
            <p>Tell me where you are and I'll text you before tickets go public near you. Where the list is biggest is where I go first.</p>
            <a class="btn btn-primary" href="#alerts">Get alerts for my city</a></div>'''
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_html = "".join(f'''<div class="weekly">
            <div class="weekly-when"><span class="dot"></span>Every {days[w["weekday"]]} · {ftime(weekly_dates(w,1)[0])}</div>
            <div class="weekly-body"><strong>{e(w["name"])}</strong><span>{e(w["venue"])}, {e(w["city"])} · {e(w["role"])}, with {e(w["presenter"])}</span>
            <span class="muted small">Next: <time data-weekly="{w["weekday"]}" data-time="{w["time"]}" datetime="{weekly_dates(w,1)[0].date().isoformat()}">{weekly_dates(w,1)[0].strftime("%a, %b %-d")}</time></span></div>
            <a class="btn btn-ghost btn-sm" href="{e(w["tickets"])}" target="_blank" rel="noopener">{icon("ticket",16)} Tickets</a></div>''' for w in weekly)

    live = "".join(f'<figure class="frame">{photo(n, alt, "(max-width:700px) 58vw, 230px")}<figcaption class="tag">{t}</figcaption></figure>'
                   for n, t, alt in LIVE if has(f"assets/photos/{n}-800.webp"))

    # videos: featured Instagram clips first, then YouTube bird shorts
    clips = "".join(f'''<a class="frame clip" href="{c["url"]}" target="_blank" rel="noopener" aria-label="Watch on {c["platform"]}: {e(c["caption"])}">
            <img src="/assets/clips/{c["id"]}.webp" width="360" height="640" alt="" loading="lazy" decoding="async">
            <span class="play">{icon("play", 22)}</span>
            <span class="tag"><b>{e(c.get("views") or c["likes"])} {"views" if c.get("views") else "likes"}</b> · {c["platform"]}</span></a>''' for c in S.get("featured_clips", []))
    birds = [v for v in VIDS if v["bird"] and v["short"] and has(f'assets/video/{v["id"]}.webp')]
    clips += "".join(f'''<button class="frame clip yt-facade" data-yt="{v["id"]}" aria-label="Play: {e(untag(v["title"]))}">
            <img src="/assets/video/{v["id"]}.webp" width="202" height="360" alt="" loading="lazy" decoding="async">
            <span class="play">{icon("play", 22)}</span>
            <span class="tag"><b>New</b> · YouTube<br>{e(untag(v["title"]))}</span></button>''' for v in birds[:5 - len(S.get("featured_clips", []))])

    # podcast
    def ep_row(ep):
        watch = f' · <a href="https://www.youtube.com/watch?v={ep["youtube"]}" target="_blank" rel="noopener">Watch</a>' if ep["youtube"] else ""
        return (f'<li><a class="ep-title" href="{e(ep["url"] or S["podcast"]["spotify"])}" target="_blank" rel="noopener">{e(ep["title"])}</a>'
                f'<span class="muted small">{dt.date.fromisoformat(ep["date"]).strftime("%b %-d")} · {ep["minutes"]} min{watch}</span></li>')
    recent = "".join(ep_row(x) for x in pod[1:5])
    if latest["youtube"] and has(f'assets/video/{latest["youtube"]}.webp'):
        latest_media = (f'<button class="yt-facade wide" data-yt="{latest["youtube"]}" aria-label="Play: {e(latest["title"])}">'
                        f'<img src="/assets/video/{latest["youtube"]}.webp" width="480" height="270" alt="" loading="lazy" decoding="async">'
                        f'<span class="play">{icon("play", 26)}</span></button>')
    else:
        latest_media = f'<button class="spot-facade" data-spotify="{S["podcast"]["spotify"].rsplit("/",1)[1]}">{icon("play",20)} Play the latest episode here</button>'

    # merch
    if MERCH["products"]:
        cards = "".join(f'''<a class="product" href="{e(p["url"])}" target="_blank" rel="noopener">
            <img src="/assets/merch/{e(p["image"])}" width="600" height="600" alt="{e(p["name"])}" loading="lazy" decoding="async">
            <span class="p-name">{e(p["name"])}</span><span class="p-price">{e(p["price"])}</span></a>''' for p in MERCH["products"])
        merch = f'<div class="products swipe">{cards}</div>' + (f'<p class="center"><a class="btn btn-ghost" href="{MERCH["store_url"]}" target="_blank" rel="noopener">Shop everything</a></p>' if MERCH["store_url"] else "")
    else:
        merch = f'''<div class="merch-drop">
          {PATCH}
          <div><p class="eyebrow">Drop 01 · In production</p><h3>The first merch drop is in the works</h3>
          <p>Shirts, hats and a few things the birds would approve of. The first run will be small, and the list gets first access before it goes public.</p>
          <a class="btn btn-primary" href="#alerts">Get first access</a></div></div>'''

    # each hero image only downloads at its own screen size (the other gets a 1px placeholder)
    blank = "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
    hero_img = photo("hero", "Evan Lopez performing stand-up comedy on stage", "100vw", "hero-bg", eager=True, widths=(1200, 1920))
    hero_m = photo("hero-m", "Evan Lopez performing stand-up comedy on stage", "100vw", "hero-m", eager=True, widths=(800,))
    if hero_img:
        hero_img = f'<picture><source media="(max-width: 700px)" srcset="{blank}">{hero_img}</picture>'
    if hero_m:
        hero_m = f'<picture><source media="(min-width: 701px)" srcset="{blank}">{hero_m}</picture>'

    about_img = photo("about", "Portrait of Austin comedian Evan Lopez", "(max-width: 700px) 90vw, 440px", "about-photo")
    bio = "".join(f"<p>{e(p)}</p>" for p in S["bio_long"])
    clubs = "".join(f"<li>{e(c)}</li>" for c in S["clubs"])

    body = f'''
    <!-- HERO -->
    <section class="hero">
      <div class="hero-media" aria-hidden="true">{hero_img}</div>
      <div class="wrap hero-inner">
        <div class="hero-top"><span>Stand-up comedian</span><span>Austin, Texas</span><span class="hide-sm">Transmitting weekly</span></div>
        <figure class="hero-mobile">{hero_m}</figure>
        <div class="hero-copy">
          <h1>Evan<br>Lopez</h1>
          <p class="lede">{e(S["tagline"])}</p>
          <div class="hero-ctas">
            <a class="btn btn-primary btn-lg" href="#alerts">Get show alerts</a>
            <a class="btn btn-ghost btn-lg" href="#videos">{icon("play",16)} Watch clips</a>
          </div>
          {socials_row("socials hero-socials")}
        </div>
      </div>
    </section>


    <!-- QUICK LINKS (link-in-bio, but owned) -->
    <section class="section tight">
      <div class="wrap tiles">
        <a class="tile" href="#shows"><span class="no">01 / Live</span><span class="t-label">Shows</span><span class="t-sub">{"Next: " + nxt.strftime("%a %-I %p") + " · East Austin" if nxt else "Dates &amp; tickets"}</span></a>
        <a class="tile" href="#videos"><span class="no">02 / Watch</span><span class="t-label">Videos</span><span class="t-sub">The bird videos &amp; more</span></a>
        <a class="tile" href="#podcast"><span class="no">03 / Listen</span><span class="t-label">Podcast</span><span class="t-sub">New: {e(latest["title"][:34])}</span></a>
        <a class="tile" href="#merch"><span class="no">04 / Wear</span><span class="t-label">Merch</span><span class="t-sub">{"Shop now" if MERCH["products"] else "Drop 01 incoming"}</span></a>
      </div>
    </section>

    <!-- SHOWS -->
    <section class="section" id="shows">
      <div class="wrap">
        <div class="sec-head"><p class="eyebrow">Live</p><h2>Come see a show</h2></div>
        {tour}
        {weekly_html}
        <div class="frames live swipe">{live}</div>
        <p class="swipe-hint" aria-hidden="true">Swipe →</p>
      </div>
    </section>

    <!-- VIDEOS -->
    <section class="section band" id="videos">
      <div class="wrap">
        <div class="sec-head split">
          <div><p class="eyebrow">Watch · the birdyverse</p><h2>Millions of views and counting</h2></div>
          <p class="muted">Check me out on social media. New videos every week on Instagram, TikTok and YouTube.</p>
        </div>
        <div class="frames clips swipe">{clips}</div>
        <p class="swipe-hint" aria-hidden="true">Swipe →</p>
        <div class="follow-row">
          <a class="btn btn-ghost" href="{S["socials"][0]["url"]}" target="_blank" rel="noopener">{icon("Instagram",18)} Instagram</a>
          <a class="btn btn-ghost" href="{S["socials"][1]["url"]}" target="_blank" rel="noopener">{icon("TikTok",18)} TikTok</a>
          <a class="btn btn-ghost" href="{S["socials"][2]["url"]}" target="_blank" rel="noopener">{icon("YouTube",18)} YouTube</a>
        </div>
      </div>
    </section>

    <!-- PODCAST -->
    <section class="section" id="podcast">
      <div class="wrap pod-grid">
        <div class="pod-cover bracket">{pod_cover("(max-width:700px) 70vw, 380px")}</div>
        <div>
          <p class="eyebrow">Listen · {S["podcast"]["cadence"].lower()}</p>
          <h2>Seven Minutes in Evan</h2>
          <p class="lede sm">{e(S["podcast"]["tagline"])} {POD["count"]} episodes of birds, movies, fights, parenting and whatever else took over the week.</p>
          <div class="listen">
            <a class="btn btn-ghost btn-sm" href="{S["podcast"]["spotify"]}" target="_blank" rel="noopener">{icon("Spotify",18)} Spotify</a>
            <a class="btn btn-ghost btn-sm" href="{S["podcast"]["apple"]}" target="_blank" rel="noopener">{icon("Apple Podcasts",18)} Apple</a>
            <a class="btn btn-ghost btn-sm" href="{S["podcast"]["youtube"]}" target="_blank" rel="noopener">{icon("YouTube",18)} YouTube</a>
          </div>
          <div class="latest">
            <p class="eyebrow">Latest episode · {dt.date.fromisoformat(latest["date"]).strftime("%b %-d")} · {latest["minutes"]} min</p>
            <h3>{e(latest["title"])}</h3>
            {latest_media}
          </div>
          <ul class="eps">{recent}</ul>
          <a class="text-link" href="/podcast/">All episodes {icon("arrow",16)}</a>
        </div>
      </div>
    </section>

    <!-- MERCH -->
    <section class="section band" id="merch">
      <div class="wrap">
        <div class="sec-head"><p class="eyebrow">Merch</p><h2>Wear the bit</h2></div>
        {merch}
      </div>
    </section>

    <!-- ABOUT -->
    <section class="section" id="about">
      <div class="wrap about-grid">
        <figure class="about-visual bracket">{about_img}<figcaption class="cap">Evan Lopez · Austin, TX</figcaption></figure>
        <div>
          <p class="eyebrow">About</p>
          <h2>Austin comedian, desert-raised</h2>
          <div class="bio">{bio}</div>
          <a class="tf-card" href="{S["topflight"]["url"]}" target="_blank" rel="noopener">
            <span class="tf-kicker">Founder &amp; producer</span>
            <strong>Top Flight Comedy</strong>
            <span>{e(S["topflight"]["blurb"])}</span>
            <span class="text-link">topflightcomedy.com {icon("arrow",16)}</span>
          </a>
        </div>
      </div>
    </section>

    <!-- ALERTS -->
    <section class="section alerts" id="alerts">
      <div class="wrap narrow center">
        <p class="eyebrow">The list</p>
        <h2>{e(S["signup"]["headline"])}</h2>
        <p class="lede sm">{e(S["signup"]["sub"])}</p>
        {signup_form("signup-main", big=True)}
      </div>
    </section>

    {faq_block(S["faq"])}

    <!-- BOOKING -->
    <section class="section band" id="book">
      <div class="wrap book-grid">
        <div>
          <p class="eyebrow">Booking &amp; press</p>
          <h2>Work with Evan</h2>
          <p>Club and private bookings, festivals, press, brand deals or coming on the podcast. Send a note and I'll get back to you.</p>
          <p><a class="text-link" href="mailto:{S["email"]}">{icon("mail",18)} {S["email"]}</a></p>
          <p><a class="text-link" href="/press/">Press kit, bios &amp; photos {icon("arrow",16)}</a></p>
        </div>
        {contact_form()}
      </div>
    </section>
'''
    ld = [person_ld(), {"@context": "https://schema.org", "@graph": events_ld()}, faq_ld(S["faq"])]
    pre = ('\n  <link rel="preload" as="image" href="/assets/photos/hero-1920.webp" imagesrcset="/assets/photos/hero-1200.webp 1200w, '
           '/assets/photos/hero-1920.webp 1920w" imagesizes="100vw" media="(min-width: 701px)" fetchpriority="high">') if hero_img else ""
    return page("", "Evan Lopez | Stand-Up Comedian in Austin, TX",
                "Evan Lopez is an Austin stand-up comedian, host of the Seven Minutes in Evan podcast and founder of Top Flight Comedy. Shows, podcast, bird videos, merch.",
                body, ld, preload=pre)


PATCH = '''<svg class="patch" viewBox="0 0 240 240" aria-hidden="true">
            <defs><path id="ring" d="M120 120 m-86 0 a86 86 0 1 1 172 0 a86 86 0 1 1 -172 0"/></defs>
            <circle cx="120" cy="120" r="116" fill="var(--space-2)" stroke="var(--accent)" stroke-width="3"/>
            <circle cx="120" cy="120" r="100" fill="none" stroke="var(--accent)" stroke-width="1" opacity=".5"/>
            <circle cx="120" cy="120" r="68" fill="#0f1a28" stroke="var(--line-2)"/>
            <text font-family="Space Mono, monospace" font-size="15" letter-spacing="4.2" fill="var(--cream)"><textPath href="#ring" startOffset="2%">EVAN LOPEZ · MERCH DIVISION · DROP 01 ·</textPath></text>
            <circle cx="120" cy="120" r="22" fill="var(--accent)"/>
            <ellipse cx="120" cy="120" rx="54" ry="16" fill="none" stroke="var(--cream)" stroke-width="2" transform="rotate(-22 120 120)"/>
            <circle cx="166" cy="98" r="4.5" fill="var(--cream)"/>
            <g fill="var(--cream)" opacity=".8"><circle cx="84" cy="84" r="1.4"/><circle cx="150" cy="156" r="1.2"/><circle cx="92" cy="150" r="1"/><circle cx="148" cy="80" r="1"/></g>
          </svg>'''


def contact_form():
    return f'''<form class="contact" id="contact-form" data-endpoint="https://formsubmit.co/ajax/{S["email"]}">
          <input type="hidden" name="_subject" value="New inquiry (evanlopez.com)">
          <input type="hidden" name="_template" value="table">
          <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
          <div class="row2">
            <label>Name<input type="text" name="name" autocomplete="name" required></label>
            <label>Email<input type="email" name="email" autocomplete="email" required></label>
          </div>
          <label>What's it for?
            <select name="type"><option>Booking a show</option><option>Private event</option><option>Press / interview</option><option>Podcast guest</option><option>Brand partnership</option><option>Something else</option></select>
          </label>
          <label>Details<textarea name="message" rows="4" placeholder="Date, city, venue, anything helpful" required></textarea></label>
          <button class="btn btn-primary" type="submit">Send</button>
          <p class="form-note" role="status"></p>
        </form>'''


# ---------------------------------------------------------------- podcast page
def podcast_page():
    eps = POD["episodes"]
    rows = []
    for ep in eps:
        d = dt.date.fromisoformat(ep["date"])
        watch = f'<a href="https://www.youtube.com/watch?v={ep["youtube"]}" target="_blank" rel="noopener">{icon("YouTube",16)} Watch</a>' if ep["youtube"] else ""
        rows.append(f'''<li class="ep-card"><div class="ep-meta"><time datetime="{ep["date"]}">{d.strftime("%b %-d, %Y")}</time> · {ep["minutes"]} min</div>
          <h3>{e(ep["title"])}</h3>{f'<p>{e(ep["desc"][:260])}{"…" if len(ep["desc"]) > 260 else ""}</p>' if ep["desc"] else ""}
          <div class="ep-links"><a href="{e(ep["url"] or S["podcast"]["spotify"])}" target="_blank" rel="noopener">{icon("play",16)} Listen</a>{watch}</div></li>''')
    body = f'''
    <section class="hero hero-sub">
      <div class="wrap pod-grid">
        <div class="pod-cover bracket">{pod_cover("(max-width:700px) 60vw, 380px", eager=True)}</div>
        <div>
          <p class="eyebrow">Podcast · {S["podcast"]["cadence"].lower()}</p>
          <h1>Seven Minutes in Evan</h1>
          <p class="lede">A weekly comedy podcast hosted by Austin stand-up comedian Evan Lopez. Birds, movies, fights, parenting, sandwiches and whatever else took over his week, often with Austin comedians along for the ride. {POD["count"]} episodes so far.</p>
          <div class="listen">
            <a class="btn btn-listen" href="{S["podcast"]["spotify"]}" target="_blank" rel="noopener">{icon("Spotify")} Spotify</a>
            <a class="btn btn-listen" href="{S["podcast"]["apple"]}" target="_blank" rel="noopener">{icon("Apple Podcasts")} Apple Podcasts</a>
            <a class="btn btn-listen" href="{S["podcast"]["youtube"]}" target="_blank" rel="noopener">{icon("YouTube")} YouTube</a>
          </div>
          <button class="spot-facade" data-spotify="{S["podcast"]["spotify"].rsplit("/",1)[1]}">{icon("play",22)} Play the latest episode here</button>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="wrap narrow">
        <div class="sec-head"><p class="eyebrow">Episodes</p><h2>Latest episodes</h2></div>
        <ol class="ep-list">{"".join(rows)}</ol>
        <p class="center"><a class="btn btn-ghost" href="{S["podcast"]["spotify"]}" target="_blank" rel="noopener">Full archive on Spotify</a></p>
      </div>
    </section>
    <section class="section alerts" id="alerts">
      <div class="wrap narrow center"><p class="eyebrow">Never miss one</p><h2>Get new episodes, shows and drops</h2>{signup_form("signup-pod")}</div></section>
'''
    ld = [person_ld(), {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "item": {"@type": "PodcastEpisode", "name": ep["title"], "datePublished": ep["date"],
         "url": ep["url"], "partOfSeries": {"@id": BASE + "podcast/#series"}, "timeRequired": f"PT{ep['minutes']}M"}}
        for i, ep in enumerate(eps[:20])]},
        crumbs([("Podcast", "podcast/")])]
    return page("podcast/", "Seven Minutes in Evan Podcast | Evan Lopez",
                f"Seven Minutes in Evan is a weekly comedy podcast from Austin comedian Evan Lopez. {POD['count']} episodes on Spotify, Apple Podcasts and YouTube.",
                body, ld)


def crumbs(items):
    lst = [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE}]
    lst += [{"@type": "ListItem", "position": i + 2, "name": n, "item": BASE + p} for i, (n, p) in enumerate(items)]
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": lst}


# ---------------------------------------------------------------- austin comedy guide
CLUB_NOTES = {
    "Comedy Mothership": "Joe Rogan's club on East Sixth Street, with two showrooms and a lineup of touring headliners and Austin regulars. Phones get locked up during shows.",
    "Cap City Comedy Club": "One of Austin's longest-running comedy clubs. A classic club room in North Austin with national headliners most weekends.",
    "The Creek and the Cave": "The New York club that moved to Austin, now a downtown hub for stand-up with multiple rooms and packed weeknight lineups.",
    "Sunset Strip Comedy Club": "A downtown Sixth Street club with shows most nights of the week. An easy way to add stand-up to a night out downtown.",
    "Black Rabbit ATX": "A cool underground room with an intimate, close-to-the-stage feel.",
    "East Austin Comedy Club": "A neighborhood club at 2505 E 6th St and home to Top Flight Comedy's weekly shows, including Daywalkers every Friday at 6 PM.",
}
AUSTIN_FAQ = [
    ["Where is the best place to see stand-up comedy in Austin?",
     "Austin's main comedy clubs include Comedy Mothership, Cap City Comedy Club, The Creek and the Cave, Sunset Strip Comedy Club, Black Rabbit ATX and East Austin Comedy Club. Most run shows several nights a week, with local comedians on weeknights and touring headliners on weekends."],
    ["Who are some Austin comedians to see live?",
     "Austin has one of the biggest stand-up scenes in the country, and weeknight showcases are the best way to find local comics. Evan Lopez is an Austin-based comedian featured on OFTV's LMAOF who performs at clubs across the city and produces weekly shows through Top Flight Comedy."],
    ["Is there early comedy in Austin?",
     "Yes. Top Flight Comedy's Daywalkers show runs every Friday at 6 PM at East Austin Comedy Club, an early option before dinner or a night out."],
]


def austin_page():
    cards = "".join(f'<li class="club"><h3>{e(c)}</h3><p>{e(CLUB_NOTES.get(c, ""))}</p></li>' for c in S["clubs"])
    body = f'''
    <section class="hero hero-sub">
      <div class="wrap narrow">
        <p class="eyebrow">Austin comedy guide</p>
        <h1>Where to see stand-up comedy in Austin, Texas</h1>
        <p class="lede">A local comic's guide to the Austin comedy scene. I've performed at every club on this list. Here's what each room is like and how to catch a good show.</p>
        <p class="muted small">By Evan Lopez, Austin stand-up comedian</p>
      </div>
    </section>
    <section class="section tight"><div class="wrap narrow">
      <h2>Austin comedy clubs</h2>
      <ul class="clubs">{cards}</ul>
      <h2 class="mt">Tips for your first Austin comedy show</h2>
      <ul class="tips">
        <li><strong>Weeknights are where the scene lives.</strong> Showcases stack a dozen local comics in one night, and they're usually cheaper than weekend headliners.</li>
        <li><strong>Buy ahead on weekends.</strong> The bigger clubs sell out Friday and Saturday shows, especially when a name headliner is in town.</li>
        <li><strong>Check the phone policy.</strong> Some rooms lock phones in pouches so comics can work out new material.</li>
        <li><strong>Go early.</strong> If you want dinner and a show, an early show like Daywalkers (Fridays, 6 PM) leaves the rest of the night open.</li>
      </ul>
      <div class="cta-box"><h2>Catch me live</h2><p>See where I'm performing next, or get a text when I'm doing a show near you.</p>
        <a class="btn btn-primary" href="/#shows">See my shows</a> <a class="btn btn-ghost" href="/#alerts">Get alerts</a></div>
    </div></section>
    {faq_block(AUSTIN_FAQ, "Austin comedy FAQ")}
'''
    ld = [person_ld(), {"@context": "https://schema.org", "@type": "Article", "headline": "Where to see stand-up comedy in Austin, Texas",
          "author": {"@id": BASE + "#evan"}, "publisher": {"@id": BASE + "#evan"}, "dateModified": NOW.date().isoformat(),
          "mainEntityOfPage": BASE + "austin-comedy/", "about": {"@type": "City", "name": "Austin"}},
          crumbs([("Austin comedy guide", "austin-comedy/")]), faq_ld(AUSTIN_FAQ)]
    return page("austin-comedy/", "Where to See Stand-Up Comedy in Austin, TX | Evan Lopez",
                "A local comic's guide to Austin comedy clubs: Comedy Mothership, Cap City, The Creek and the Cave, Sunset Strip, Black Rabbit and East Austin Comedy.",
                body, ld, og_type="article")


# ---------------------------------------------------------------- press kit
def press_page():
    photos = [n for n in ("press-1", "press-2", "press-3", "press-4") if has(f"assets/photos/{n}-2400.webp")]
    grid = "".join(f'<a class="press-photo" href="/assets/photos/{n}-2400.webp" download="evan-lopez-{n}.webp">{photo(n, "Evan Lopez press photo", "(max-width:700px) 45vw, 360px")}<span>Download hi-res</span></a>' for n in photos) \
        or '<p class="muted">Hi-res press photos coming soon. Email for photos in the meantime.</p>'
    long_bio = "".join(f"<p>{e(p)}</p>" for p in S["bio_long"])
    body = f'''
    <section class="hero hero-sub"><div class="wrap narrow">
      <p class="eyebrow">Press kit</p>
      <h1>Evan Lopez press kit</h1>
      <p class="lede">Bios, credits and photos for bookers, promoters and press. For anything else, email <a href="mailto:{S["email"]}">{S["email"]}</a>.</p>
    </div></section>
    <section class="section tight"><div class="wrap narrow">
      <h2>Short bio</h2>
      <div class="copy-box"><p id="bio-short">{e(S["bio_short"])}</p><button class="btn btn-ghost btn-sm" data-copy="bio-short">Copy</button></div>
      <h2 class="mt">Long bio</h2>
      <div class="copy-box"><div id="bio-long">{long_bio}</div><button class="btn btn-ghost btn-sm" data-copy="bio-long">Copy</button></div>
      <h2 class="mt">Credits</h2>
      <ul class="tips">
        <li><strong>OFTV, LMAOF:</strong> featured comedian on the series' most-watched episode</li>
        <li><strong>Clubs:</strong> {", ".join(e(c) for c in S["clubs"])}</li>
        <li><strong>Podcast:</strong> host of <a href="/podcast/">Seven Minutes in Evan</a> ({POD["count"]} episodes, weekly)</li>
        <li><strong>Producer:</strong> founder of <a href="{S["topflight"]["url"]}" target="_blank" rel="noopener">Top Flight Comedy</a>, Austin</li>
        <li><strong>Social:</strong> viral bird-watching comedy series on Instagram and TikTok</li>
      </ul>
      <h2 class="mt">Photos</h2>
      <div class="press-grid">{grid}</div>
      <h2 class="mt">Links</h2>
      {socials_row("socials socials-lg")}
    </div></section>
    <section class="section panel" id="book"><div class="wrap book-grid">
      <div><p class="eyebrow">Booking</p><h2>Book Evan</h2><p>Clubs, colleges, festivals, private events and podcasts.</p></div>
      {contact_form()}
    </div></section>
'''
    return page("press/", "Evan Lopez Press Kit | Austin Comedian Bio & Photos",
                "Press kit for Austin stand-up comedian Evan Lopez: short and long bios, credits (OFTV LMAOF), photos and booking contact.",
                body, [person_ld(), crumbs([("Press kit", "press/")])])


# ---------------------------------------------------------------- extras
REDIRECTS = {"about": "/press/", "shows": "/#shows", "contact": "/#book", "lessons": "/", "blogs": "/",
             "the-future-of-ai": "/", "sample-page": "/", "category/uncategorized": "/", "author/iamevanlopez": "/",
             **{f"tag/{t}": "/" for t in ["ai-misuse", "alien-life", "artificial-intelligence", "augmentation", "automation",
                                          "birth-rates", "misinformation", "population-crisis", "relationships",
                                          "space-exploration", "technology", "white-collar-jobs"]}}


def redirect_stub(to):
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Redirecting…</title>
<meta name="robots" content="noindex"><link rel="canonical" href="{BASE}{to.lstrip("/")}">
<meta http-equiv="refresh" content="0; url={to}"></head><body><a href="{to}">Continue to evanlopez.com</a></body></html>
'''


def not_found():
    body = f'''<section class="hero hero-sub"><div class="wrap narrow center">
      <p class="eyebrow">404</p><h1>This page flew the coop</h1>
      <p class="lede">It either moved or never existed. Try one of these instead.</p>
      <div class="hero-ctas center-row"><a class="btn btn-primary" href="/">Home</a><a class="btn btn-ghost" href="/#shows">Shows</a><a class="btn btn-ghost" href="/podcast/">Podcast</a></div>
    </div></section>'''
    return page("404.html", "Page not found | Evan Lopez", "This page doesn't exist.", body, noindex=True)


def sitemap(paths):
    today = NOW.date().isoformat()
    urls = "".join(f"  <url><loc>{BASE}{p}</loc><lastmod>{today}</lastmod></url>\n" for p in paths)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def llms():
    eps = "\n".join(f"- {x['title']} ({x['date']})" for x in POD["episodes"][:5])
    weekly = "\n".join(f"- {w['name']}: every {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][w['weekday']]} at {ftime(weekly_dates(w,1)[0])}, {w['venue']}, {w['address']}, {w['city']}, {w['region']}. Presented by {w['presenter']}. Tickets: {w['tickets']}" for w in SHOWS["weekly"])
    return f"""# Evan Lopez

> {S["bio_short"]}

## Who
- Evan Lopez is a stand-up comedian based in Austin, Texas.
- Featured on OFTV's most-watched episode of the "LMAOF" stand-up series.
- Has performed at Austin comedy clubs including {", ".join(S["clubs"])} (a regular at East Austin Comedy Club).
- Known online for a viral comedic bird-watching series on Instagram and TikTok ("the birdyverse").
- Born in a small desert town in California; half white, half Puerto Rican; raised as a homeschool kid.
- Founder and producer of Top Flight Comedy ({S["topflight"]["url"]}), an Austin comedy production company.

## Podcast
- Seven Minutes in Evan: a weekly comedy podcast hosted by Evan Lopez, {POD["count"]} episodes.
- Spotify: {S["podcast"]["spotify"]}
- Apple Podcasts: {S["podcast"]["apple"]}
- Recent episodes:
{eps}

## Live shows
{weekly}
- Tour dates are listed at {BASE}#shows as they are announced.

## Pages
- Home: {BASE}
- Podcast: {BASE}podcast/
- Austin comedy guide (where to see stand-up in Austin): {BASE}austin-comedy/
- Press kit (bios, credits, photos): {BASE}press/

## Social
""" + "\n".join(f"- {s['name']}: {s['url']}" for s in S["socials"]) + f"""

## Contact
- Booking, press and podcast guests: {S["email"]}
"""


def main():
    pages = {"index.html": home(), "podcast/index.html": podcast_page(), "austin-comedy/index.html": austin_page(),
             "press/index.html": press_page(), "404.html": not_found()}
    for p, t in pages.items():
        write(p, t)
    for src, to in REDIRECTS.items():
        write(f"{src}/index.html", redirect_stub(to))
    write("sitemap.xml", sitemap(["", "podcast/", "austin-comedy/", "press/"]))
    write("llms.txt", llms())
    print(f"built {len(pages)} pages + {len(REDIRECTS)} redirects")


if __name__ == "__main__":
    main()
