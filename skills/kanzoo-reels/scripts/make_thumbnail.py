"""Make a Kanzoo cover/thumbnail in the official look (the user's own Monday thumbnail).

usage:
  python3 make_thumbnail.py OUT.jpg --video clip.mov --at 13.0 [--zoom 1.0 --cx 0.45 --cy 0.5]
  python3 make_thumbnail.py OUT.jpg --image photo.jpg [--zoom 1.0 --cx 0.5 --cy 0.5]
     [--kicker "How to survive a"] [--word "Monday"] [--tag "Kanzoo edition"]
     [--size 2160x3840] [--no-grade]

Look (do not drift from it; the user chose this exact cover):
  - footage graded with the kanzoo-video grade (soft natural coffee light)
  - text block lower-left in the empty space beside him, no fade, no bar, no white
  - kicker + tag: Inter Medium, uppercase, very wide spacing, mocha #694330
  - word: TeX Gyre Chorus, espresso #341D13, large; its descender may touch the tag
Pick a frame where his face fills the upper/right part and the lower-left is calm sheet or fur.
"""
import argparse, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelspec import media_size, crop_box

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--video"); ap.add_argument("--image"); ap.add_argument("--at", type=float, default=0)
ap.add_argument("--zoom", type=float, default=1.0); ap.add_argument("--cx", type=float, default=0.5); ap.add_argument("--cy", type=float, default=0.5)
ap.add_argument("--kicker", default="How to survive a"); ap.add_argument("--word", default="Monday"); ap.add_argument("--tag", default="Kanzoo edition")
ap.add_argument("--size", default="2160x3840"); ap.add_argument("--no-grade", action="store_true")
a = ap.parse_args()
if not (a.video or a.image):
    sys.exit("give --video (with --at) or --image")
W, H = map(int, a.size.split("x"))
src = a.video or a.image
grade = json.load(open(os.path.join(ASSETS, "styles.json")))["styles"]["kanzoo-video"]["grade"]
tmp = tempfile.mkdtemp()
sw, sh = media_size(src)
cw, ch, x, y = crop_box(sw, sh, a.zoom, a.cx, a.cy)
vf = f"crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos" + ("" if a.no_grade else f",{grade}")
seek = ["-ss", str(a.at)] if a.video else []
bg = os.path.join(tmp, "bg.jpg")
subprocess.run(["ffmpeg", "-v", "error", "-y", *seek, "-i", src, "-map", "0:v:0", "-frames:v", "1", "-vf", vf, "-q:v", "1", bg], check=True)

fonts = os.path.abspath(os.path.join(ASSETS, "fonts"))
esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;")
html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Chorus"; src: url("file://{fonts}/texgyrechorus-mediumitalic.otf") format("opentype"); }}
@font-face {{ font-family: "InterM"; src: url("file://{fonts}/inter-medium.otf") format("opentype"); font-weight: 500; }}
html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #694330; }}
.bg {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; }}
.glow {{ position: absolute; inset: 0; background:
  radial-gradient(ellipse 470px 230px at 340px 1505px, rgba(250,246,241,.44), rgba(250,246,241,.23) 48%, rgba(250,246,241,0) 100%); }}
.t {{ position: absolute; left: 78px; top: 1345px; }}
.cap {{ display: block; font: 500 40px "InterM", sans-serif; letter-spacing: .42em; text-transform: uppercase; color: #694330;
  text-shadow: 0 0 18px rgba(250,246,241,.55), 0 0 40px rgba(250,246,241,.3); }}
.w {{ display: block; font: 400 222px/0.86 "Chorus", serif; color: #341D13; margin: 5px 0 0 4px; -webkit-text-stroke: 1px #341D13;
  text-shadow: 0 0 24px rgba(250,246,241,.55), 0 0 60px rgba(250,246,241,.35); }}
.tag {{ font-size: 37px; margin-top: -1px; }}
</style></head><body>
<img class="bg" src="file://{bg}"><div class="glow"></div>
<div class="t"><span class="cap">{esc(a.kicker)}</span><span class="w">{esc(a.word)}</span><span class="cap tag">{esc(a.tag)}</span></div>
</body></html>'''
page = os.path.join(tmp, "thumb.html"); open(page, "w").write(html)
png = os.path.join(tmp, "thumb.png")
js = f'''const {{ chromium }} = require('playwright');
(async () => {{ const b = await chromium.launch(); const p = await b.newPage({{ viewport: {{ width: 1080, height: 1920 }}, deviceScaleFactor: {W / 1080} }});
await p.goto('file://{page}'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
await p.screenshot({{ path: '{png}' }}); await b.close(); }})();'''
subprocess.run(["node", "-e", js], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "1", a.out], check=True)
print(f"thumbnail {W}x{H} -> {a.out}")
