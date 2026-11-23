"""Break a reference reel down into measurable editing techniques.

usage: python3 analyze_reference.py reference.mp4 OUT_DIR
Writes:
  OUT_DIR/sheet_*.jpg     1 frame per second, timestamped, 9 per row (read these to see shots, text, framing)
  OUT_DIR/title.jpg       a full-size frame from the first seconds (read it to copy the title's type system)
  OUT_DIR/wave.png        audio waveform (spiky = foley/ASMR hits, flat dense = music bed, gaps = silence)
  OUT_DIR/analysis.json   cut times, shot lengths, pace by third, loudness
Then describe the techniques in your own words: title treatment, hook/payoff order, what each cut lands on,
rhythm changes, transitions, sound design, grade. Adapt them; never copy the reference's story, text or look 1:1.
"""
import json, os, statistics, subprocess, sys

ref, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ref],
                           capture_output=True, text=True).stdout.strip())

# scene cuts (scdet works on gradual cuts too; threshold 5 suits phone footage)
meta = subprocess.run(["ffmpeg", "-i", ref, "-vf", "scdet=threshold=5,metadata=print:file=-", "-an", "-f", "null", "-"],
                      capture_output=True, text=True).stdout
cuts = []
for line in meta.splitlines():
    if "lavfi.scd.time=" in line:
        t = float(line.split("=")[1])
        if not cuts or t - cuts[-1] > 0.15:   # merge flash-frames / dissolves
            cuts.append(round(t, 2))
bounds = [0.0] + cuts + [dur]
shots = [round(b - a, 2) for a, b in zip(bounds, bounds[1:]) if b - a > 0.05]

def pace(a, b):
    s = [round(y - x, 2) for x, y in zip(bounds, bounds[1:]) if a <= x < b]
    return round(statistics.mean(s), 2) if s else None

thirds = [round(dur * i / 3, 2) for i in range(4)]
loud = subprocess.run(["ffmpeg", "-i", ref, "-af", "volumedetect", "-vn", "-f", "null", "-"],
                      capture_output=True, text=True).stderr
vol = {k: l.split(":")[1].strip() for l in loud.splitlines() for k in ("mean_volume", "max_volume") if k in l}

# contact sheets: 18 frames per sheet
per = 18
for i in range(0, int(dur) + 1, per):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(i), "-i", ref, "-frames:v", "1", "-vf",
        f"fps=1,scale=240:-2,setpts=PTS+{i}/TB,drawtext=text='%{{pts\\:hms}}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black,tile=9x2",
        f"{out}/sheet_{i:03d}.jpg"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(min(2.5, dur / 3)), "-i", ref, "-frames:v", "1", f"{out}/title.jpg"])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ref, "-filter_complex", "showwavespic=s=1600x200", "-frames:v", "1", f"{out}/wave.png"])

res = {"duration": round(dur, 2), "cuts": cuts, "shot_count": len(shots),
       "avg_shot": round(statistics.mean(shots), 2) if shots else None,
       "shortest": min(shots) if shots else None, "longest": max(shots) if shots else None,
       "avg_shot_by_third": {"first": pace(thirds[0], thirds[1]), "middle": pace(thirds[1], thirds[2]), "last": pace(thirds[2], thirds[3])},
       "loudness": vol}
json.dump(res, open(f"{out}/analysis.json", "w"), indent=1)
print(json.dumps(res, indent=1))
