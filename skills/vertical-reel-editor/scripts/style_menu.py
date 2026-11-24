"""Build the visual style menu: the user's own frames shown in every style, so they pick a look by eye.

usage: python3 style_menu.py OUT.html frame1.jpg [frame2.jpg ...] [--label "STEP 1"] [--line "ignore the alarm"]
         [--title "Kanzoo's style menu"] [--current sleepy-diary]
Frames should be 9:16 crops of the user's footage (crop_thumbs.py output works; 270x480 or larger).
Each card shows: the grade applied with the real FFmpeg filter, a caption in the style's two fonts and palette,
mood, what it suits, pacing, fonts and swatches. Publish the HTML as an artifact and ask the user to pick one.
"""
import base64, html, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelspec import STYLES_PATH, local_font_css

args = sys.argv[1:]
def opt(name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
label, line = opt("--label", "STEP 1"), opt("--line", "ignore the alarm")
title, current = opt("--title", "Style menu"), opt("--current", "")
out, frames = args[0], args[1:]
styles = json.load(open(STYLES_PATH))["styles"]
tmp = tempfile.mkdtemp(); e = html.escape

def graded(frame, grade, key):
    p = os.path.join(tmp, f"{key}.jpg")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", frame, "-vf", f"scale=540:960:force_original_aspect_ratio=increase,crop=540:960,{grade}",
                    "-q:v", "3", p], check=True)
    return "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()

families = sorted({s["fonts"][r]["google"] for s in styles.values() for r in ("bold", "accent") if s["fonts"][r].get("google")})
local_css = "".join(local_font_css(s["fonts"][r], s["fonts"][r]["family"]) for s in styles.values() for r in ("bold", "accent"))
gfonts = "https://fonts.googleapis.com/css2?" + "&".join(f"family={f}" for f in families + ["DM+Sans:wght@400;500;700"]) + "&display=swap"

cards = []
for key, s in styles.items():
    fb, fa, pal = s["fonts"]["bold"], s["fonts"]["accent"], s["palette"]
    imgs = [graded(f, s["grade"], f"{key}_{i}") for i, f in enumerate(frames[:3])]
    tokens = (f"--light:{pal['light']};--dark:{pal['dark']};--accent-c:{pal['accent']};"
              f"--bold:'{fb['family']}',sans-serif;--accent:'{fa['family']}',cursive;--ls:{s.get('line_scale', 1)}")
    extra = "".join(f'<img src="{u}" alt="" width="90" height="160">' for u in imgs[1:])
    sw = "".join(f'<span class="sw" style="background:{c}" title="{c}"></span>' for c in (pal["light"], pal["dark"], pal["accent"]))
    cards.append(f'''<article class="card{' current' if key == current else ''}" id="{key}">
  <div class="phone" style="{tokens}">
    <img src="{imgs[0]}" alt="{e(s['name'])} grade on your footage" width="270" height="480">
    {f'<div class="scrim" style="--scrim:{s["scrim"]}"></div>' if s.get("scrim") else ""}
    <div class="cap"><span class="lb" style="{e(s['label_css'])}">{e(label)}</span><span class="ln" style="{e(s['line_css'])}">{e(line)}</span></div>
  </div>
  <div class="info">
    <h2>{e(s['name'])}{' <small>used last time</small>' if key == current else ''}</h2>
    <p class="mood">{e(s['mood'])}</p>
    <dl><dt>Suits</dt><dd>{e(s['best_for'])}</dd><dt>Pacing</dt><dd>{e(s['pacing'])}</dd>
    <dt>Fonts</dt><dd><span style="font-family:'{fb['family']}';font-weight:{fb['weight']}">{e(fb['family'])}</span> + <span style="font-family:'{fa['family']}';font-weight:{fa['weight']};font-style:{fa.get('style','normal')}">{e(fa['family'])}</span></dd>
    <dt>Palette</dt><dd class="sws">{sw}</dd></dl>
    {f'<div class="more">{extra}</div>' if extra else ''}
    <p class="pick">Pick with: <code>{key}</code></p>
  </div>
</article>''')

page = f'''<title>{e(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="{gfonts}">
<style>
{local_css}
/* Layout: intro, then a two-column grid of style cards (phone preview + spec), one column on phones */
:root {{ --bg: #f3f4f1; --card: #ffffff; --ink: #1b1c1a; --muted: #5d6159; --line: #dfe1db; --hi: #2f6f5e; --ui: "DM Sans", system-ui, sans-serif; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #141513; --card: #1d1f1c; --ink: #ecede9; --muted: #a4a89f; --line: #30332e; --hi: #7fc4ae; color-scheme: dark }} }}
:root[data-theme="dark"] {{ --bg: #141513; --card: #1d1f1c; --ink: #ecede9; --muted: #a4a89f; --line: #30332e; --hi: #7fc4ae; color-scheme: dark }}
body {{ background: var(--bg); color: var(--ink); font: 15px/1.5 var(--ui); }}
.wrap {{ max-width: 1120px; margin: 0 auto; padding-block: 36px 64px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: grid; gap: 28px; }}
h1 {{ font: 700 clamp(1.8rem, 4vw, 2.6rem)/1.1 var(--ui); margin: 0; letter-spacing: -.02em; text-wrap: balance; }}
.intro p {{ color: var(--muted); max-width: 62ch; margin: 10px 0 0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 500px), 1fr)); gap: 18px; }}
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 16px; display: grid; grid-template-columns: 230px minmax(0, 1fr); gap: 18px; }}
.card.current {{ border-color: var(--hi); box-shadow: 0 0 0 1px var(--hi); }}
.phone {{ position: relative; width: 230px; max-width: 100%; aspect-ratio: 9/16; border-radius: 12px; overflow: hidden; background: #000; container-type: inline-size; }}
.phone > img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.scrim {{ position: absolute; inset: 0; background: linear-gradient(to bottom, transparent 50%, var(--scrim) 66%, var(--scrim) 74%, transparent 92%); }}
/* caption scaled from the 1080px Reel layout: 1080px -> 100cqw */
.cap {{ position: absolute; left: 12cqw; right: 8cqw; top: 52%; font-size: 5.2cqw; }}
.lb {{ display: inline-block; font-size: 1em; }}
.ln {{ display: block; font-size: calc(12.2cqw * var(--ls)); line-height: .95; margin-top: 1cqw; }}
.info {{ min-width: 0; display: grid; align-content: start; gap: 8px; }}
.info h2 {{ margin: 0; font: 700 1.25rem/1.2 var(--ui); }}
.info h2 small {{ font: 500 11px var(--ui); color: var(--hi); letter-spacing: .08em; text-transform: uppercase; margin-left: 6px; }}
.mood {{ margin: 0; color: var(--muted); }}
dl {{ margin: 4px 0 0; display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 6px 10px; font-size: 13.5px; }}
dt {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; padding-top: 2px; }}
dd {{ margin: 0; }}
.sws {{ display: flex; gap: 6px; }}
.sw {{ width: 22px; height: 22px; border-radius: 50%; box-shadow: inset 0 0 0 1px rgba(127,127,127,.35); }}
.more {{ display: flex; gap: 6px; }}
.more img {{ width: 54px; height: 96px; object-fit: cover; border-radius: 6px; }}
.pick {{ margin: 2px 0 0; font-size: 12.5px; color: var(--muted); }}
code {{ font: 500 12.5px ui-monospace, monospace; color: var(--ink); background: var(--bg); padding: 1px 6px; border-radius: 4px; }}
@media (max-width: 560px) {{ .card {{ grid-template-columns: minmax(0, 1fr); }} .phone {{ width: 100%; max-width: 280px; }} }}
</style>
<div class="wrap">
  <div class="intro">
    <h1>{e(title)}</h1>
    <p>Every card is your own footage with that style's real color grade, and a caption in its two fonts and palette. Pick one by name, or mix: for example "Soft Film colors with Sleepy Diary fonts".</p>
  </div>
  <div class="grid">{"".join(cards)}</div>
</div>
'''
open(out, "w").write(page)
print(f"style menu with {len(cards)} styles -> {out}")
