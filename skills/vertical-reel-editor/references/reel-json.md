# reel.json: the edit plan

One file drives the storyboard, the render, the captions and the sound. Relative source paths resolve from the file's folder. `assets/example-reel.json` is a complete example.

```jsonc
{
  "title": "How to survive a Monday",          // storyboard heading
  "fps": 25,                                    // match the footage (DJI / most phones: 25 or 30)
  "style": "sleepy-diary",                      // key in assets/styles.json
  "sources": {                                  // short keys used by shots
    "W": "clips/sheets.mov",                    // string or {"path": ..., "kind": "video"|"image"}
    "F": "photo.jpg"                            // images are held as stills (kind inferred from extension)
  },
  "title_card": {"kicker": "How to survive a", "word": "Monday", "tag": "Kanzoo edition"},
  "sections": [
    {"id": "hook", "title": "Hook", "note": "Title over three quick shots."},
    {"id": "s1", "label": "Step 1", "line": "ignore the alarm", "note": "..."},
    {"id": "end", "title": "That's it", "lines": ["That's it.", "That's the whole routine."]}
  ],
  "shots": [ ... ],
  "pops": [ ... ],
  "sfx": [ ... ],
  "storyboard": {"intro": "...", "reference": {...}, "questions": ["..."]}
}
```

## shots[] (in film order)

| field | meaning | typical |
|---|---|---|
| `id` | unique, used by time references | "01", "02" ... |
| `section` | which section it belongs to | "s1" |
| `dur` | seconds on screen (snapped to whole frames) | 0.36 to 2.4 |
| `src`, `in` | source key and the second to start from | "H", 7.0 |
| `zoom` | 1 = full source height in 9:16; 2 = 2x punch-in | 1.0 to 2.6 |
| `cx`, `cy` | crop centre, 0 to 1 of source width and height | 0.47, 0.22 |
| `speed` | playback speed; reads dur×speed seconds of source | 2 for replays and ramps |
| `push` | slow zoom-in across the shot | 0.03 to 0.08 |
| `roll` | eased 180-degree rotation over 0.6s (the "flip over" move) | true |
| `what`, `sound` | storyboard notes: what we see, what we hear | |

Punch-ins above about 2.6x on 4K sources start to look soft at 1080. The grade is applied to the joined video, never per shot, so the look stays even.

## sections[]

The first section's window holds the `title_card`. Its three lines land on the first three shots of that section.

- `label` + `line`: a step caption that stays on screen for the whole section. The label is set in the bold font, the line in the accent font.
- `lines`: ending lines shown one after another, spread over the section's shots.
- `title` / `note`: storyboard heading and one-line description only.

## Highlight words (second colour)

Wrap any word in `*asterisks*` inside `title_card`, `sections[].label/line/lines` or `pops[].text` to set it in the style's `highlight_css` colour, e.g. `"line": "ignore the *alarm*"`. Use it for the hook word and one key word per section; a pop with `"highlight": true` is coloured whole. Keep it to one highlight per line so it stays special.

## Time references (pops and sfx)

`3.2` absolute · `"08"` start of shot 08 · `"08+0.12"` / `"08-0.3"` offset · `"08.end"` end of shot 08 · `"end-0.6"` from the film's end. Tie cues to shots, never to absolute times, so they follow re-cuts.

## pops[]

Short accent-font pop-ups that appear, wiggle in and vanish: beeps, counters, "x2", sound words.

```json
{"text": "BEEEP", "at": "07+0.03", "until": "08+0.12", "x": 560, "y": 380, "size": 140, "rot": 4}
```

`x`/`y`/`size` are on the 1080×1920 stage. Keep them inside x 130–950 and y 260–1450 for the Reels safe area, and off the subject's face.

## sfx[]

```json
{"sound": "alarm", "at": "04+0.08", "until": "08+0.12", "vol": 0.9}
```

The sounds are `alarm` (give it `until`), `pop`, `tick`, `whoosh` (start it about 0.3s before a section change), `chime`, `boing` and `thud`. Volumes range from 0.5 to 0.9. Leave headroom for the music the user adds in the app.

## storyboard

`intro` (one or two sentences), `reference` (`name`, `techniques` as `[title, description]` pairs, `frames` as `[path, caption]`), and `questions` (what you need decided before rendering).
