---
name: kanzoo-reels
description: Kanzoo's locked brand look for Instagram. Reels and covers/thumbnails share one type system copied from the user's official Monday thumbnail: TeX Gyre Chorus in espresso plus wide-spaced Inter Medium capitals in mocha, each with a soft cream glow, on soft natural coffee light. No white, no bars, no dark fades. Includes the visual style menu. Use this whenever the user mentions Kanzoo, their kitten, the cat account, a new Kanzoo Reel/post/cover/thumbnail, "my style", "same look as Monday", or uploads new kitten clips to edit, even if they don't name the skill.
compatibility: Needs ffmpeg/ffprobe, Node with npx (HyperFrames runs as `npx hyperframes`), Python 3 and Playwright's Chromium. All fonts are bundled in assets/fonts.
---

# Kanzoo Reels

This skill locks in two looks the user approved after many rounds. Reproduce them; don't redesign them.

| Output | The reference | What it looks like |
|---|---|---|
| **Video** | `kanzoo-monday-reel-4k-final.mp4` (frames in `assets/reference/video-*.jpg`) | Style `kanzoo-video`: soft natural coffee grade; lines in TeX Gyre Chorus, espresso `#341D13`; labels in Inter Medium capitals, spacing .42em, mocha `#694330`; both with a soft cream glow; hook title lower-left like the thumbnail. |
| **Cover / thumbnail** | `assets/reference/official-thumbnail.jpg` (the user made it; never replace it) | `scripts/make_thumbnail.py`: same grade and fonts; the word in Chorus with a soft cream glow behind the text block; kicker 40px and tag 37px Inter Medium mocha; lower-left on calm sheet or fur. |

To show the look, run `python3 -I scripts/style_guide.py OUT.html` and publish it as an artifact. That builds the visual style menu: the thumbnail, video frames, palette, fonts and rules. Do this when the user asks to see the style, and offer it at the start of a new post so they can confirm.

## Palette (from the user's sheet)

Cream `#FAF6F1`, light beige `#E3CEC0`, latte `#C69A77`, caramel `#A56D4E`, mocha `#694330`, espresso `#341D13`. Text is espresso and the accent is mocha; cream is for paper and backgrounds.

## Making a new Reel

The pipeline is the same one used for the Monday Reel. The plan format is in `references/reel-json.md`, and `assets/example-monday-reel.json` is the Monday plan to copy from (set `"style": "kanzoo-video"`).

1. **Inventory.** `python3 -I scripts/probe_footage.py WORK/probe clips...`, then read the contact sheets. Note the good moments, where his face sits, and duplicate uploads.
2. **Story.** Pick a short premise with 3–4 beats, such as a how-to, a "first time", or a routine with a punchline. Write the captions short. The Monday Reel's structure works well: hook title, steps, a fast replay with a ×2…×∞ counter, then a quiet punchline.
3. **Storyboard first.** `crop_thumbs.py reel.json WORK/thumbs --style kanzoo-video --sheet`, then `build_storyboard.py`, then publish it. Fix any crop that is only fur or sheet, and avoid shots that repeat each other. Ask about names on screen, length and music; the user adds music in Instagram. Don't render before approval.
4. **Render.**
   ```bash
   python3 -I scripts/render_shots.py reel.json WORK/r --size 2160x3840 --style kanzoo-video   # cached per shot
   python3 -I scripts/gen_composition.py reel.json WORK/r WORK/proj
   cd WORK/proj && npx -y hyperframes check && npx -y hyperframes snapshot --at <one time per section>
   npx -y hyperframes render -o renders/out.mp4 --fps 25 --video-frame-format png --video-bitrate 45M --quiet
   python3 -I scripts/mix_sfx.py WORK/r/cues.json WORK/proj/renders/out.mp4 FINAL.mp4
   ```
   Read every snapshot. Captions and pop-ups must not touch his eyes, nose or mouth, and the first letter of a label must not vanish on a dark blanket edge. If either happens, reframe the shot (`cy`/`cx`) or move the pop-up.
5. **Deliver.** Send the MP4 and a ZIP copy (`zip -0`), because the user's phone app downsizes plain video downloads to 720p. Keep each file under 100 MB: 45M bitrate suits about 16s.

## Making a cover or thumbnail

```bash
python3 -I scripts/make_thumbnail.py OUT.jpg --video clip.mov --at 13 --zoom 1.0 --cx 0.45 --cy 0.5 \
    --kicker "How to survive a" --word "Monday" --tag "Kanzoo edition"
```

Choose a frame where his face fills the upper right and the lower left is calm. Check the result once against `assets/reference/official-thumbnail.jpg`. If the user supplies their own thumbnail, use theirs as-is.

## Things the user decided (don't undo them)

- **Brightness:** they rejected looks that were too bright, too dark, or pale and washed out. The kanzoo-video grade is the middle they chose.
- **Text:** no white text, no bars or boxes behind text, no dark gradient fades. Espresso and mocha only.
- **Fonts:** one system everywhere: TeX Gyre Chorus + Inter Medium, in videos and thumbnails alike (the user's own font files). Show options as real posters before changing anything; the user decides from pictures, not descriptions.
- **Glow:** the soft cream glow behind the words is part of the look, matching the official thumbnail. It is a glow, never a bar or box, and never white text.
- **Pop-ups:** beeps and other pop-ups land in unexpected spots, a new place and tilt each time, never lined up along the edges and never on his face.
- **Punchlines:** they snap in on the cut (`{"text": "...", "punch": true}`).
- **Highlights:** off by default, because the loved Reel has none. If the user wants a second color, wrap words in `*asterisks*` in the plan. The colors are listed in `styles.json` under `highlight_options` (caramel, dusty rose, honey gold and others); set the style's `highlight_css` to the chosen one. They haven't decided yet, so ask.
- **4K honesty:** say that crops from landscape footage are upscaled, and that Instagram shows Reels at 1080 wide anyway.

## Files

- `scripts/`: the pipeline (`reelspec`, `probe_footage`, `crop_thumbs`, `build_storyboard`, `render_shots`, `gen_composition`, `mix_sfx`), plus `make_thumbnail.py`, `style_guide.py` and `style_menu.py`.
- `assets/styles.json`: the `kanzoo-video` style and the highlight options.
- `assets/fonts/`: TeX Gyre Chorus and Inter Medium (used), plus TeX Gyre Pagella Italic and Inter Regular (earlier drafts).
- `assets/reference/`: the official thumbnail and frames from the loved Reel.
- `assets/example-monday-reel.json`: the plan behind the loved Reel.
- `references/reel-json.md`: the plan file format.
