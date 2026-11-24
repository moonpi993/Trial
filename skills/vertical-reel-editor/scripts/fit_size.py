#!/usr/bin/env python3
"""Make a copy of a video that fits under a size limit (default 30 MB, the Claude upload limit).

    python3 -I fit_size.py FINAL.mp4 FINAL_30mb.mp4 [--max-mb 30] [--width 1080]

Picks the video bitrate from the duration and encodes two-pass H.264, so the file lands just under the limit
at the best quality that fits. 4K input is scaled to --width (1080 by default, which is what Instagram shows).
Audio is re-encoded to AAC 160k. If the file is already small enough it is copied as is.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile

p = argparse.ArgumentParser()
p.add_argument("src"); p.add_argument("out")
p.add_argument("--max-mb", type=float, default=30.0)
p.add_argument("--width", type=int, default=1080, help="output width; 0 keeps the source size")
a = p.parse_args()

limit = a.max_mb * 1000 * 1000 * 0.97          # MB as most upload forms count it, with a 3% margin for the container
if os.path.getsize(a.src) <= limit:
    shutil.copyfile(a.src, a.out); print(f"already under {a.max_mb:g} MB, copied"); sys.exit(0)

info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width",
                                  "-of", "json", a.src], capture_output=True, text=True, check=True).stdout)
dur = float(info["format"]["duration"])
has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
src_w = next(s["width"] for s in info["streams"] if s["codec_type"] == "video")
audio_k = 160 if has_audio else 0
video_k = int(limit * 8 / 1000 / dur) - audio_k
if video_k < 1500:
    sys.exit(f"{dur:.1f}s cannot fit under {a.max_mb:g} MB at a watchable bitrate ({video_k}k); trim the video or raise --max-mb")

vf = ["-vf", f"scale={a.width}:-2:flags=lanczos"] if a.width and src_w > a.width else []
aud = ["-c:a", "aac", "-b:a", f"{audio_k}k"] if has_audio else ["-an"]
with tempfile.TemporaryDirectory() as t:
    log = os.path.join(t, "pass")
    base = ["ffmpeg", "-v", "error", "-y", "-i", a.src, *vf, "-c:v", "libx264", "-preset", "slow",
            "-b:v", f"{video_k}k", "-pix_fmt", "yuv420p", "-passlogfile", log]
    subprocess.run([*base, "-pass", "1", "-an", "-f", "mp4", os.devnull], check=True)
    subprocess.run([*base, "-pass", "2", *aud, "-movflags", "+faststart", a.out], check=True)

mb = os.path.getsize(a.out) / 1e6
print(f"{a.out}: {mb:.1f} MB, video {video_k}k, {dur:.1f}s")
if mb > a.max_mb:
    sys.exit(f"still {mb:.1f} MB; rerun with --max-mb {a.max_mb - 2:g}")
