"""Synthesize the SFX in cues.json, place them, and mux onto the rendered video.

usage: python3 mix_sfx.py WORK_DIR/cues.json RENDERED.mp4 FINAL.mp4
Sounds (all generated with FFmpeg, so there is nothing to license):
  alarm   phone-alarm double beeps that get louder; give it "until" so it cuts off on a beat
  pop     short downward blip (title word landing, a twitch)
  tick    small high blip (counters, list items)
  whoosh  filtered noise swell (section changes, spins, speed ramps)
  chime   soft bell (reveal, 'aww' moment)
  boing   springy wobble (jump, fall, silly beat)
  thud    low soft hit (plop down, hard stop)
Music is not added: the user picks it in Instagram/TikTok, which handles licensing. Leave room for it.
"""
import json, os, subprocess, sys, tempfile

cues_path, video, final = sys.argv[1], sys.argv[2], sys.argv[3]
cues = json.load(open(cues_path)); total = cues["total"]
tmp = tempfile.mkdtemp()
SR = 48000
SYNTH = {
    "pop":    ("aevalsrc='0.9*sin(2*PI*(900*t-2600*t*t))*exp(-t*38)':s=48000:d=0.15", ""),
    "tick":   ("aevalsrc='0.7*sin(2*PI*(1300*t-3000*t*t))*exp(-t*45)':s=48000:d=0.12", ""),
    "chime":  ("aevalsrc='0.5*(sin(2*PI*1318*t)+0.6*sin(2*PI*1976*t)+0.3*sin(2*PI*2637*t))*exp(-t*3.2)':s=48000:d=1.4", ""),
    "boing":  ("aevalsrc='0.8*sin(2*PI*(220*t+40*sin(2*PI*9*t)/(2*PI*9)*(1-t)*8))*exp(-t*4)':s=48000:d=0.7", ""),
    "thud":   ("aevalsrc='0.9*sin(2*PI*(110*t-90*t*t))*exp(-t*16)':s=48000:d=0.3", ""),
    "whoosh": ("anoisesrc=color=pink:amplitude=0.9:d=0.6:r=48000",
               "bandpass=f=1800:width_type=o:w=1.6,afade=t=in:d=0.3:curve=qsin,afade=t=out:st=0.3:d=0.3:curve=qsin,volume=1.6"),
}

def make(sound, length=None):
    path = os.path.join(tmp, f"{sound}_{length}.wav")
    if os.path.exists(path):
        return path
    if sound == "alarm":
        d = length or 3.0
        src = (f"aevalsrc='(lt(mod(t,0.5),0.07)+between(mod(t,0.5),0.12,0.19))*(0.55*sin(2*PI*2600*t)+0.25*sin(2*PI*5200*t))"
               f"*(0.35+0.65*t/{d})':s=48000:d={d}")
        af = f"afade=t=out:st={max(d - 0.02, 0)}:d=0.02"
    else:
        src, af = SYNTH[sound]
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", src] + (["-af", af] if af else []) + ["-ac", "2", path]
    subprocess.run(cmd, check=True)
    return path

ins, fl = [], []
for i, c in enumerate(cues["cues"]):
    ins += ["-i", make(c["sound"], c.get("len") if c["sound"] == "alarm" else None)]
    d = max(int(c["at"] * 1000), 0)
    cut = f"atrim=0:{c['len']}," if c.get("len") and c["sound"] != "alarm" else ""
    fl.append(f"[{i}:a]{cut}volume={c.get('vol', 0.7)},adelay={d}|{d}[a{i}]")
n = len(cues["cues"])
mix_in = "".join(f"[a{i}]" for i in range(n))
if n == 0:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-c", "copy", "-movflags", "+faststart", final], check=True)
    sys.exit(0)
fl.append(f"{mix_in}amix=inputs={n}:normalize=0,apad,atrim=0:{total},alimiter=limit=0.89[out]")
wav = os.path.join(tmp, "sfx_mix.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fl), "-map", "[out]", "-ar", str(SR), wav], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
print(f"{final}  ({len(cues['cues'])} sfx cues)")
