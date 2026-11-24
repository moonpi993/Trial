"""Build the storyboard page from reel.json and the thumbnails made by crop_thumbs.py.

usage: python3 build_storyboard.py reel.json THUMBS_DIR OUT.html
Uses these optional reel.json fields:
  "storyboard": {
    "intro": "one or two sentences: the idea and what it borrows from the reference",
    "reference": {"name": "...", "techniques": [["Title over moving shots", "what it does"], ...],
                  "frames": [["/path/frame.jpg", "0:03 title over shots"], ...]},
    "questions": ["Title words ...?", "Music ...?", "Length ...?"]
  }
  sections[].title / sections[].note   heading and one-line description per section
  shots[].what / shots[].sound         what the viewer sees / hears on that shot
Every frame is the real crop, so the user approves exactly what will be rendered.
"""
import base64, html, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelspec import load_spec, load_style, timeline, sections, local_font_css

spec_path, thumbs, out = sys.argv[1:4]
spec = load_spec(spec_path); style = load_style(spec["style"])
rows, total = timeline(spec); order, win = sections(spec, rows, total)
sec = {s["id"]: s for s in spec.get("sections", [])}
sb = spec.get("storyboard", {}); e = html.escape
b64 = lambda p: "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()
fb, fa, pal = style["fonts"]["bold"], style["fonts"]["accent"], style["palette"]
ls = style.get("line_scale", 1)

def cap(label, line):
    l1 = f'<span class="lb" style="{e(style["label_css"])}">{e(label)}</span>' if label else ""
    l2 = f'<span class="ln" style="{e(style["line_css"])}">{e(line)}</span>' if line else ""
    return f'<span class="cap">{l1}{l2}</span>' if (l1 or l2) else ""

strips = ""
for sid in order:
    s = sec.get(sid, {}); a, b = win[sid]
    items = ""
    for i, r in enumerate(x for x in rows if x["section"] == sid):
        label = line = ""
        if i == 0 and (s.get("label") or s.get("line")):
            label, line = s.get("label", ""), s.get("line", "")
        if s.get("lines"):
            n = len(s["lines"]); k = sum(1 for x in rows if x["section"] == sid)
            for j in range(n):
                if i == j * k // n:
                    item = s["lines"][j]
                    line = item if isinstance(item, str) else item.get("text", "")
        moves = [m for m, on in (("2x speed", r.get("speed", 1) != 1), ("push-in", r.get("push")), ("180° roll", r.get("roll"))) if on]
        zoom = "full frame" if r.get("zoom", 1) <= 1 else f'{r["zoom"]:.1f}x punch-in'
        items += f'''<li class="shot"><div class="fr"><img src="{b64(os.path.join(thumbs, r["id"] + ".jpg"))}" alt="Shot {r['id']}" width="270" height="480" loading="lazy">{cap(label, line)}</div>
<div class="meta"><span class="num">{e(r["id"])}</span><span>{r["start"]:05.2f}s · {r["end"] - r["start"]:.2f}s</span></div>
<p class="what">{e(r.get("what", ""))}</p>{f'<p class="snd">{e(r["sound"])}</p>' if r.get("sound") else ""}
<p class="src">{e(r["src"])}{"" if spec["sources"][r["src"]]["kind"] == "image" else f' @ {r.get("in", 0):.1f}s'} · {zoom}{" · " + ", ".join(moves) if moves else ""}</p></li>'''
    head = s.get("title") or " · ".join(x for x in (s.get("label"), s.get("line")) if x) or sid
    strips += f'''<section class="part"><header><h2>{e(head)}</h2><span class="rng">{a:.1f} to {b:.1f}s · {len([x for x in rows if x["section"] == sid])} shots</span></header>
{f'<p class="lede">{e(s["note"])}</p>' if s.get("note") else ""}<ol class="strip">{items}</ol></section>'''

ref = sb.get("reference")
ref_html = ""
if ref:
    tech = "".join(f"<li><b>{e(t)}.</b> {e(d)}</li>" for t, d in ref.get("techniques", []))
    frs = "".join(f'<figure><img src="{b64(p)}" alt="" width="270" height="480"><figcaption>{e(c)}</figcaption></figure>' for p, c in ref.get("frames", []) if os.path.exists(p))
    ref_html = f'''<section class="ref"><div><p class="kick">From the reference{": " + e(ref["name"]) if ref.get("name") else ""}</p><h2>Techniques to adapt</h2><ul>{tech}</ul></div>{f'<div class="reffr">{frs}</div>' if frs else ""}</section>'''

tc = spec.get("title_card"); look = ""
if tc and rows:
    look = f'''<section class="look"><div class="phone"><img src="{b64(os.path.join(thumbs, rows[min(2, len(rows)-1)]["id"] + ".jpg"))}" alt="Title preview">
<div class="tmock"><span class="lb" style="{e(style["label_css"])}">{e(tc.get("kicker",""))}</span><span class="ln big" style="{e(style["line_css"])}">{e(tc.get("word",""))}</span><span class="lb tg" style="{e(style["label_css"])}">{e(tc.get("tag",""))}</span></div></div>
<div><p class="kick">Look: {e(style["name"])}</p><h2>{e(style["mood"])}</h2>
<p class="lede">Fonts: {e(fb["family"])} (bold) and {e(fa["family"])}. Palette: {pal["light"]}, {pal["dark"]}, {pal["accent"]}. Every frame on this page already has the style's color grade.</p></div></section>'''

qs = "".join(f"<li>{e(q)}</li>" for q in sb.get("questions", []))
gf = "https://fonts.googleapis.com/css2?" + "".join(f"family={f['google']}&" for f in (fb, fa) if f.get("google")) + "family=DM+Sans:wght@400;500;700&display=swap"
local_css = local_font_css(fb, fb["family"]) + local_font_css(fa, fa["family"])
page = f'''<title>{e(spec.get("title", "Reel"))} Storyboard</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="{gf}">
<style>
{local_css}
/* Layout: intro, reference digest, look card, then one horizontal film strip per section, then open questions */
:root {{ --l: {pal["light"]}; --d: {pal["dark"]}; --accent-c: {pal["accent"]}; --light: {pal["light"]}; --dark: {pal["dark"]};
  --bg: color-mix(in srgb, var(--l) 92%, var(--d)); --panel: color-mix(in srgb, var(--l) 80%, var(--d)); --ink: var(--d);
  --muted: color-mix(in srgb, var(--d) 70%, var(--l)); --line: color-mix(in srgb, var(--d) 22%, var(--l));
  --bold: "{fb["family"]}", sans-serif; --accent: "{fa["family"]}", cursive; --ui: "DM Sans", system-ui, sans-serif; --ls: {ls}; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: color-mix(in srgb, var(--d) 92%, #000); --panel: color-mix(in srgb, var(--d) 80%, var(--l)); --ink: var(--l); --muted: color-mix(in srgb, var(--l) 70%, var(--d)); --line: color-mix(in srgb, var(--l) 20%, var(--d)); color-scheme: dark }} }}
:root[data-theme="dark"] {{ --bg: color-mix(in srgb, var(--d) 92%, #000); --panel: color-mix(in srgb, var(--d) 80%, var(--l)); --ink: var(--l); --muted: color-mix(in srgb, var(--l) 70%, var(--d)); --line: color-mix(in srgb, var(--l) 20%, var(--d)); color-scheme: dark }}
body {{ background: var(--bg); color: var(--ink); font: 15px/1.55 var(--ui); }}
.wrap {{ max-width: 1180px; margin: 0 auto; padding-block: 40px 72px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: grid; gap: 48px; }}
h1, h2 {{ margin: 0; text-wrap: balance; }}
h1 {{ font: 700 clamp(2rem, 6vw, 3.6rem)/1 var(--bold); text-transform: uppercase; letter-spacing: -.01em; }}
h2 {{ font: 700 1.35rem/1.2 var(--bold); }}
.kick {{ font: 700 12px var(--ui); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin: 0 0 8px; }}
.intro p, .lede {{ max-width: 66ch; color: var(--muted); margin: 12px 0 0; }}
.facts {{ display: flex; flex-wrap: wrap; gap: 6px 22px; margin-top: 16px; font-size: 13px; color: var(--muted); font-variant-numeric: tabular-nums; }}
.facts b {{ color: var(--ink); }}
.ref {{ display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr); gap: 28px; align-items: start; }}
.ref ul {{ margin: 12px 0 0; padding-left: 18px; display: grid; gap: 8px; }}
.reffr {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; }}
.reffr figure {{ margin: 0; }} figcaption {{ font-size: 11px; color: var(--muted); margin-top: 4px; }}
.reffr img, .fr img {{ display: block; width: 100%; height: auto; aspect-ratio: 9/16; object-fit: cover; border-radius: 8px; }}
.look {{ display: grid; grid-template-columns: 220px minmax(0, 1fr); gap: 28px; align-items: center; }}
.phone {{ position: relative; width: 220px; max-width: 100%; aspect-ratio: 9/16; border-radius: 14px; overflow: hidden; container-type: inline-size; }}
.phone img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.tmock {{ position: absolute; left: 6cqw; right: 6cqw; top: 15%; text-align: center; font-size: 5.2cqw; }}
.tmock .lb {{ display: inline-block; }} .tmock .tg {{ font-size: .72em; margin-top: 4cqw; letter-spacing: .16em; }}
.tmock .big {{ display: block; font-size: calc(23cqw * var(--ls)); line-height: .85; }}
.part header {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 16px; padding-bottom: 10px; border-bottom: 2px solid var(--ink); }}
.rng {{ font-size: 13px; color: var(--muted); font-variant-numeric: tabular-nums; }}
.strip {{ list-style: none; margin: 14px 0 0; padding: 0 0 10px; display: grid; grid-auto-flow: column; grid-auto-columns: 150px; gap: 14px; overflow-x: auto; scroll-snap-type: x proximity; }}
.shot {{ scroll-snap-align: start; min-width: 0; }}
.fr {{ position: relative; border-radius: 8px; overflow: hidden; container-type: inline-size; }}
.cap {{ position: absolute; left: 9cqw; right: 6cqw; top: 52%; font-size: 4.8cqw; }}
.cap .lb {{ display: inline-block; }} .cap .ln {{ display: block; font-size: calc(12.5cqw * var(--ls)); line-height: .95; margin-top: 1cqw; }}
.meta {{ display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; }}
.num {{ color: var(--ink); font-weight: 700; }}
.what {{ margin: 4px 0 0; font-weight: 500; font-size: 13.5px; line-height: 1.35; }}
.snd {{ margin: 3px 0 0; font-size: 12.5px; color: var(--muted); }} .snd::before {{ content: "♪ "; }}
.src {{ margin: 6px 0 0; font-size: 10.5px; color: var(--muted); }}
.ask {{ border-top: 2px solid var(--ink); padding-top: 22px; }} .ask ol {{ margin: 12px 0 0; padding-left: 20px; display: grid; gap: 10px; max-width: 72ch; }}
@media (max-width: 760px) {{ .ref, .look {{ grid-template-columns: minmax(0, 1fr); }} .strip {{ grid-auto-columns: 128px; }} }}
</style>
<div class="wrap">
  <div class="intro"><p class="kick">Storyboard · draft for approval</p><h1>{e(spec.get("title", "Reel"))}</h1>
    {f'<p>{e(sb["intro"])}</p>' if sb.get("intro") else ""}
    <div class="facts"><span><b>{total:.1f}s</b> total</span><span><b>{len(rows)}</b> shots</span><span><b>9:16</b> vertical</span><span><b>{spec["fps"]} fps</b></span><span>Style: <b>{e(style["name"])}</b></span></div></div>
  {ref_html}{look}{strips}
  {f'<section class="ask"><p class="kick">Before I render</p><h2>To decide</h2><ol>{qs}</ol></section>' if qs else ""}
</div>
'''
open(out, "w").write(page)
print(f"storyboard: {len(rows)} shots, {total}s -> {out}")
