---
name: vertical-reel-editor
description: Edit a person's own phone or camera clips (pets, kids, food, travel, daily life) into a finished vertical 9:16 Reel, TikTok or Short. The workflow studies a reference reel's editing techniques, shows a visual style menu, gets a storyboard approved, then renders a graded edit with animated captions and synthesized sound effects up to 4K, using FFmpeg, HyperFrames and yt-dlp. Use this whenever someone uploads footage and wants it edited "like this reel", asks for a storyboard, a caption style, a color palette or look for a short video, wants their pet or life clips turned into a Reel, TikTok or Short, or wants an earlier Reel re-cut, shortened, restyled or re-rendered in 4K, even if they never say "skill" or name these tools.
compatibility: Needs ffmpeg/ffprobe, Node with npx (HyperFrames is run with `npx hyperframes`, never installed globally), Python 3, and a Chromium for HyperFrames rendering. yt-dlp is optional (only for downloading reference reels).
---

# Vertical Reel Editor

Turn someone's raw clips into a short vertical video that feels made on purpose: a story with a hook, rhythm that changes, captions in a deliberate type system, a consistent grade and sound on the actions. The person approves a storyboard before anything is rendered, and picks the look from a menu that shows their own footage.

The scripts in `scripts/` carry the mechanics, so your job is judgment: what the story is, which moments are worth a shot, what the reference does well, and how to adapt it.

## The workflow

1. **Inventory the footage.** Look at every clip.
2. **Study the reference.** If they gave you one, work out its techniques.
3. **Find the story.** Pick an angle that fits their footage, rather than copying the reference.
4. **Style menu.** They pick a look by seeing their footage in each style.
5. **Storyboard.** Every shot as a real crop. Get approval before rendering.
6. **Render.** Shots, then grade, then captions in HyperFrames, then sound effects. 1080p first, or 4K if asked.
7. **Deliver and revise.** Send the file, then re-cut cheaply on feedback.

Each step below says what to run and what to watch for. The scripts use one shared edit plan file, `reel.json`. Read `references/reel-json.md` before writing it. `assets/example-reel.json` is a complete working example (the Kanzoo Monday Reel).

Run scripts with `python3 -I <skill>/scripts/<name>.py`. They find their own helpers, so they work from any directory. Keep work files in a scratch directory and put finals where the user can open them.

---

### 1. Inventory the footage

```bash
python3 -I scripts/probe_footage.py WORK/probe clip1.mov clip2.mov photo.jpg
```

This prints size, length, fps and audio peak for every file, flags duplicate uploads, and writes a contact sheet per clip (one frame every 2s, with timestamps). Read every sheet. You need to know where the good moments are (in-points), where the subject sits in the frame (crop centre), and which clips are near-silent.

Most phone footage is landscape 4K. A 9:16 crop from it is only about 1215×2160, which comes out sharp at 1080×1920. At 4K output it is upscaled, so say so plainly when 4K is requested (see step 7).

People often re-upload the same clips with new names. Use each clip once.

### 2. Study the reference (if there is one)

If they paste links, try `yt-dlp -o "WORK/ref.%(ext)s" URL`. Instagram and TikTok are often blocked by the network or need a login. If the download fails, don't fight it: ask them to save the reel or screen-record it and upload the file. Asking for that is faster than changing network settings, and you can never invent what a reel you couldn't watch looks like.

```bash
python3 -I scripts/analyze_reference.py ref.mp4 WORK/ref
```

Read the sheets, `title.jpg` and `wave.png`, then write down the techniques in plain words. Typical things to look for:

- **Title system:** how many lines, which fonts and sizes, and whether it stays on screen while shots cut underneath.
- **Order:** is the payoff shown first, as a hook?
- **What each cut lands on:** a hand action, a reaction, a beat in the music.
- **Rhythm:** the average shot length per third, from `analysis.json`. Fast middles and slow endings are common.
- **Transitions and moves:** speed ramps, push-ins, rotations.
- **Sound:** foley or ASMR hits (spiky waveform), a music bed (dense), silence.
- **Grade:** bright and neutral, warm and matte, punchy.

A reference shows techniques to adapt, not an edit to copy. People notice and dislike a 1:1 copy of someone else's reel. Keep the rhythm and devices, and replace the story, words and look with their own. If they send a second reference for one aspect only, such as "this is the colour palette", take only that aspect from it. Ask before taking its fonts too.

### 3. Find the story

Short pet and life videos land when they have a premise. "How to survive a Monday: Step 1 ignore the alarm, Step 2 toe bean stretch, Step 3 repeat" works because a sleeping kitten doing nothing becomes the joke. Look at what the footage really shows (sleepy, chaotic, sweet, clumsy) and give it a frame:
- a how-to list
- a "first time" story
- a day-in-the-life
- a reaction gag
- a counter ("×2 … ×∞")
- a before and after

If they hand you their own script or idea, use it, even loosely ("not exactly like this"). Keep each section's caption short enough to read in under a second.

Length: about 15–24s for Reels. A step that only repeats footage from another step is the first thing to cut. If they say a section is unnecessary, remove the whole section and renumber, rather than squeezing it.

### 4. Visual style menu

Show the look before you plan the shots around it. Make 2–3 representative 9:16 frames: write a rough `reel.json` with a few shots, or crop by hand. Then:

```bash
python3 -I scripts/crop_thumbs.py reel.json WORK/raw          # ungraded crops
python3 -I scripts/style_menu.py WORK/style-menu.html WORK/raw/<face>.jpg WORK/raw/<detail>.jpg \
    --title "<Name>'s style menu" --label "STEP 1" --line "<a real caption from the story>" [--current <style>]
```

Publish the HTML as an artifact and ask which style they want. Put a clear, characterful frame first: a face beats a patch of fur. The six built-in styles are described in `references/styles.md`:

| Style | What it is |
|---|---|
| sleepy-diary | Butter and espresso, Bricolage Grotesque plus Caveat handwriting, warm matte grade. The Kanzoo look. |
| editorial-script | Bright neutral grade, Jost caps plus a Pinyon Script title word. |
| soft-film | Teal-orange faded grade, Archivo plus italic Fraunces. |
| bold-meme | Punchy saturated grade, Anton plus Permanent Marker with outlines. |
| quiet-mono | Desaturated cool grade, small lowercase DM Sans and DM Mono. |
| pastel-pop | Bright airy grade, Fredoka plus Gaegu on candy colors. |

If they give their own palette (a swatch image, hex codes or a reference video), add a style to `assets/styles.json`. `references/styles.md` explains how. A style uses **at most two fonts: one bold and one contrasting**, which is a rule people asked for directly. Labels with no background bar are the default. If someone dislikes bars, solve readability with a glow or shadow in the text's own palette instead.

### 5. Storyboard, then approval

Write the full `reel.json`: sections, shots with in-points and crops, title card, pops, SFX cues and storyboard text. Then check the crops:

```bash
python3 -I scripts/crop_thumbs.py reel.json WORK/thumbs --style <style> --sheet
```

Read `WORK/thumbs/_sheet.jpg`. Fix any crop that shows only fur, sheet or blur, or that nearly matches its neighbour: move `cx`/`cy`, lower `zoom`, or pick another in-point. One fix pass is usually enough.

```bash
python3 -I scripts/build_storyboard.py reel.json WORK/thumbs WORK/storyboard.html
```

Publish it as an artifact. In your reply, summarize the beats in a small table and ask the open questions. Usually there are three:
1. Names on screen, such as the pet's name.
2. Music: they add it in the app (recommended, because the app handles licensing), or they send a track.
3. Length.

Don't render until they answer. Rendering is the slow part, and storyboard changes are cheap.

### 6. Render

```bash
# a. shots: crop, speed, push-ins, roll, then concat and grade (cached per shot)
python3 -I scripts/render_shots.py reel.json WORK/r --size 1080x1920      # or 2160x3840 for 4K
# b. captions: HyperFrames project + SFX cue list
python3 -I scripts/gen_composition.py reel.json WORK/r WORK/proj
cd WORK/proj && npx -y hyperframes check            # fix errors; read the contrast/overlap warnings
npx -y hyperframes snapshot --at <one time per section>   # LOOK at the contact sheet
npx -y hyperframes render -o renders/out.mp4 --fps 25 --quiet [--video-bitrate 32M for 4K]
# c. sound
python3 -I scripts/mix_sfx.py WORK/r/cues.json WORK/proj/renders/out.mp4 FINAL.mp4
```

4K shot rendering takes several minutes, and so does the HyperFrames render. Run both in the background and carry on: write the next script, prepare the delivery note.

**Reading the check output:**
- **Errors:** fix them. The usual one is `content_overlap` between the title word and the tag; add margin.
- **Contrast warnings on labels over fur:** look at the snapshot before acting. A glow often reads fine even when the number says 2.x:1.
- **Safe-zone warnings:** the layout is built for the Instagram Reels safe area. TikTok and Shorts side warnings are fine for an Instagram post.
- **`line_unread` on ×4/×5 counters in a fast replay:** intentional; leave them.
- **`film_silent`:** expected. The sound is added in step c.

In the snapshot, check that every caption sits over the right shots, that nothing covers the face, and that the end line is readable for at least about 1.5s.

### 7. Deliver and revise

Send the final file with the file-sending tool, and say:
- The length, resolution and fps.
- What's on screen, section by section, in a short table.
- That music is meant to be added in the app, with the original sound kept at about 50–70% so the SFX still come through.
- For 4K from landscape phone footage: the text is rendered at true 4K, but the footage is upscaled from about 1215×2160 crops, and Instagram shows Reels at 1080 wide anyway.

If the work is in a git repo, commit the final MP4 when asked or when a hook requires it. Keep each file under 100 MB, so use `--video-bitrate 32M` for 4K at about 20s. Give each new cut a new filename, so earlier versions stay.

Revisions are cheap if you keep the plan as the source of truth: edit `reel.json`, then rerun `render_shots.py`. Unchanged shots come from the cache and only the join and grade rerun. Then rerun `gen_composition.py`, the check, a snapshot, the render and `mix_sfx.py`. Captions and SFX use time references like `"08+0.12"` tied to shot IDs, so they follow the new cuts automatically. When someone says "remove step 3", also fix anything that depended on it, such as a replay montage that reused its clip.

---

## Things people asked for in real use (keep doing these)

- They wanted an approval step before any render, with real frames on the storyboard, not sketches.
- They wanted their own palette and fonts, never the reference's. Max two fonts.
- They found butter bars behind labels heavy. Glowing letters read better.
- They cut duplicate-feeling shots when trimming, before shortening the good ones.
- They wanted honest answers about 4K, network blocks and what you could and couldn't watch.
- Music is added by the user in the app, and the sound effects are made with FFmpeg, so nothing in the file needs a license.

## Files

- `scripts/reelspec.py`: shared loader, frame-accurate timeline, time-reference resolver.
- `scripts/probe_footage.py`, `scripts/analyze_reference.py`: footage inventory and reference breakdown.
- `scripts/crop_thumbs.py`, `scripts/style_menu.py`, `scripts/build_storyboard.py`: everything the user sees before rendering.
- `scripts/render_shots.py`, `scripts/gen_composition.py`, `scripts/mix_sfx.py`: the render pipeline.
- `assets/styles.json`: the style menu data (fonts, palette, grade, caption CSS).
- `assets/example-reel.json`: a full working plan to copy from.
- `references/reel-json.md`: every field of the plan file. Read it before writing one.
- `references/styles.md`: the styles in words, and how to add a custom one.
