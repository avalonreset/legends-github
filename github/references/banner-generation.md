<!-- Updated: 2026-03-09 -->
# Banner Generation — One-Shot AI Banners via KIE.ai

## Overview

Every GitHub repo deserves a professional banner. We generate the entire banner —
art, text, and layout — in a single AI image generation call via KIE.ai Nano Banana 2.

**Why one-shot?** Nano Banana 2 renders text at ~87% accuracy. When the AI designs
the text as part of the composition, it looks integrated and stylized — not like a
sticker slapped on top. If text comes out garbled (~13% of the time), just regenerate.
At ~4 cents per shot, iteration is cheap.

**Pillow is the fallback, not the primary approach.** Only use Pillow compositing if
Nano Banana consistently fails on a specific text string after 2-3 attempts.

## Defaults

| Setting | Default | Customizable |
|---------|---------|-------------|
| Model | nano-banana-2 | No (suite standard) |
| Resolution | 1K | Yes (1K, 2K, 4K) |
| Aspect Ratio | 21:9 | Yes (see supported list) |
| Format | jpg | Yes (jpg, png) |

## Supported Aspect Ratios

1:1, 1:4, 1:8, 2:3, 3:2, 3:4, 4:1, 4:3, 4:5, 5:4, 8:1, 9:16, 16:9, 21:9, auto

## Prerequisites

1. KIE.ai account — sign up at https://kie.ai
2. API key — generate at https://kie.ai/api-key
3. `KIE_API_KEY` available via environment variable or `.env` file

**Loading the key:**
```bash
if [ -z "$KIE_API_KEY" ]; then
  for envfile in ./.env ~/.claude/skills/github/.env ~/.env; do
    if [ -f "$envfile" ]; then
      export $(grep -v '^#' "$envfile" | xargs) 2>/dev/null
      break
    fi
  done
fi
[ -n "$KIE_API_KEY" ] && echo "KIE_API_KEY loaded" || echo "KIE_API_KEY NOT FOUND"
```

If key is not found, guide the user:
1. Go to https://kie.ai and create an account
2. Navigate to https://kie.ai/api-key
3. Create a key, copy it immediately
4. Add to `.env`: `KIE_API_KEY=your_key_here`

---

## Generating a Banner

### API Calls

**Create task:**
```bash
curl -X POST https://api.kie.ai/api/v1/jobs/createTask \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nano-banana-2",
    "input": {
      "prompt": "YOUR_PROMPT_HERE",
      "image_input": [],
      "google_search": false,
      "aspect_ratio": "21:9",
      "resolution": "1K",
      "output_format": "jpg"
    }
  }'
```

**Poll for results** (every 3-5 seconds, typically completes in 10-20s):
```bash
curl -X GET "https://api.kie.ai/api/v1/jobs/recordInfo?taskId=TASK_ID" \
  -H "Authorization: Bearer $KIE_API_KEY"
```

States: `waiting` → `queuing` → `generating` → `success` / `fail`
Result URL is in `data.resultJson` → parse JSON → `resultUrls[0]`

**Download:**
```bash
mkdir -p assets
curl -s -o assets/banner.jpg "RESULT_URL"
```

### Crafting the Prompt

The prompt describes the COMPLETE banner — layout, text, visual subject, effects,
and mood — all in one go. Think like a graphic designer briefing a team.

**Text rendering rules (critical for accuracy):**
- Put exact text in double quotes: `"CLAUDE KNIFE"`
- Keep each text line under 25 characters for best accuracy
- Specify font style: "bold sans-serif", "lighter weight", "clean white"
- Describe text hierarchy: headline vs tagline vs features
- Specify text position: "left side", "bottom left", "centered"

**The prompt formula:**

```
Wide cinematic 21:9 GitHub repository banner.
[TEXT SIDE]: [describe text content, size, style, color, position]
[VISUAL SIDE]: [describe the visual subject, metaphor, details]
[EFFECTS]: [finishing touches — lens flare, bokeh, reflections, light bloom, particles]
[MOOD]: [background, lighting, color palette, overall aesthetic]
```

**Keep it under 150 words.** Nano Banana responds better to focused prompts.

### What Makes a Great Banner Prompt

**Strong visual metaphor.** Translate the project's purpose into a concrete image.
Don't describe what the project IS — show what it DOES or REPRESENTS.

- Terminal emulator → floating terminal window with glowing code
- CLI multitool → steampunk Swiss army knife with neon blades
- Video generation → GPU chip with spiraling filmstrip frames
- Web framework → modular floating city of connected buildings
- Data pipeline → crystalline streams flowing through prismatic gateway

**Finishing touches that elevate.** Add ONE or TWO of these, not all:
- Subtle lens flare from the brightest light source
- Soft bokeh particles in the background
- Polished reflective surface below the subject
- Volumetric light rays from a focal point
- Soft light bloom around edges
- Faint holographic scan lines
- Gentle particle dust catching the light
- Code patterns faintly visible in the background
- Cinematic depth of field

**Text styling that integrates.** Let the AI style the text as part of the design:
- Color the project name to match the visual theme (gold for warm scenes, cyan for tech)
- Split-color names work well: "Benjamin" in white + "Term" in green
- ALL CAPS for impact, mixed case for elegance
- The tagline should be noticeably smaller and lighter weight than the name

### Example Prompts

**Terminal emulator (dark, developer aesthetic):**
```
Wide cinematic 21:9 GitHub repository banner. Left side: large bold
headline "BenjaminTerm" in white with "Term" in bright green, below:
"Modern Terminal Emulator" in lighter weight. Right side: sleek floating
terminal window with green glowing code and blinking cursor, soft light
bloom around the terminal edges, faint holographic scan line effect.
Subtle green light reflecting on a dark glass surface below. Deep dark
navy background, neon green accents, cinematic depth of field.
Professional developer tool aesthetic.
```

**CLI multitool (cinematic product shot):**
```
Wide cinematic 21:9 GitHub repository banner. Left side: bold white
sans-serif text "CLAUDE KNIFE" as large headline, below in smaller
lighter weight: "The Swiss Army Knife for Claude Code". Right side:
ornate steampunk Swiss army knife with glowing neon blades fanned open,
dramatic rim lighting, floating above a polished reflective surface.
Subtle blue lens flare from the brightest blade. Soft bokeh particles.
Dark charcoal background with faint code patterns. Professional tech
product banner, cinematic depth of field.
```

**AI/GPU tool (warm painterly):**
```
Wide cinematic 21:9 GitHub repository banner. Left half: large bold text
"wan2gp" in warm golden gradient color with subtle glow, below in clean
white: "AI Video Generation". Right half: glowing GPU chip with spiraling
filmstrip frames showing morphing landscapes, soft volumetric light rays
emanating from the GPU core, gentle particle dust catching the light.
Painterly digital art style with teal and orange tones. Dark background
with subtle vignette. Professional layout, cinematic lighting.
```

### What NOT to prompt
- "A banner for my project" — too vague, generic output
- "Logo of ProjectName" — AI logos look amateur
- Prompts over 200 words — diminishing returns, confused output
- Multiple competing visual concepts — pick ONE strong metaphor
- "Simple gradient background" — boring, no identity

### Handling Text Failures

If the text comes out garbled or misspelled:
1. **Regenerate** — just run the same prompt again (87% accuracy means most retries succeed)
2. **Simplify text** — shorten the headline, remove the tagline, try ALL CAPS
3. **Pillow fallback** — if 3 attempts fail on the same text, generate a background
   WITHOUT text (add "no text, no letters, no words" to prompt) and composite text
   using the Pillow fallback script below

### Pillow Fallback Script

Only use this if one-shot text generation fails repeatedly.

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def load_font(weight, size):
    for path in [f"C:/Windows/Fonts/Roboto-{weight}.ttf",
                 f"/usr/share/fonts/truetype/roboto/Roboto-{weight}.ttf"]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    for fb in ["arial.ttf", "C:/Windows/Fonts/arial.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(fb, size)
        except OSError: continue
    return ImageFont.load_default(size=size)

img = Image.open("assets/banner-bg.jpg").convert("RGBA")
W, H = img.size
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

# Adapt text, fonts, positions, and colors to the specific banner
# ...

result = Image.alpha_composite(img, overlay).convert("RGB")
result.save("assets/banner.jpg", quality=95)
```

---

## Post-Generation

1. **Show the banner to the user.** Use the Read tool on `assets/banner.jpg`
   so they see it inline. Then provide the clickable local file link so the user
   can open it full-size in their browser or image viewer:
   ```
   Banner saved: file:///[absolute-path-to]/assets/banner.jpg
   ```
   Use the actual absolute path (forward slashes, `file:///` prefix). Example:
   `file:///E:/my-project/assets/banner.jpg` or `file:///home/user/my-project/assets/banner.jpg`.
   Ask: "Here's your banner. Use it, regenerate, or skip?"
   Do NOT place it in the README until the user approves.
2. If approved, place at the very top of README, before H1:

```markdown
<p align="center">
  <img src="assets/banner.jpg" alt="[Project Name] — [brief description]" width="100%">
</p>
```

## Pricing

- 1K: ~4 cents per image
- 2K: ~6 cents
- 4K: ~9 cents

Regeneration is cheap. Don't settle for a mediocre banner — try 2-3 times
to get something great.

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Unauthorized | Check KIE_API_KEY |
| 402 | Insufficient credits | Top up at https://kie.ai |
| 422 | Validation error | Check prompt and parameters |
| 429 | Rate limited | Wait 10 seconds, retry |
| 501 | Generation failed | Retry with simplified prompt |

## Data Retention

KIE.ai stores images for 14 days. Always download and commit to `assets/` —
never hotlink the KIE URL.
