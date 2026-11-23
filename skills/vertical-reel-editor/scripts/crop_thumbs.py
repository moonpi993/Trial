"""Extract the real 9:16 crop of every shot in reel.json as a 270x480 thumbnail.

usage: python3 crop_thumbs.py reel.json OUT_DIR [--style STYLE] [--sheet]
--style applies that style's grade so the storyboard shows the final look.
--sheet also writes OUT_DIR/_sheet.jpg (all shots tiled) for a quick look: check that no crop is
just fur/bedsheet/blur, and that neighbouring shots don't look the same.
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelspec import load_spec, load_style, media_size, crop_box

spec_path, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
args = sys.argv[3:]
grade = load_style(args[args.index("--style") + 1])["grade"] if "--style" in args else None
spec = load_spec(spec_path)
sizes = {}
for s in spec["shots"]:
    src = spec["sources"][s["src"]]
    sizes.setdefault(s["src"], media_size(src["path"]))
    w, h, x, y = crop_box(*sizes[s["src"]], s.get("zoom", 1.0), s.get("cx", 0.5), s.get("cy", 0.5))
    vf = f"crop={w}:{h}:{x}:{y},scale=270:480" + (f",{grade}" if grade else "")
    seek = [] if src["kind"] == "image" else ["-ss", str(s.get("in", 0))]
    subprocess.run(["ffmpeg", "-v", "error", "-y", *seek, "-i", src["path"], "-map", "0:v:0", "-frames:v", "1",
                    "-vf", vf, "-q:v", "3", f"{out}/{s['id']}.jpg"], check=True)
if "--sheet" in args:
    ids = [s["id"] for s in spec["shots"]]
    cols = min(9, len(ids))
    ins = sum((["-i", f"{out}/{i}.jpg"] for i in ids), [])
    rows = -(-len(ids) // cols)
    layout = "|".join(f"{(k % cols) * 270}_{(k // cols) * 480}" for k in range(len(ids)))
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex",
                    f"xstack=inputs={len(ids)}:layout={layout}:fill=black" if len(ids) > 1 else "null",
                    f"{out}/_sheet.jpg"], check=True)
print(f"{len(spec['shots'])} thumbnails in {out}")
