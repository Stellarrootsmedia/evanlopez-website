/* evanlopez.com — tiny, dependency-free */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // mobile menu
  const btn = $('.menu-btn'), nav = $('.nav');
  if (btn && nav) {
    btn.addEventListener('click', () => {
      const open = btn.getAttribute('aria-expanded') !== 'true';
      btn.setAttribute('aria-expanded', open); nav.classList.toggle('open', open);
    });
    $$('.nav a').forEach(a => a.addEventListener('click', () => { btn.setAttribute('aria-expanded', 'false'); nav.classList.remove('open'); }));
  }

  // keep "Next: Fri, Oct 2" fresh between builds (Austin time)
  $$('time[data-weekly]').forEach(t => {
    const wd = (+t.dataset.weekly + 1) % 7;                     // data uses Mon=0; JS uses Sun=0
    const [h, m] = t.dataset.time.split(':').map(Number);
    const now = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/Chicago' }));
    const d = new Date(now); d.setHours(h, m, 0, 0);
    d.setDate(d.getDate() + ((wd - d.getDay() + 7) % 7));
    if (d < now) d.setDate(d.getDate() + 7);
    t.textContent = d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  });

  // click-to-load YouTube (no third-party JS until someone presses play)
  $$('.yt-facade').forEach(el => el.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = `https://www.youtube-nocookie.com/embed/${el.dataset.yt}?autoplay=1&playsinline=1`;
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen'; f.title = el.getAttribute('aria-label') || 'Video';
    el.replaceChildren(f);
  }, { once: true }));

  // click-to-load Spotify
  $$('.spot-facade').forEach(el => el.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.className = 'spot-embed'; f.loading = 'lazy'; f.title = 'Seven Minutes in Evan on Spotify';
    f.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture';
    f.src = `https://open.spotify.com/embed/show/${el.dataset.spotify}?theme=0`;
    el.replaceWith(f);
  }, { once: true }));

  // forms → FormSubmit (ajax)
  $$('form[data-endpoint]').forEach(form => form.addEventListener('submit', async ev => {
    ev.preventDefault();
    const note = $('.form-note', form), b = $('button[type=submit]', form), label = b.textContent;
    b.disabled = true; b.textContent = 'Sending…';
    try {
      const res = await fetch(form.dataset.endpoint, { method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(form) });
      if (!res.ok) throw new Error(res.status);
      form.reset();
      note.className = 'form-note ok';
      note.textContent = form.classList.contains('signup') ? "You're on the list. Talk soon." : "Got it. I'll get back to you soon.";
      if (window.gtag) gtag('event', form.classList.contains('signup') ? 'sign_up' : 'generate_lead');
    } catch {
      note.className = 'form-note err';
      note.innerHTML = 'That didn’t go through. Email <a href="mailto:contact@evanlopez.com">contact@evanlopez.com</a> instead.';
    } finally { b.disabled = false; b.textContent = label; }
  }));

  // copy buttons (press kit)
  $$('[data-copy]').forEach(b => b.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText($('#' + b.dataset.copy).innerText.trim()); b.textContent = 'Copied'; }
    catch { b.textContent = 'Select & copy'; }
    setTimeout(() => (b.textContent = 'Copy'), 1800);
  }));

  // track outbound clicks that matter (tickets, listen, follow)
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href^="http"]');
    if (a && window.gtag && !a.href.includes(location.hostname)) gtag('event', 'click_out', { link_url: a.href, link_text: a.textContent.trim().slice(0, 40) });
  });

  // gentle reveal (skipped for reduced motion)
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(x => { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } }), { rootMargin: '0px 0px -8% 0px' });
    $$('.sec-head, .tile, .date-row, .weekly, .empty-tour, .frame, .latest, .merch-drop, .tf-card, .ep-card, .club').forEach(el => { el.classList.add('reveal'); io.observe(el); });
  }
})();
