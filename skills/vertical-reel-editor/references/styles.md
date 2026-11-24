# Visual styles

Every style is an entry in `assets/styles.json`, with two fonts (one bold, one contrasting), a palette, an FFmpeg grade and caption CSS. `scripts/style_menu.py` renders all of them on the user's own frames, so they choose by eye. A summary follows; the JSON is the source of truth.

| key | name | fonts (bold + accent) | grade | suits |
|---|---|---|---|---|
| kanzoo-brand | Kanzoo Brand | Inter 600 + TeX Gyre Pagella italic (bundled in assets/fonts) | warm, calms blue/cyan and green, keeps oranges rich, deep blacks | every post on the account, so the grid matches |
| sleepy-diary | Sleepy Diary | Bricolage Grotesque 800 + Caveat 700 | rich golden: deep blacks, warm mids, light sharpening | sleepy pets, how-to routines, deadpan humor |
| editorial-script | Editorial Script | Jost 600 + Pinyon Script | bright, clean, neutral | recipes, treat or product prep, gifts |
| soft-film | Soft Film | Archivo 800 + Fraunces 600 italic | teal shadows, orange skin and fur, faded | firsts, outdoors, emotional stories |
| bold-meme | Bold Meme | Anton + Permanent Marker, outlined | contrasty, saturated, sharpened | chaos, zoomies, fails, punchlines |
| quiet-mono | Quiet Mono | DM Sans 600 + DM Mono, lowercase | desaturated and cool | routines, ASMR, diaries |
| pastel-pop | Pastel Pop | Fredoka 600 + Gaegu 700 | bright, airy, slightly saturated | kittens and puppies, birthdays, intros |

## Caption roles

- **label** (bold font): step numbers, the kicker and tag of the title. Short. The base size is 50px on the 1080 stage; `em` sizes in `label_css` scale from that.
- **line** (accent font): the action words, the big title word, the ending lines, the pops. Its size scales with `line_scale`.
- **scrim**: a soft gradient behind the caption band (and behind the title during the hook) that lifts light text off light fur. An empty string turns it off.
- **fade_to**: the color of the last 0.6s fade, which helps the Reel loop.

## Adding a custom style (a user's palette, swatch or reference video)

1. **Colors.** Take hex values straight from a swatch, or sample a reference frame. Set `light` (main text color), `dark` (shadows, outlines, fade) and `accent`.
2. **Fonts.** Pick two Google Fonts that exist as `@fontsource/<pkg>` on npm. A font that isn't on npm (like Pagella) can be bundled: put the file in `assets/fonts/` and set `"local": true` and `"file"` instead of `pkg`. Check that the file exists: `npm pack @fontsource/<pkg>` and look in `package/files/` for `<pkg>-latin-<weight>-<normal|italic>.woff2`. If the user said "not the same font" as their reference, pick fonts that differ in character, not just in name.
3. **Grade.** Build an FFmpeg chain from `curves` (lift blacks for matte), `eq` (contrast and saturation), `colorbalance` (shadow, mid and highlight tints) and `vignette`. Test it on one thumbnail next to the reference and compare. Raise brightness if it looks grey and muddy: lifted blacks plus lower saturation easily overshoots.
4. **CSS.** In `label_css` and `line_css`, use `var(--light)`, `var(--dark)` and `var(--accent-c)` for colors, and `var(--bold)` and `var(--accent)` for font families. Get readability from glow or shadow in the palette's own colors. Bars behind text are opt-in only.
5. Run `style_menu.py` again so the new style shows next to the others, and let the user confirm it.
