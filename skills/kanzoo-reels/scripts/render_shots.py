"""Cut every shot of reel.json into a vertical segment, join them, and apply the style's grade once.

usage: python3 render_shots.py reel.json WORK_DIR [--size 1080x1920|2160x3840] [--style NAME]
Per-shot fields: src, in (seconds into the source), dur, zoom (1 = full source height; 2 = 2x punch-in),
cx/cy (0-1 crop centre), speed (2 = double speed), push (0.06 = slow 6% zoom-in over the shot),
roll (true = 180-degree eased rotation, the 'flip over' move).
Segments are cached by their settings, so re-timing or dropping shots only re-renders what changed.
Writes WORK_DIR/base_graded.mp4 (silent) and WORK_DIR/timeline.json.
"""
import hashlib, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reelspec import load_spec, load_style, media_size, crop_box, timeline

spec_path, work = sys.argv[1], os.path.abspath(sys.argv[2])
args = sys.argv[3:]
OW, OH = map(int, (args[args.index("--size") + 1] if "--size" in args else "1080x1920").split("x"))
spec = load_spec(spec_path)
style_name = args[args.index("--style") + 1] if "--style" in args else spec["style"]
grade = load_style(style_name)["grade"]
fps = spec["fps"]
rows, total = timeline(spec)
seg_dir = os.path.join(work, "seg"); os.makedirs(seg_dir, exist_ok=True)
sizes = {}

for r in rows:
    src = spec["sources"][r["src"]]
    sizes.setdefault(r["src"], media_size(src["path"]))
    SW, SH = sizes[r["src"]]
    n, speed = r["frames"], float(r.get("speed", 1))
    if r.get("roll"):
        side = min(SW, SH)                      # square window so the rotation never shows corners
        x = int(min(max(r.get("cx", .5) * SW - side / 2, 0), SW - side))
        y = int(min(max(r.get("cy", .5) * SH - side / 2, 0), SH - side))
        diag = int((OW ** 2 + OH ** 2) ** 0.5) // 2 * 2 + 8
        u = "min(t/0.6\\,1)"
        vf = (f"crop={side}:{side}:{x}:{y},scale={diag}:{diag}:flags=lanczos,setpts=PTS/{speed},fps={fps},"
              f"rotate=a='PI*{u}*{u}*(3-2*{u})':ow={OW}:oh={OH}:c=black")
    else:
        w, h, x, y = crop_box(SW, SH, r.get("zoom", 1.0), r.get("cx", .5), r.get("cy", .5))
        p = float(r.get("push", 0))
        ow2, oh2 = int(OW * 1.2) // 2 * 2, int(OH * 1.2) // 2 * 2   # oversample so the push-in stays sharp
        vf = (f"crop={w}:{h}:{x}:{y},scale={ow2}:{oh2}:flags=lanczos,setpts=PTS/{speed},fps={fps},"
              f"zoompan=z='1+{p}*on/{max(n - 1, 1)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={OW}x{OH}:fps={fps}")
    vf += ",setsar=1,format=yuv420p"
    key = hashlib.md5(json.dumps([src["path"], r.get("in", 0), n, vf]).encode()).hexdigest()[:10]
    r["segment"] = os.path.join(seg_dir, f"{r['id']}_{key}.mp4")
    if os.path.exists(r["segment"]):
        print(r["id"], "cached"); continue
    inp = (["-loop", "1", "-framerate", str(fps), "-i", src["path"]] if src["kind"] == "image"
           else ["-ss", str(r.get("in", 0)), "-i", src["path"]])
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-map", "0:v:0", "-vf", vf, "-frames:v", str(n), "-an",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "14", r["segment"]], check=True)
    print(r["id"], n, "frames", flush=True)

with open(os.path.join(work, "list.txt"), "w") as f:
    for r in rows:
        f.write(f"file '{r['segment']}'\n")
json.dump({"fps": fps, "size": [OW, OH], "total": total, "style": style_name, "shots": rows},
          open(os.path.join(work, "timeline.json"), "w"), indent=1)
crf = "16" if OW > 1080 else "15"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(work, "list.txt"),
                "-vf", grade + ",format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", crf,
                "-g", str(fps), "-r", str(fps), os.path.join(work, "base_graded.mp4")], check=True)
print(f"base_graded.mp4  {OW}x{OH}  {total}s  style={style_name}")
