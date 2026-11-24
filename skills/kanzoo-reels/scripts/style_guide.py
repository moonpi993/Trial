"""Build Kanzoo's visual style menu: the locked video look, the thumbnail look, palette, fonts and rules.

usage: python3 style_guide.py OUT.html [--frames DIR]   (default frames: assets/reference)
Publish OUT.html as an artifact when the user asks to see the style, or when starting a new Kanzoo post
so they can confirm the look before anything renders.
"""
import base64, glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "..", "assets")
out = sys.argv[1]
fdir = sys.argv[sys.argv.index("--frames") + 1] if "--frames" in sys.argv else os.path.join(A, "reference")
b64 = lambda p, m: f"data:{m};base64," + base64.b64encode(open(p, "rb").read()).decode()
font = lambda f, m: b64(os.path.join(A, "fonts", f), m)
data = json.load(open(os.path.join(A, "styles.json")))
sw = data["styles"]["kanzoo-video"]["palette"]["swatches"]
hl = data["highlight_options"]
thumb = b64(os.path.join(fdir, "official-thumbnail.jpg"), "image/jpeg")
labels = {"2.6": "Hook title", "4.6": "Step 1 + beep", "6.4": "Surprise beep", "8.4": "Step 2", "12.3": "Punchline", "14.6": "Ending"}
frames = sorted(glob.glob(os.path.join(fdir, "video-*.jpg")), key=lambda p: float(os.path.basename(p)[6:-4]))
strip = "".join(f'<figure><img src="{b64(p, "image/jpeg")}" alt="" width="540" height="960"><figcaption>{labels.get(os.path.basename(p)[6:-4], "")}</figcaption></figure>' for p in frames)
swatches = "".join(f'<div class="sw" style="background:{h};color:{"#341D13" if i < 3 else "#FAF6F1"}"><b>{n}</b><span>{h}</span></div>' for i, (n, h) in enumerate(sw.items()))
hls = "".join(f'<span class="hc"><i style="background:{h}"></i>{n}</span>' for n, h in hl.items())

page = f'''<title>Kanzoo Style Menu</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
@font-face {{ font-family: "Pagella"; src: url({font("texgyrepagella-italic.otf", "font/otf")}) format("opentype"); font-style: italic; }}
@font-face {{ font-family: "Chorus"; src: url({font("texgyrechorus-mediumitalic.otf", "font/otf")}) format("opentype"); }}
@font-face {{ font-family: "InterK"; src: url({font("inter-latin-400-normal.woff2", "font/woff2")}) format("woff2"); font-weight: 400; }}
@font-face {{ font-family: "InterK"; src: url({font("inter-medium.otf", "font/otf")}) format("opentype"); font-weight: 500; }}
/* Layout: hero (thumbnail + intro), video strip, palette, fonts, rules. Cream page, espresso ink. */
:root {{ --bg: #FAF6F1; --panel: #F1E7DD; --ink: #341D13; --muted: #694330; --line: #E3CEC0; --car: #A56D4E; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg: #241509; --panel: #341D13; --ink: #FAF6F1; --muted: #C69A77; --line: #4A2F20; --car: #C69A77; color-scheme: dark }} }}
:root[data-theme="dark"] {{ --bg: #241509; --panel: #341D13; --ink: #FAF6F1; --muted: #C69A77; --line: #4A2F20; --car: #C69A77; color-scheme: dark }}
body {{ background: var(--bg); color: var(--ink); font: 400 15px/1.6 InterK, system-ui, sans-serif; }}
.wrap {{ max-width: 1080px; margin: 0 auto; padding-block: 44px 80px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: grid; gap: 60px; }}
.kick {{ font: 500 11px InterK, sans-serif; letter-spacing: .32em; text-transform: uppercase; color: var(--muted); margin: 0 0 12px; }}
h1 {{ font: 400 clamp(3.4rem, 10vw, 6rem)/.9 Chorus, serif; margin: 0; }}
h2 {{ font: italic 400 2rem/1.1 Pagella, serif; margin: 0 0 8px; text-wrap: balance; }}
p {{ margin: 0; max-width: 62ch; }} .lede {{ color: var(--muted); margin-top: 12px; }}
.hero {{ display: grid; grid-template-columns: 300px minmax(0, 1fr); gap: 36px; align-items: center; }}
.hero img {{ width: 100%; max-width: 300px; height: auto; aspect-ratio: 9/16; object-fit: cover; border-radius: 10px; display: block; }}
.strip {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; margin-top: 18px; }}
figure {{ margin: 0; }} figure img {{ width: 100%; height: auto; aspect-ratio: 9/16; object-fit: cover; border-radius: 6px; display: block; }}
figcaption {{ font: 500 10.5px InterK, sans-serif; letter-spacing: .2em; text-transform: uppercase; color: var(--muted); margin-top: 8px; }}
.pal {{ display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; margin-top: 18px; }}
.sw {{ border-radius: 999px 999px 8px 8px; min-height: 200px; padding: 14px 10px; display: grid; align-content: end; gap: 2px; box-shadow: inset 0 0 0 1px rgba(52,29,19,.12); }}
.sw b {{ font: italic 400 1.2rem Pagella, serif; }} .sw span {{ font: 500 11px InterK, sans-serif; letter-spacing: .06em; }}
.fonts {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin-top: 18px; }}
.fc {{ background: var(--panel); border-radius: 8px; padding: 22px; display: grid; gap: 8px; align-content: start; }}
.fc .tagline {{ font: 500 11px InterK, sans-serif; letter-spacing: .22em; text-transform: uppercase; color: var(--muted); }}
.f-pag {{ font: italic 400 3rem/1 Pagella, serif; }} .f-cho {{ font: 400 3.4rem/1 Chorus, serif; }}
.f-cap {{ font-family: InterK, sans-serif; text-transform: uppercase; letter-spacing: .4em; font-size: 14px; color: var(--muted); }}
.fc p {{ font-size: 13.5px; color: var(--muted); }}
.hcs {{ display: flex; flex-wrap: wrap; gap: 8px 16px; margin-top: 14px; }} .hc {{ font-size: 13.5px; }} .hc i {{ display: inline-block; width: 13px; height: 13px; border-radius: 50%; vertical-align: -2px; margin-right: 6px; }}
ol {{ margin: 16px 0 0; padding: 0; list-style: none; display: grid; counter-reset: r; }}
ol li {{ counter-increment: r; display: grid; grid-template-columns: 44px minmax(0, 1fr); gap: 10px; padding: 14px 0; border-top: 1px solid var(--line); }}
ol li::before {{ content: counter(r, decimal-leading-zero); font: italic 400 1.2rem Pagella, serif; color: var(--car); }}
@media (max-width: 700px) {{ .hero, .fonts {{ grid-template-columns: minmax(0, 1fr); }} .strip, .pal {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }} }}
</style>
<div class="wrap">
  <section class="hero">
    <img src="{thumb}" alt="Official Kanzoo Monday thumbnail" width="1080" height="1920">
    <div><p class="kick">Visual style menu</p><h1>Kanzoo</h1>
      <p class="lede">The locked look for every Kanzoo post. Videos and covers share this thumbnail's fonts, colours and glow. Soft natural coffee light, dark coffee text placed in the empty space beside him, never white, no bars, no dark fades.</p></div>
  </section>

  <section><p class="kick">Video look</p><h2>From the Monday Reel</h2>
    <p class="lede">Chorus lines in espresso and wide-spaced Inter Medium capitals in mocha, each with a soft cream glow, exactly like the thumbnail. The hook title sits lower-left; steps sit mid-frame; beeps pop up in a different spot each time; "That's it." snaps in.</p>
    <div class="strip">{strip}</div></section>

  <section><p class="kick">Palette</p><h2>Coffee tones</h2>
    <div class="pal">{swatches}</div>
    <p class="lede" style="margin-top:14px">Text: espresso. Small capitals: mocha. Backgrounds and paper: cream.</p></section>

  <section><p class="kick">Fonts</p><h2>One type system everywhere</h2>
    <div class="fonts">
      <div class="fc"><span class="tagline">Words and lines</span><span class="f-cho">Monday</span><p>TeX Gyre Chorus, espresso #341D13, with a soft cream glow. Used for the cover word and every line in the video.</p></div>
      <div class="fc"><span class="tagline">Small capitals</span><span class="f-cap" style="font-weight:500;font-size:16px">How to survive a · Kanzoo edition</span><p>Inter Medium, mocha #694330, wide letter spacing, the same glow. Used for kickers, step numbers and tags.</p></div>
    </div></section>

  <section><p class="kick">Optional</p><h2>Highlight colours</h2>
    <p class="lede">Off by default (the Monday Reel uses none). When a word should pop, wrap it in *asterisks* in the plan and pick one of these.</p>
    <div class="hcs">{hls}</div></section>

  <section><p class="kick">Rules</p><h2>Keep doing</h2>
    <ol>
      <li><span><b>Same grade on everything.</b> Soft natural coffee light: not bright, not dark, never pale.</span></li>
      <li><span><b>No white text.</b> Espresso and mocha only, with the soft cream glow behind the words.</span></li>
      <li><span><b>Text sits on the picture.</b> No bars, boxes or dark fades behind it. Place it in the calm space beside his face.</span></li>
      <li><span><b>Keep his face clear.</b> No caption or pop-up on his eyes, nose or mouth.</span></li>
      <li><span><b>Shoot light.</b> White sheets, daylight, window light make this look shine.</span></li>
      <li><span><b>Deliver 4K with a ZIP copy.</b> The ZIP keeps full quality when downloading on a phone.</span></li>
    </ol></section>
</div>
'''
open(out, "w").write(page)
print(f"style menu -> {out} ({len(page)//1024} KB)")
