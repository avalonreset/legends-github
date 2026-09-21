# banner and social preview production

The old KIE.ai generation and 16:9 crop workflow is retired.

For Legends README banners, follow [the house style](../../docs/LEGENDS-README-STYLE.md).
For social previews, follow [the canonical SOP](../../docs/SOCIAL-PREVIEW-SOP.md)
and use `scripts/render_social_preview.py` with the approved font and copy.
The social canvas is 1280x640, with fixed 64 px title and 36 px subtitle sizes.
Render text directly; never stretch, crop, or regenerate the lettering with AI.

## Image Format Optimization

Keep a lossless PNG source for typography. Derive WebP for README delivery when
appropriate. Social cards use an opaque PNG under 1 MB; GitHub also accepts JPG
and GIF. Do not claim PNG is unsupported or require a paid image provider.
Inspect dimensions and rendered text before publishing. For non-Legends owners,
preserve their approved visual identity rather than forcing the house template.

## Social Preview Image Generation

The SOP covers rendering, overflow rejection, visual QA, agent-first browser
upload, supported computer-use fallback, and an honest manual handoff when
blocked. Saving or committing an image is separate from configuring GitHub.
