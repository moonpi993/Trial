"""Shared helpers: load reel.json + styles.json, frame-accurate timeline, and time references.

Time references (used by pops and sfx in reel.json):
  3.2            absolute seconds
  "04"           start of shot 04          "04+0.1" / "04-0.2"  offset from that start
  "04.end"       end of shot 04            "04.end-0.15"
  "end"          end of the film           "end-0.6"
"""
import json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
STYLES_PATH = os.path.join(HERE, "..", "assets", "styles.json")


def load_spec(path):
    spec = json.load(open(path))
    spec.setdefault("fps", 25)
    base = os.path.dirname(os.path.abspath(path))
    for k, v in spec["sources"].items():
        if isinstance(v, str):
            v = {"path": v}
        if not os.path.isabs(v["path"]):
            v["path"] = os.path.join(base, v["path"])
        v.setdefault("kind", "image" if v["path"].lower().endswith((".jpg", ".jpeg", ".png", ".heic", ".webp")) else "video")
        spec["sources"][k] = v
    return spec


def load_style(name):
    styles = json.load(open(STYLES_PATH))["styles"]
    if name not in styles:
        raise SystemExit(f"unknown style '{name}'. Options: {', '.join(styles)}")
    return styles[name]


def media_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    w, h = out.strip().splitlines()[0].split(",")[:2]
    return int(w), int(h)


def timeline(spec):
    """Shot starts snapped to whole frames, so captions, SFX and cuts agree exactly."""
    fps, t, rows = spec["fps"], 0, []
    for s in spec["shots"]:
        n = max(1, round(s["dur"] * fps))
        rows.append({**s, "frames": n, "start": round(t / fps, 3), "end": round((t + n) / fps, 3)})
        t += n
    return rows, round(t / fps, 3)


_REF = re.compile(r"^(?P<id>[A-Za-z0-9_]+?)(?P<end>\.end)?(?P<off>[+-]\d*\.?\d+)?$")


def resolve(ref, rows, total):
    if isinstance(ref, (int, float)):
        return float(ref)
    m = _REF.match(str(ref).strip())
    if not m:
        raise ValueError(f"bad time reference {ref!r}")
    off = float(m["off"] or 0)
    if m["id"] == "end" and not m["end"]:
        return round(total + off, 3)
    for r in rows:
        if r["id"] == m["id"]:
            return round((r["end"] if m["end"] else r["start"]) + off, 3)
    raise ValueError(f"time reference {ref!r}: no shot {m['id']}")


def sections(spec, rows, total):
    """Section windows in film order: {id: (start, end)}."""
    order, win = [], {}
    for r in rows:
        if r["section"] not in win:
            order.append(r["section"]); win[r["section"]] = [r["start"], r["end"]]
        win[r["section"]][1] = r["end"]
    return order, {k: tuple(v) for k, v in win.items()}


def crop_box(src_w, src_h, zoom, cx, cy, aspect=9 / 16):
    """9:16 window inside the source frame. zoom 1 = full source height."""
    h = src_h / zoom
    w = h * aspect
    if w > src_w:
        w = src_w; h = w / aspect
    x = min(max(cx * src_w - w / 2, 0), src_w - w)
    y = min(max(cy * src_h - h / 2, 0), src_h - h)
    return int(w) // 2 * 2, int(h) // 2 * 2, int(x), int(y)


def local_font_css(font, family):
    """@font-face with an embedded data URI for fonts bundled in assets/fonts (used by the HTML previews)."""
    if not font.get("local"):
        return ""
    import base64
    path = os.path.join(HERE, "..", "assets", "fonts", font["file"])
    ext = font["file"].rsplit(".", 1)[-1]
    mime, fmt = {"otf": ("font/otf", "opentype"), "ttf": ("font/ttf", "truetype"), "woff": ("font/woff", "woff")}.get(ext, ("font/woff2", "woff2"))
    data = base64.b64encode(open(path, "rb").read()).decode()
    return (f'@font-face {{ font-family: "{family}"; src: url(data:{mime};base64,{data}) format("{fmt}"); '
            f'font-weight: {font.get("weight", 400)}; font-style: {font.get("style", "normal")}; }}')
