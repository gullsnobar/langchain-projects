import html

import gradio as gr

from src.data import load_books
from src.recommender import recommend_books

# --------------------------------------------------------------------------
# Data (loaded once at startup, backend untouched)
# --------------------------------------------------------------------------
df = load_books()

EXAMPLES = [
    "Dystopian future with government surveillance",
    "Cozy mystery in a small English village",
    "Epic fantasy with political intrigue",
    "A story about grief and healing",
]

# --------------------------------------------------------------------------
# Helpers: backend results -> HTML cards
# --------------------------------------------------------------------------
def _clean(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() in {"nan", "none"} else html.escape(text)


def _truncate(text: str, limit: int = 200) -> str:
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "..."


def _notice(message: str) -> str:
    return f'<div class="notice">{html.escape(message)}</div>'


def _empty_state() -> str:
    return '<div class="empty">Your recommendations will appear here.</div>'


def _card(rank: int, row) -> str:
    title = _clean(row.get("title")) or "Untitled"
    authors = _clean(row.get("authors")) or "Unknown author"
    desc = _truncate(_clean(row.get("description")))
    desc_html = f'<p class="book-desc">{desc}</p>' if desc else ""
    return (
        '<article class="book-card">'
        f'<div class="book-rank">{rank:02d}</div>'
        '<div class="book-body">'
        f'<h3 class="book-title">{title}</h3>'
        f'<div class="book-author">{authors}</div>'
        f"{desc_html}"
        "</div>"
        "</article>"
    )


def search_books(query):
    if not query or not query.strip():
        return _notice("Type a mood, plot or theme to get started.")

    results = recommend_books(query, df)  # returns a DataFrame

    if results is None or len(results) == 0:
        return _notice("No matches found. Try describing it differently.")

    cards = "".join(
        _card(i, row) for i, (_, row) in enumerate(results.iterrows(), start=1)
    )
    return f'<div class="results-grid">{cards}</div>'


# --------------------------------------------------------------------------
# <head>: font, GSAP, Three.js and behaviour JS.
# (<script> inside gr.HTML does not execute, so it goes through Blocks(head=).)
# --------------------------------------------------------------------------
HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function () {
  var root = document.documentElement;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Theme ---------- */
  function getSaved() { try { return localStorage.getItem('sbr-theme'); } catch (e) { return null; } }
  function setTheme(t) {
    root.setAttribute('data-theme', t);
    if (document.body) document.body.classList.toggle('dark', t === 'dark');
    try { localStorage.setItem('sbr-theme', t); } catch (e) {}
    if (window.__recolor) window.__recolor();
  }
  var initial = getSaved() || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  root.setAttribute('data-theme', initial);
  document.addEventListener('DOMContentLoaded', function () { setTheme(initial); });
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('#theme-toggle');
    if (t) setTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
  });

  /* ---------- Loading state ---------- */
  var loadingTimer = null;
  window.__boost = 1;
  window.__searchStart = function () {
    var g = document.getElementById('glass');
    if (g) g.classList.add('is-loading');
    var r = document.getElementById('results');
    if (r && window.gsap) gsap.to(r, { opacity: 0.3, duration: 0.25 });
    window.__boost = 4;
    clearTimeout(loadingTimer);
    loadingTimer = setTimeout(endLoading, 60000);
  };
  function endLoading() {
    var g = document.getElementById('glass');
    if (g) g.classList.remove('is-loading');
    var r = document.getElementById('results');
    if (r && window.gsap) gsap.to(r, { opacity: 1, duration: 0.3 });
    window.__boost = 1;
    clearTimeout(loadingTimer);
  }

  /* ---------- GSAP: entrance + results ---------- */
  function animateNew() {
    if (!window.gsap) return;

    var intro = document.querySelectorAll('.anim-in:not([data-a])');
    if (intro.length) {
      intro.forEach(function (n) { n.setAttribute('data-a', '1'); });
      if (!reduceMotion)
        gsap.fromTo(intro, { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.8, ease: 'power3.out', stagger: 0.1 });
    }

    var fresh = document.querySelectorAll('.book-card:not([data-a]), .notice:not([data-a]), .empty:not([data-a])');
    if (fresh.length) {
      var hasResult = false;
      fresh.forEach(function (n) {
        n.setAttribute('data-a', '1');
        if (!n.classList.contains('empty')) hasResult = true;
      });
      if (!reduceMotion)
        gsap.fromTo(fresh, { opacity: 0, y: 24 },
          { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', stagger: 0.07 });
      if (hasResult) endLoading();
    }
  }
  new MutationObserver(animateNew).observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener('DOMContentLoaded', animateNew);

  /* ---------- GSAP: card hover (simple lift) ---------- */
  document.addEventListener('mouseover', function (e) {
    if (!window.gsap || reduceMotion) return;
    var card = e.target.closest && e.target.closest('.book-card');
    if (card && !card.contains(e.relatedTarget))
      gsap.to(card, { x: 6, duration: 0.3, ease: 'power2.out' });
  });
  document.addEventListener('mouseout', function (e) {
    if (!window.gsap) return;
    var card = e.target.closest && e.target.closest('.book-card');
    if (card && !card.contains(e.relatedTarget))
      gsap.to(card, { x: 0, duration: 0.4, ease: 'power3.out' });
  });

  /* ---------- Three.js: slow particle network ---------- */
  function initScene() {
    if (!window.THREE || document.getElementById('bg-canvas')) return;

    var canvas = document.createElement('canvas');
    canvas.id = 'bg-canvas';
    document.body.appendChild(canvas);

    var renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(60, 1, 0.1, 300);
    camera.position.z = 70;

    var N = 80, BOX = { x: 90, y: 55, z: 35 }, LINK = 18, MAX_SEG = 300;
    var pos = new Float32Array(N * 3), vel = new Float32Array(N * 3);
    for (var i = 0; i < N; i++) {
      pos[i * 3]     = (Math.random() - 0.5) * BOX.x * 2;
      pos[i * 3 + 1] = (Math.random() - 0.5) * BOX.y * 2;
      pos[i * 3 + 2] = (Math.random() - 0.5) * BOX.z * 2;
      vel[i * 3]     = (Math.random() - 0.5) * 0.04;
      vel[i * 3 + 1] = (Math.random() - 0.5) * 0.04;
      vel[i * 3 + 2] = (Math.random() - 0.5) * 0.025;
    }

    var pGeo = new THREE.BufferGeometry();
    pGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    var pMat = new THREE.PointsMaterial({ size: 1.5, transparent: true, opacity: 0.7, sizeAttenuation: true });
    var points = new THREE.Points(pGeo, pMat);

    var lPos = new Float32Array(MAX_SEG * 6);
    var lGeo = new THREE.BufferGeometry();
    lGeo.setAttribute('position', new THREE.BufferAttribute(lPos, 3));
    lGeo.setDrawRange(0, 0);
    var lMat = new THREE.LineBasicMaterial({ transparent: true, opacity: 0.14 });
    var lines = new THREE.LineSegments(lGeo, lMat);

    var group = new THREE.Group();
    group.add(points); group.add(lines);
    scene.add(group);

    window.__recolor = function () {
      var c = getComputedStyle(root).getPropertyValue('--particle').trim() || '#888888';
      pMat.color = new THREE.Color(c);
      lMat.color = new THREE.Color(c);
    };
    window.__recolor();

    function resize() {
      var w = window.innerWidth, h = window.innerHeight;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    window.addEventListener('resize', resize);
    resize();

    var tx = 0, ty = 0;
    window.addEventListener('mousemove', function (e) {
      tx = (e.clientX / window.innerWidth - 0.5) * 0.3;
      ty = (e.clientY / window.innerHeight - 0.5) * 0.2;
    });

    var speed = 1, running = true;
    document.addEventListener('visibilitychange', function () {
      running = !document.hidden;
      if (running) tick();
    });

    function tick() {
      if (!running) return;
      requestAnimationFrame(tick);

      speed += ((reduceMotion ? 0 : window.__boost) - speed) * 0.05;
      for (var i = 0; i < N; i++) {
        var k = i * 3;
        pos[k]     += vel[k] * speed;
        pos[k + 1] += vel[k + 1] * speed;
        pos[k + 2] += vel[k + 2] * speed;
        if (Math.abs(pos[k]) > BOX.x)     vel[k] *= -1;
        if (Math.abs(pos[k + 1]) > BOX.y) vel[k + 1] *= -1;
        if (Math.abs(pos[k + 2]) > BOX.z) vel[k + 2] *= -1;
      }
      pGeo.attributes.position.needsUpdate = true;

      var seg = 0;
      for (var a = 0; a < N && seg < MAX_SEG; a++) {
        for (var b = a + 1; b < N && seg < MAX_SEG; b++) {
          var dx = pos[a * 3] - pos[b * 3];
          var dy = pos[a * 3 + 1] - pos[b * 3 + 1];
          var dz = pos[a * 3 + 2] - pos[b * 3 + 2];
          if (dx * dx + dy * dy + dz * dz < LINK * LINK) {
            var o = seg * 6;
            lPos[o] = pos[a * 3]; lPos[o + 1] = pos[a * 3 + 1]; lPos[o + 2] = pos[a * 3 + 2];
            lPos[o + 3] = pos[b * 3]; lPos[o + 4] = pos[b * 3 + 1]; lPos[o + 5] = pos[b * 3 + 2];
            seg++;
          }
        }
      }
      lGeo.setDrawRange(0, seg * 2);
      lGeo.attributes.position.needsUpdate = true;

      group.rotation.y += (tx - group.rotation.y) * 0.03 + 0.0003 * speed;
      group.rotation.x += (ty - group.rotation.x) * 0.03;
      renderer.render(scene, camera);
    }
    tick();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initScene);
  else initScene();
})();
</script>
"""

# --------------------------------------------------------------------------
# CSS: one accent colour, flat surfaces, bold type. Dark default + light theme.
# --------------------------------------------------------------------------
CSS = """
:root {
  --bg: #0c0c0d;
  --fg: #f4f4f5;
  --muted: #9a9aa2;
  --panel: rgba(20, 20, 22, 0.72);
  --card: rgba(255, 255, 255, 0.03);
  --border: rgba(255, 255, 255, 0.12);
  --accent: #ff5a1f;
  --accent-fg: #ffffff;
  --particle: #9a9aa2;
}
:root[data-theme="light"] {
  --bg: #f6f4ef;
  --fg: #101010;
  --muted: #666660;
  --panel: rgba(255, 255, 255, 0.7);
  --card: rgba(255, 255, 255, 0.6);
  --border: rgba(16, 16, 16, 0.14);
  --accent: #e8460f;
  --particle: #77776f;
}

html, body, gradio-app {
  background: var(--bg) !important;
  color: var(--fg);
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif !important;
  transition: background 0.3s ease, color 0.3s ease;
}
.gradio-container, .gradio-container * { font-family: inherit; }
.gradio-container {
  position: relative;
  z-index: 1;
  background: transparent !important;
  max-width: 820px !important;
  margin: 0 auto !important;
  padding: 48px 20px 80px !important;
}
.gradio-container .block, .gradio-container .form, .gradio-container .gap,
.gradio-container .row, .gradio-container .column {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
footer { display: none !important; }

/* Three.js canvas: behind everything, never captures input */
#bg-canvas {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  z-index: 0;
  pointer-events: none;
}

/* ---------- Header ---------- */
.topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 56px; }
.brand { font-weight: 800; font-size: 15px; letter-spacing: -0.01em; color: var(--fg); }
#theme-toggle {
  cursor: pointer;
  background: transparent;
  color: var(--fg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 600;
  transition: border-color 0.2s ease, color 0.2s ease;
}
#theme-toggle::after { content: "Light mode"; }
:root[data-theme="light"] #theme-toggle::after { content: "Dark mode"; }
#theme-toggle:hover { border-color: var(--accent); color: var(--accent); }

.hero { margin: 0 0 36px; }
.hero h1 {
  font-size: clamp(40px, 8vw, 72px);
  line-height: 1;
  font-weight: 800;
  letter-spacing: -0.04em;
  margin: 0 0 18px;
  color: var(--fg);
}
.hero h1 span { color: var(--accent); }
.hero p { color: var(--muted); font-size: 18px; margin: 0; max-width: 520px; line-height: 1.55; }

/* ---------- Search panel (subtle glass, plain border) ---------- */
#glass {
  position: relative;
  padding: 20px !important;
  border-radius: 16px !important;
  border: 1px solid var(--border) !important;
  background: var(--panel) !important;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  gap: 14px !important;
  overflow: hidden;
}
/* thin loading bar */
#glass::after {
  content: "";
  position: absolute;
  left: 0; top: 0;
  height: 3px; width: 100%;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  opacity: 0;
}
#glass.is-loading::after {
  opacity: 1;
  animation: bar 1.1s ease-in-out infinite;
}
@keyframes bar {
  0%   { transform: scaleX(0); transform-origin: left; }
  50%  { transform: scaleX(1); transform-origin: left; }
  51%  { transform: scaleX(1); transform-origin: right; }
  100% { transform: scaleX(0); transform-origin: right; }
}

/* Input row */
#palette {
  display: flex !important;
  flex-wrap: nowrap !important;
  align-items: center;
  gap: 10px !important;
  padding: 6px 6px 6px 16px !important;
  border-radius: 12px !important;
  background: transparent !important;
  border: 2px solid var(--border) !important;
  transition: border-color 0.2s ease;
}
#palette:focus-within { border-color: var(--accent) !important; }
#query-box { flex: 1 1 auto !important; min-width: 0 !important; }
#query-box textarea, #query-box input {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: var(--fg) !important;
  font-size: 18px !important;
  font-weight: 500 !important;
  padding: 10px 0 !important;
}
#query-box textarea::placeholder { color: var(--muted) !important; opacity: 1; }
#query-box textarea:focus { outline: none !important; }

#search-btn {
  flex: 0 0 auto !important;
  min-width: 120px !important;
  height: 46px;
  border: none !important;
  border-radius: 8px !important;
  color: var(--accent-fg) !important;
  font-weight: 700 !important;
  font-size: 15px !important;
  background: var(--accent) !important;
  transition: transform 0.15s ease, filter 0.2s ease;
}
#search-btn:hover { filter: brightness(1.1); }
#search-btn:active { transform: scale(0.97); }
#glass.is-loading #search-btn { opacity: 0.6; pointer-events: none; }

.hint { color: var(--muted); font-size: 13px; margin: 0 2px; }

/* Example chips */
#chips { display: flex !important; flex-wrap: wrap !important; gap: 8px !important; }
.chip {
  flex: 0 0 auto !important;
  width: auto !important;
  min-width: 0 !important;
  border-radius: 8px !important;
  padding: 6px 12px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  color: var(--muted) !important;
  background: transparent !important;
  border: 1px solid var(--border) !important;
  transition: color 0.2s ease, border-color 0.2s ease;
}
.chip:hover { color: var(--fg) !important; border-color: var(--accent) !important; }

/* ---------- Results ---------- */
#results { margin-top: 32px; }
.results-grid { display: grid; gap: 12px; }
.book-card {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  padding: 20px 22px;
  border-radius: 12px;
  background: var(--card);
  border: 1px solid var(--border);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: border-color 0.2s ease, background 0.2s ease;
}
.book-card:hover { border-color: var(--accent); }
.book-rank {
  flex: 0 0 auto;
  min-width: 36px;
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: -0.03em;
  color: var(--accent);
  font-variant-numeric: tabular-nums;
}
.book-body { min-width: 0; }
.book-title { margin: 0 0 4px; font-size: 20px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.25; color: var(--fg); }
.book-author { font-size: 14px; font-weight: 500; color: var(--muted); }
.book-desc { margin: 10px 0 0; font-size: 14px; line-height: 1.6; color: var(--muted); }

.notice, .empty {
  padding: 28px 20px;
  border-radius: 12px;
  border: 1px dashed var(--border);
  color: var(--muted);
  font-size: 15px;
}

/* Hide Gradio's own progress overlay; we use our own loading bar */
#results .wrap, #results .generating, #results .pending { display: none !important; }

@media (max-width: 640px) {
  .gradio-container { padding-top: 28px !important; }
  .topbar { margin-bottom: 36px; }
  #palette { flex-wrap: wrap !important; padding: 10px !important; }
  #search-btn { width: 100% !important; }
  .book-card { gap: 14px; padding: 16px; }
  .book-rank { font-size: 22px; min-width: 28px; }
}
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; }
}
"""

# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
START_LOADING_JS = "() => { if (window.__searchStart) window.__searchStart(); }"


def _make_setter(text):
    def _setter():
        return text
    return _setter


# Gradio 6 moved `css` / `head` from gr.Blocks() to launch(); Gradio 4/5 take
# them on gr.Blocks(). Handle both so the styling always applies.
_GRADIO_MAJOR = int(gr.__version__.split(".")[0])
_blocks_kwargs = {"title": "Semantic Book Recommender"}
if _GRADIO_MAJOR < 6:
    _blocks_kwargs.update(css=CSS, head=HEAD)

demo = gr.Blocks(**_blocks_kwargs)

with demo:
    gr.HTML(
        """
        <div class="topbar anim-in">
          <span class="brand">Book Recommender</span>
          <button id="theme-toggle" type="button"></button>
        </div>
        <section class="hero">
          <h1 class="anim-in">Find your next<br><span>book.</span></h1>
          <p class="anim-in">Describe a mood, a plot or a theme. Get books that match the meaning, not just the keywords.</p>
        </section>
        """
    )

    with gr.Column(elem_id="glass", elem_classes="anim-in"):
        with gr.Row(elem_id="palette"):
            query_input = gr.Textbox(
                show_label=False,
                container=False,
                placeholder="What do you want to read?",
                lines=1,
                max_lines=1,
                elem_id="query-box",
            )
            search_btn = gr.Button("Search", variant="primary", elem_id="search-btn")

        gr.HTML('<div class="hint">Press Enter to search, or try an example:</div>')

        with gr.Row(elem_id="chips"):
            chip_buttons = [
                gr.Button(text, elem_classes="chip", size="sm") for text in EXAMPLES
            ]

    output_html = gr.HTML(value=_empty_state(), elem_id="results")

    # ----- Events -----
    for trigger in (search_btn.click, query_input.submit):
        trigger(fn=None, js=START_LOADING_JS)
        trigger(
            fn=search_books,
            inputs=query_input,
            outputs=output_html,
            show_progress="hidden",
        )

    for btn, text in zip(chip_buttons, EXAMPLES):
        btn.click(fn=None, js=START_LOADING_JS)
        btn.click(fn=_make_setter(text), outputs=query_input, show_progress="hidden").then(
            fn=search_books,
            inputs=query_input,
            outputs=output_html,
            show_progress="hidden",
        )


if _GRADIO_MAJOR >= 6:
    # Inject the styling into launch() so it works even when another file
    # (e.g. app.py) simply calls demo.launch().
    _original_launch = demo.launch

    def _launch_with_style(*args, **kwargs):
        kwargs.setdefault("css", CSS)
        kwargs.setdefault("head", HEAD)
        return _original_launch(*args, **kwargs)

    demo.launch = _launch_with_style


if __name__ == "__main__":
    demo.launch()