<!-- Updated: 2026-03-09 -->
# Banner Generation -- One-Shot AI Banners via KIE.ai

## Overview

Every GitHub repo deserves a professional banner. We generate the entire banner --
art, text, and layout -- in a single AI image generation call via KIE.ai Nano Banana 2.

**Why one-shot?** Nano Banana 2 renders text at ~87% accuracy. When the AI designs
the text as part of the composition, it looks integrated and stylized -- not like a
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
| API Format | png | No (always request PNG source -- convert after) |
| Delivery Format | webp | Yes (webp, jpg, png -- see Image Format Pipeline) |

## Supported Aspect Ratios

1:1, 1:4, 1:8, 2:3, 3:2, 3:4, 4:1, 4:3, 4:5, 5:4, 8:1, 9:16, 16:9, 21:9, auto

## Prerequisites

1. KIE.ai account -- sign up at https://kie.ai
2. API key -- generate at https://kie.ai/api-key
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
      "output_format": "png"
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

**Download the PNG source, then convert to optimal delivery format:**
```bash
mkdir -p assets
curl -s -o assets/banner-source.png "RESULT_URL"
```

**Convert to delivery format (WebP preferred, JPEG fallback):**
```python
from PIL import Image

img = Image.open("assets/banner-source.png")

# WebP -- best compression, GitHub renders it fine
img.save("assets/banner.webp", "WEBP", quality=80)

# JPEG fallback -- if user prefers maximum compatibility
# img.convert("RGB").save("assets/banner.jpg", "JPEG", quality=85)

import os
os.remove("assets/banner-source.png")  # clean up source
```

Default to **WebP**. Use JPEG only if the user specifically asks for it or if
the image will be embedded outside GitHub (email, forums, older tools).
See the **Image Format Pipeline** section below for the full decision logic.

### Crafting the Prompt

The prompt describes the COMPLETE banner -- layout, text, visual subject, effects,
and mood -- all in one go. Think like a graphic designer briefing a team.

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
[EFFECTS]: [finishing touches -- lens flare, bokeh, reflections, light bloom, particles]
[MOOD]: [background, lighting, color palette, overall aesthetic]
```

**Keep it under 150 words.** Nano Banana responds better to focused prompts.

### What Makes a Great Banner Prompt

**Strong visual metaphor.** Translate the project's purpose into a concrete image.
Don't describe what the project IS -- show what it DOES or REPRESENTS.

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
- "A banner for my project" -- too vague, generic output
- "Logo of ProjectName" -- AI logos look amateur
- Prompts over 200 words -- diminishing returns, confused output
- Multiple competing visual concepts -- pick ONE strong metaphor
- "Simple gradient background" -- boring, no identity

### Handling Text Failures

If the text comes out garbled or misspelled:
1. **Regenerate** -- just run the same prompt again (87% accuracy means most retries succeed)
2. **Simplify text** -- shorten the headline, remove the tagline, try ALL CAPS
3. **Pillow fallback** -- if 3 attempts fail on the same text, generate a background
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

img = Image.open("assets/banner-bg.png").convert("RGBA")
W, H = img.size
overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

# Adapt text, fonts, positions, and colors to the specific banner
# ...

result = Image.alpha_composite(img, overlay).convert("RGB")
# Strip metadata: create fresh image from pixel data only
clean = Image.new(result.mode, result.size)
clean.putdata(list(result.getdata()))
clean.save("assets/banner.webp", "WEBP", quality=80, method=6)
os.remove("assets/banner-bg.png")
```

---

## Post-Generation

1. **Show the banner to the user.** Use the Read tool on `assets/banner.webp`
   so they see it inline. Then provide the clickable local file link so the user
   can open it full-size in their browser or image viewer:
   ```
   Banner saved: file:///[absolute-path-to]/assets/banner.webp
   ```
   Use the actual absolute path (forward slashes, `file:///` prefix). Example:
   `file:///E:/my-project/assets/banner.webp` or `file:///home/user/my-project/assets/banner.webp`.
   Ask: "Here's your banner. Use it, regenerate, or skip?"
   Do NOT place it in the README until the user approves.
2. If approved, place at the very top of README, before H1:

```markdown
<p align="center">
  <img src="assets/banner.webp" alt="[Project Name] - [brief description]" width="100%">
</p>
```

## Image Format Pipeline

**The strategy: always start with the highest quality source, then convert to the
optimal delivery format.** We control the conversion, not the API.

### Step 1: Generate as PNG (lossless source)

Always request `output_format: "png"` from KIE.ai. This gives us a lossless source
image with maximum quality. We never lose data at the generation step.

### Step 2: Convert, strip metadata, and optimize

Use Pillow to convert from the PNG source to the optimal delivery format.
**Always strip metadata** -- no EXIF, no ICC profiles, no generation prompts,
no tool signatures. Clean, minimal, professional.

```python
from PIL import Image
import os

src = Image.open("assets/banner-source.png")

# Strip all metadata by creating a fresh image from pixel data only.
# Pillow's .save() without exif= already drops EXIF, but this also
# strips ICC color profiles and any other embedded chunks.
clean = Image.new(src.mode, src.size)
clean.putdata(list(src.getdata()))

# WebP -- preferred. ~30% smaller than JPEG, sharp, GitHub renders it natively.
# method=6 is slowest encode but smallest file (worth it, runs once).
clean.save("assets/banner.webp", "WEBP", quality=80, method=6)

# JPEG -- fallback if user explicitly requests it
# clean.convert("RGB").save("assets/banner.jpg", "JPEG", quality=85, optimize=True)

# Clean up the source PNG
os.remove("assets/banner-source.png")
```

**Why strip metadata?**
- **File size:** EXIF, ICC profiles, and AI generation metadata add 5-50KB of bloat.
  On a 100KB WebP banner, that is a significant percentage.
- **Privacy:** AI generation tools embed model names, prompt text, timestamps, and
  tool versions into image metadata. None of that should leak into a public repo.
- **Professionalism:** Clean images with zero metadata signal attention to detail.
  It is the kind of thing nobody notices when you do it, but auditors and tools flag
  when you don't.
- **Consistency:** Every image in the repo follows the same pipeline. No surprises.

### Step 3: Choose the right delivery format

| Image Type | Deliver As | Why |
|-----------|-----------|-----|
| AI-generated art (banners, avatars) | **WebP** (default) or JPEG | Rich photographic content. WebP is ~30% smaller than JPEG at equivalent quality. |
| Screenshots (terminal, UI, code) | **PNG** | Sharp edges, flat colors, text. PNG is lossless and often smaller than lossy formats for this content. Do NOT convert screenshots. |
| Logos, icons, diagrams | **PNG** or **SVG** | Clean lines, transparency, small palettes. SVG for vector art. |
| Photos (team, office, product) | **WebP** (default) or JPEG | Same as AI art. |

**The rule: AI art and photos get WebP. Screenshots and logos stay PNG.**

### When to use JPEG instead of WebP

- User explicitly requests JPEG
- Image will be embedded outside GitHub (email newsletters, forums, older CMS)
- User reports rendering issues with WebP in their specific context

For GitHub READMEs, WebP works perfectly. GitHub has rendered WebP natively for
years. There is no compatibility concern for GitHub-hosted content.

### Quality Settings

| Format | Quality | Notes |
|--------|---------|-------|
| WebP | 80 | ~30% smaller than JPEG q85 at equivalent visual quality. The sweet spot. |
| JPEG | 85 | Fallback. Best balance of size vs quality. Below 80, artifacts appear on text. |
| PNG | N/A (lossless) | Only for screenshots, logos, diagrams. Use pngquant for further compression if needed. |

### Applying This to Banners

1. Request PNG from KIE.ai (`output_format: "png"`)
2. Download as `assets/banner-source.png`
3. Strip metadata + convert to WebP: `assets/banner.webp` (quality 80, method 6)
4. Delete the source PNG
5. Reference in README as `assets/banner.webp`

### Applying This to Avatars

Same pipeline as banners, but always deliver as JPEG:
1. Request PNG from KIE.ai (`output_format: "png"`, `aspect_ratio: "1:1"`)
2. Download as `assets/avatar-source.png`
3. Strip metadata + convert to JPEG: `assets/avatar.jpg` (quality 85)
4. Delete the source PNG
5. Provide `file:///` link to the JPEG for the user to upload

```python
from PIL import Image
import os

src = Image.open("assets/avatar-source.png")
clean = Image.new(src.mode, src.size)
clean.putdata(list(src.getdata()))
clean.convert("RGB").save("assets/avatar.jpg", "JPEG", quality=85, optimize=True)
os.remove("assets/avatar-source.png")
print(f"Avatar saved: assets/avatar.jpg ({os.path.getsize('assets/avatar.jpg')//1024}KB)")
```

**Why JPEG?** GitHub's profile photo and social preview uploaders both reject WebP
and enforce a 1MB limit. AI-generated PNGs at 1K resolution routinely exceed 1MB.
JPEG at quality 85 produces avatars around 50-150KB with no visible quality loss
at the sizes GitHub displays them (40px to 460px).

### Scanning Existing Repo Images

When auditing or optimizing a repo, check for format mismatches and offer to fix them:

```
Issues to flag:
- PNG files > 200KB that contain AI art or photos -> convert to WebP (saves 60-70%)
- PNG banners of any size -> convert to WebP (always a win for photographic content)
- JPEG files that contain screenshots or text-heavy images -> these should be PNG
- Any image > 1MB -> flag for optimization regardless of format
- Hotlinked images from external URLs -> download and commit (link rot risk)
```

**Offer to convert, don't just flag.** If Pillow is available (and it usually is),
convert the image right there and show the size savings:

```python
from PIL import Image
import os

# Example: convert an oversized PNG banner to WebP (with metadata stripping)
src = Image.open("assets/banner.png")
clean = Image.new(src.mode, src.size)
clean.putdata(list(src.getdata()))
clean.save("assets/banner.webp", "WEBP", quality=80, method=6)

old_size = os.path.getsize("assets/banner.png")
new_size = os.path.getsize("assets/banner.webp")
savings = 100 - new_size * 100 // old_size
print(f"Converted: {old_size//1024}KB -> {new_size//1024}KB ({savings}% smaller, metadata stripped)")
# Then update the README reference and delete the old file
```

## Pricing

- 1K: ~4 cents per image
- 2K: ~6 cents
- 4K: ~9 cents

Regeneration is cheap. Don't settle for a mediocre banner -- try 2-3 times
to get something great.

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Unauthorized | Check KIE_API_KEY |
| 402 | Insufficient credits | Top up at https://kie.ai |
| 422 | Validation error | Check prompt and parameters |
| 429 | Rate limited | Wait 10 seconds, retry |
| 501 | Generation failed | Retry with simplified prompt |

## Nano Banana 2 Input Format Rules

**Nano Banana 2 accepts PNG and JPEG only. It does NOT accept WebP.**

This matters because our delivery pipeline converts images to WebP for size savings.
When a skill needs to feed an existing image back into Nano Banana 2 (for example,
to generate a social preview from an existing banner), the source image may already
be WebP. You MUST convert it before passing it as `image_input`.

**Dynamic format handling for image_input:**

1. Check the source image format
2. If WebP, convert to PNG (lossless, preserves quality) before sending
3. If PNG or JPEG, use directly
4. The image_input field accepts URLs, so either use a raw GitHub URL pointing to
   a committed PNG/JPEG, or host the converted file temporarily

```python
from PIL import Image
import os

source = "assets/banner.webp"
ext = os.path.splitext(source)[1].lower()

if ext == ".webp":
    # Convert to PNG for Nano Banana 2 compatibility
    img = Image.open(source)
    converted = source.rsplit(".", 1)[0] + "-input.png"
    img.save(converted, "PNG")
    print(f"Converted {source} to {converted} for API input")
    # Use `converted` as the image_input source
    # Clean up after API call completes
```

**When using a GitHub raw URL as image_input:** Make sure the committed file is
PNG or JPEG. If the repo only has the WebP version (because we optimized it),
either use an older commit's raw URL that still has the PNG/JPEG, or convert
locally and use a different hosting method.

---

## Social Preview Image Generation

GitHub social preview images (the card shown when a repo link is shared on Twitter/X,
LinkedIn, Slack, Discord) require a 1280x640 image (2:1 aspect ratio).

**Nano Banana 2 does not support 2:1 directly.** The closest supported ratio is 16:9.

### Strategy: Banner-to-Social-Preview Pipeline

The most efficient approach is to reuse the existing README banner rather than
designing a social preview from scratch. This keeps branding consistent and avoids
a separate design process.

**The pipeline:**

1. **Feed the existing banner into Nano Banana 2 as image_input at 16:9.**
   This recomposes the design for the new aspect ratio rather than just cropping.
   The AI adapts the layout, centering important elements.

2. **Crop the 16:9 result to 2:1.**
   A 16:9 image at 1K resolution is ~1680x945. Cropping to 2:1 means trimming
   ~52px from top and bottom (about 5% of the image height). With centered
   composition from step 1, nothing important gets clipped.

3. **Resize to exactly 1280x640 and save as PNG.**
   GitHub recommends PNG for social previews. Keep it as PNG (not WebP) because
   social preview images are served by GitHub's CDN for external platforms, and
   maximum compatibility matters here.

**Important:** The image_input source must be PNG or JPEG (see Nano Banana 2 Input
Format Rules above). If the banner is already WebP, convert to PNG first.

### Social Preview Prompt Formula

When feeding the banner as image_input, use this prompt pattern:

```
Recreate this exact banner design but recomposed for 16:9 aspect ratio.
Keep the same style, colors, text, and visual elements. Center the
composition so important elements are not at the extreme edges. Keep all
text fully visible and legible. Same [describe key visual elements:
background color, text style, main visual subject].
```

Key rules:
- Explicitly mention centering the composition (critical for the subsequent crop)
- Reference the specific visual elements you want preserved
- Keep the prompt under 100 words (the image_input does the heavy lifting)

### API Call

```bash
curl -X POST https://api.kie.ai/api/v1/jobs/createTask \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nano-banana-2",
    "input": {
      "prompt": "Recreate this exact banner design but recomposed for 16:9...",
      "image_input": ["https://raw.githubusercontent.com/{owner}/{repo}/main/path/to/banner.png"],
      "google_search": false,
      "aspect_ratio": "16:9",
      "resolution": "1K",
      "output_format": "png"
    }
  }'
```

Note: image_input tasks take longer (30-60 seconds vs 10-20 for text-only).
Poll with longer intervals.

### Crop and Resize Script

```python
from PIL import Image
import os

img = Image.open("assets/social-preview-16x9.png")
w, h = img.size

# Crop to 2:1 (center crop, trim top and bottom equally)
target_h = w // 2
trim = (h - target_h) // 2
cropped = img.crop((0, trim, w, h - trim))

# Resize to exactly 1280x640
preview = cropped.resize((1280, 640), Image.LANCZOS)

# Strip metadata
clean = Image.new(preview.mode, preview.size)
clean.putdata(list(preview.getdata()))

# Save as JPEG (GitHub social preview upload requires JPEG, rejects WebP and
# PNG is often over the 1MB limit at 1280x640)
clean.convert("RGB").save("assets/social-preview.jpg", "JPEG", quality=85, optimize=True)

# Verify under 1MB (GitHub rejects files over 1MB)
size = os.path.getsize("assets/social-preview.jpg")
if size > 1_048_576:
    # Re-save at lower quality to fit under 1MB
    clean.convert("RGB").save("assets/social-preview.jpg", "JPEG", quality=70, optimize=True)
    size = os.path.getsize("assets/social-preview.jpg")

# Clean up the 16:9 intermediate
os.remove("assets/social-preview-16x9.png")

print(f"Social preview saved: assets/social-preview.jpg ({size//1024}KB)")
```

### Post-Generation

1. Show the social preview to the user via Read tool and provide a clickable link:
   ```
   Social preview saved: file:///[absolute-path]/assets/social-preview.jpg
   ```

2. Provide the manual upload instructions (no API for this):
   ```
   To set your social preview:
   1. Open: https://github.com/{owner}/{repo}/settings
   2. Scroll to "Social preview"
   3. Click "Edit" > "Upload an image"
   4. Select: assets/social-preview.jpg
   5. Save changes

   Test it: paste your repo URL at https://www.opengraph.xyz
   ```

3. **Format policy: JPEG only, under 1MB.**
   GitHub's social preview uploader rejects WebP and PNG files at 1280x640
   routinely exceed the 1MB upload limit. JPEG at quality 85 produces files
   around 100-200KB, well within the limit. If a JPEG somehow exceeds 1MB
   (unlikely at 1280x640), the script automatically re-saves at quality 70.
   This is the one case where we use JPEG instead of WebP.

### When to Skip Social Preview Generation

- User explicitly says they don't want one
- The repo is private or internal (social sharing is unlikely)
- The user already has a custom social preview set (`usesCustomOpenGraphImage: true`)

---

## Data Retention

KIE.ai stores images for 14 days. Always download and commit to `assets/` --
never hotlink the KIE URL.
