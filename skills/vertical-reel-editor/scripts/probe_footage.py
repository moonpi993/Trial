"""Inventory the user's footage: size, length, fps, audio level, and a contact sheet per clip.

usage: python3 probe_footage.py OUT_DIR clip1.mov clip2.mp4 photo.jpg ...
Writes OUT_DIR/<name>.jpg (one frame every 2s, 4 columns) and prints a summary table.
Duplicate uploads (same duration and size) are flagged so you can skip them.
"""
import json, os, subprocess, sys

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
seen = {}
print(f"{'file':52} {'size':>11} {'len':>6} {'fps':>5} {'audio max':>10}")
for f in sys.argv[2:]:
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", f],
        capture_output=True, text=True).stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), {})
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    dur = float(info.get("format", {}).get("duration", 0) or 0)
    name = os.path.splitext(os.path.basename(f))[0][:40]
    still = dur < 0.5 or f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".heic"))
    peak = "-"
    if has_audio and not still:
        r = subprocess.run(["ffmpeg", "-i", f, "-map", "0:a:0", "-af", "volumedetect", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        peak = next((l.split(":")[1].strip() for l in r.splitlines() if "max_volume" in l), "-")
    num, den = (v.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    fps = round(int(num) / max(int(den), 1), 2) if not still else "-"
    key = (round(dur, 2), v.get("width"), v.get("height"))
    dup = f"  (same as {seen[key]})" if key in seen and not still else ""
    seen.setdefault(key, name)
    print(f"{name:52} {str(v.get('width'))+'x'+str(v.get('height')):>11} {dur:6.1f} {str(fps):>5} {peak:>10}{dup}")
    if still:
        vf = "scale=480:-2"
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", f, "-frames:v", "1", "-vf", vf, f"{out}/{name}.jpg"]
    else:
        vf = f"fps=1/2,scale=480:-2,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=4x4"
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", f, "-map", "0:v:0", "-vf", vf, "-frames:v", "1", f"{out}/{name}.jpg"]
    subprocess.run(cmd, check=False)
print(f"\ncontact sheets in {out}  (timestamps are burned in; a mostly silent clip peaks below about -35 dB)")
