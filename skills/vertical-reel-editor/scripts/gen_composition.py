"""Write the HyperFrames text layer for a rendered base video, plus the SFX cue list.

usage: python3 gen_composition.py reel.json WORK_DIR PROJECT_DIR
Reads WORK_DIR/timeline.json (from render_shots.py) and the style named in it.
Creates/updates PROJECT_DIR (a HyperFrames project): index.html, assets/base.mp4, assets/fonts/*, assets/gsap.min.js,
and writes WORK_DIR/cues.json for mix_sfx.py.

Text system (all laid out on a 1080x1920 stage, scaled up for 4K so type stays vector-sharp):
  title_card  {kicker, word, tag}  over the first section; one line lands on each of its first three shots
  sections    {id, label, line}    a step caption for the whole section (label = bold font, line = accent font)
              {id, lines: [...]}   ending lines, one after another across the section's shots
  pops        {text, at, until, x, y, size, rot}  short accent-font pop-ups (beeps, counters, "x2")
Captions sit at y 1000-1450 and x 130-950, inside the Instagram/TikTok/Shorts safe areas.
"""
import glob, json, os, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelspec import load_spec, load_style, resolve, sections

spec_path, work, proj = sys.argv[1], sys.argv[2], sys.argv[3]
spec = load_spec(spec_path)
tl = json.load(open(os.path.join(work, "timeline.json")))
style = load_style(tl["style"])
rows, total, (W, H) = tl["shots"], tl["total"], tl["size"]
S = W / 1080
r3 = lambda x: round(x, 3)
order, win = sections(spec, rows, total)
sec_spec = {s["id"]: s for s in spec.get("sections", [])}
shots_in = lambda sid: [r for r in rows if r["section"] == sid]

# ---- project scaffold, fonts, gsap (npm works where CDNs and Google Fonts may be blocked) ----
if not os.path.exists(os.path.join(proj, "hyperframes.json")):
    parent, name = os.path.split(os.path.abspath(proj))
    os.makedirs(parent, exist_ok=True)
    subprocess.run(["npx", "-y", "hyperframes", "init", name, "--example", "blank", "--non-interactive", "--skip-skills"],
                   cwd=parent, check=True, env={**os.environ, "HYPERFRAMES_SKIP_SKILLS": "1"}, stdout=subprocess.DEVNULL)
os.makedirs(os.path.join(proj, "assets", "fonts"), exist_ok=True)

def npm_file(pkg, rel, dest):
    if os.path.exists(dest):
        return
    tmp = tempfile.mkdtemp()
    subprocess.run(["npm", "pack", pkg, "--silent"], cwd=tmp, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["tar", "xzf", glob.glob(os.path.join(tmp, "*.tgz"))[0], "-C", tmp], check=True)
    shutil.copy(os.path.join(tmp, "package", rel), dest)

for role in ("bold", "accent"):
    f = style["fonts"][role]
    dest = os.path.join(proj, "assets", "fonts", f["file"])
    if f.get("local"):   # font file bundled in the skill's assets/fonts (fonts not on npm, e.g. TeX Gyre Pagella)
        shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", f["file"]), dest)
    else:
        npm_file(f"@fontsource/{f['pkg']}", f"files/{f['file']}", dest)
npm_file("gsap@3.15.0", "dist/gsap.min.js", os.path.join(proj, "assets", "gsap.min.js"))
shutil.copy(os.path.join(work, "base_graded.mp4"), os.path.join(proj, "assets", "base.mp4"))

# ---- elements + timeline ----
els, js = [], []
def clip(id_, cls, start, dur, inner, track=2, style_attr=""):
    els.append(f'<div id="{id_}" class="{cls} clip" data-start="{r3(start)}" data-duration="{r3(dur)}" data-track-index="{track}"{style_attr}>{inner}</div>')

first, after_first = order[0], [o for o in order[1:]]
if style.get("scrim"):
    a = win[first][1]
    clip("topscrim", "full topscrim", 0, a, "", 1)
    clip("scrim", "full scrim", a, total - a, "", 1)

tc = spec.get("title_card")
if tc:
    a, b = win[first]
    hook = shots_in(first)
    at = [hook[min(i, len(hook) - 1)]["start"] + (0.12 if i == 0 else 0) for i in range(3)]
    clip("title", "title", 0, b, (f'<span id="t1" class="sz kick"><span class="label">{tc.get("kicker","")}</span></span>'
                                  f'<span id="t2" class="line">{tc.get("word","")}</span>'
                                  f'<span id="t3" class="sz tagw"><span class="label tag">{tc.get("tag","")}</span></span>'))
    js += [f'tl.fromTo("#t1", soft, {{ ...on }}, {r3(at[0])});',
           f'tl.fromTo("#t2", {{ opacity: 0, scale: 0.8, filter: "blur(10px)" }}, {{ opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.38, ease: "back.out(1.8)" }}, {r3(at[1])});',
           f'tl.fromTo("#t3", soft, {{ ...on }}, {r3(at[2])});',
           f'tl.to(["#title", "#topscrim"], {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, {r3(b - 0.24)});']

for sid in order:
    s = sec_spec.get(sid, {})
    a, b = win[sid]
    if s.get("label") or s.get("line"):
        k = f"sec_{sid}"
        clip(k, "step", a, b - a, f'<span class="sz lab"><span class="label">{s.get("label","")}</span></span><span class="line">{s.get("line","")}</span>')
        js += [f'tl.fromTo("#{k} .lab", soft, {{ ...on }}, {r3(a + 0.04)});',
               f'tl.fromTo("#{k} .line", {{ opacity: 0, x: -30, rotation: -3 }}, {{ opacity: 1, x: 0, rotation: 0, duration: 0.38, ease: "back.out(1.6)" }}, {r3(a + 0.14)});',
               f'tl.to("#{k}", {{ opacity: 0, duration: 0.14 }}, {r3(b - 0.15)});']
    if s.get("lines"):
        sh = shots_in(sid); n = len(s["lines"])
        starts = [sh[min(i * len(sh) // n, len(sh) - 1)]["start"] for i in range(n)]
        for i, item in enumerate(s["lines"]):
            # a line is "text" or {"text": ..., "punch": true}; punch = lands on the cut and snaps in (punchlines)
            text, punch = (item, False) if isinstance(item, str) else (item["text"], item.get("punch", False))
            st = starts[i] + (0.0 if punch else (0.2 if i == 0 else -0.12))
            en = (starts[i + 1] - 0.02) if i + 1 < n else total
            k = f"end_{sid}_{i}"
            size = 150 if len(text) <= 12 else 116
            clip(k, "end", st, en - st, f'<span class="line" style="font-size:{round(size * style.get("line_scale", 1))}px">{text}</span>')
            if punch:
                js.append(f'tl.fromTo("#{k} .line", {{ opacity: 0, scale: 1.5 }}, {{ opacity: 1, scale: 1, duration: 0.14, ease: "back.out(2.6)" }}, {r3(st)});')
            else:
                js.append(f'tl.fromTo("#{k} .line", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }}, {r3(st + 0.02)});')
            if i + 1 < n:
                js.append(f'tl.to("#{k}", {{ opacity: 0, duration: 0.12 }}, {r3(en - 0.13)});')

for i, p in enumerate(spec.get("pops", [])):
    st = resolve(p["at"], rows, total); en = resolve(p.get("until", st + 0.6), rows, total)
    rot = p.get("rot", (-6 if i % 2 else 6))
    pos = f'left:{p.get("x", 150)}px; top:{p.get("y", 400)}px; font-size:{p.get("size", 96)}px;'
    clip(f"pop{i}", "pop", st, en - st + 0.05, f'<span class="line" style="{pos}">{p["text"]}</span>', 3)
    js += [f'tl.fromTo("#pop{i} .line", {{ opacity: 0, scale: 0.4, rotation: {rot * 1.6 if abs(rot) < 20 else rot + 12} }}, {{ opacity: 1, scale: 1, rotation: {rot}, duration: 0.18, ease: "back.out(3)" }}, {r3(st)});',
           f'tl.to("#pop{i} .line", {{ opacity: 0, duration: 0.06 }}, {r3(en - 0.06)});']

clip("fadeout", "full fadeout", total - 0.6, 0.6, "", 4)
js.append(f'tl.to("#fadeout", {{ opacity: 1, duration: 0.55, ease: "power1.in" }}, {r3(total - 0.58)});')

fb, fa = style["fonts"]["bold"], style["fonts"]["accent"]
fmt = lambda f: {"otf": "opentype", "ttf": "truetype", "woff": "woff"}.get(f["file"].rsplit(".", 1)[-1], "woff2")
ls = style.get("line_scale", 1)
html = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "ReelBold"; src: url("assets/fonts/{fb['file']}") format("{fmt(fb)}"); font-weight: {fb['weight']}; }}
      @font-face {{ font-family: "ReelAccent"; src: url("assets/fonts/{fa['file']}") format("{fmt(fa)}"); font-weight: {fa['weight']}; font-style: {fa.get('style', 'normal')}; }}
      :root {{ --light: {style['palette']['light']}; --dark: {style['palette']['dark']}; --accent-c: {style['palette']['accent']};
              --bold: "ReelBold", sans-serif; --accent: "ReelAccent", cursive; }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: var(--dark); }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; }}
      #footage {{ position: absolute; inset: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      #stage {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform: scale({S}); transform-origin: 0 0; }}
      .full {{ position: absolute; inset: 0; width: 1080px; height: 1920px; }}
      .sz {{ display: block; }} .kick {{ font-size: 73px; }} .tagw {{ font-size: 52px; margin-top: 50px; }} .lab {{ font-size: 50px; }}
      .label {{ display: inline-block; font-size: 1em; {style['label_css']} }}
      .tag {{ letter-spacing: .16em; }}
      .line {{ {style['line_css']} }}
      .scrim {{ background: linear-gradient(to bottom, transparent 55%, {style.get('scrim') or 'transparent'} 70%, {style.get('scrim') or 'transparent'} 76%, transparent 92%); }}
      .topscrim {{ background: linear-gradient(to bottom, transparent 8%, {style.get('scrim') or 'transparent'} 24%, {style.get('scrim') or 'transparent'} 36%, transparent 50%); }}
      .title {{ position: absolute; left: 60px; right: 60px; top: 300px; text-align: center; }}
      .title .line {{ display: block; font-size: {round(250 * ls)}px; line-height: .82; margin-top: 10px; }}
      .step {{ position: absolute; left: 130px; right: 130px; top: 1000px; }}
      .step .line {{ display: block; font-size: {round(132 * ls)}px; line-height: .92; margin-top: 10px; }}
      .end {{ position: absolute; left: 130px; right: 130px; top: 1000px; text-align: center; }}
      .end .line {{ line-height: .95; display: block; }}
      .pop .line {{ position: absolute; white-space: nowrap; }}
      .fadeout {{ background: {style.get('fade_to', '#000')}; opacity: 0; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{W}" data-height="{H}" data-fps="{tl['fps']}">
      <video id="footage" class="clip" src="assets/base.mp4" muted playsinline data-start="0" data-duration="{total}" data-track-index="0"></video>
      <div id="stage">
        {chr(10).join("        " + e for e in els).strip()}
      </div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const soft = {{ opacity: 0, y: 24, filter: "blur(6px)" }};
      const on = {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.35, ease: "power3.out" }};
      {chr(10).join("      " + j for j in js).strip()}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
'''
open(os.path.join(proj, "index.html"), "w").write(html)

cues = {"total": total, "cues": []}
for c in spec.get("sfx", []):
    at = resolve(c["at"], rows, total)
    cue = {"sound": c["sound"], "at": at, "vol": c.get("vol", 0.7)}
    if "until" in c:
        cue["len"] = r3(resolve(c["until"], rows, total) - at)
    cues["cues"].append(cue)
json.dump(cues, open(os.path.join(work, "cues.json"), "w"), indent=1)
print(f"wrote {proj}/index.html ({len(els)} timed elements) and {work}/cues.json ({len(cues['cues'])} cues)")
