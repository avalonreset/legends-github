# Legends typography banner recipe

This is an optional visual treatment, extracted from the owner's approved September 2026 banners and their inspected rendering recipe. It is not a requirement for unrelated projects or proof of improved retention.

## Identity, explanation, then proof

A banner should answer two questions quickly: what is this called, and why would I use it? The README immediately below supplies a working example and evidence. Distinctive typography provides recognition; the subtitle carries meaning. Do not use mysterious slogans, a capability list, model-vendor names, or claims the product cannot support.

For example, the approved GeoGrid subtitle is:

> local ranking maps and reports, without a tracking subscription

It names the output and the meaningful difference. The approved GitHub subtitle is:

> agent-led repository audits, repairs, and search optimization

Both describe the project without pretending a banner proves its capabilities. Preserve owner-approved wording unless the requested task includes rewriting it.

## Visual contract

- Black background, red lowercase project title, white lowercase subtitle.
- Exact project name with its existing dash separators; no arbitrary rebranding.
- The supplied Legends Regular font for the Legends treatment. Never silently substitute another face and call it Legends.
- Left-aligned type, generous margins and readable text at normal README width.
- One or two deliberately broken subtitle lines. Shorten copy before shrinking it into a footnote.
- A restrained red edge and gray separator; no required mascot, gradient, badges, or decorative illustration.
- A 4:1 canvas, rendered at 4096 x 1024; lossless PNG and WebP plus a 1024 x 256 review preview.
- Preserve the complete image. No detached strips, slicing, stretching, or text-cropping social previews.

These dimensions and details describe this approved template, not a universal rule for every GitHub project. Keep another project's identity when applying the broader copy and readability principles.

## Render without an image service

Supply a local font you have permission to use. The toolkit does not bundle or download a proprietary font or configure a provider.

```powershell
python github/scripts/render_banner.py --title legends-geogrid --subtitle-line "local ranking maps and reports," --subtitle-line "without a tracking subscription" --font "C:/path/to/Legends-Regular.ttf" --output-dir "review-output/banner-v1"
```

Use a new output directory. The renderer refuses to overwrite earlier drafts, rejects overflowing copy, retains exact literal characters, and records asset/font hashes. It does not change the README or publish anything. Installed skills can use `GITHUB_HOME/scripts/render_banner.py`.

Inspect the small preview and original. Check exact characters, line breaks, readable size, whitespace, and contrast. Link the banner and write useful alt text when placing it in the README. Keep the subtitle available as real README text too; readers should not have to decode an image to understand the product. Preserve existing video artwork, captions, links, anchors, and section order.

## Evaluate the effect honestly

The intended effects are recognition and immediate comprehension. Retention and conversion are hypotheses until observed. Ask a new reader to explain the project and find the first useful example. Measure task completion or relevant traffic over comparable windows, recording other changes. Do not treat file generation, a higher checklist score, or a longer README as evidence that the banner worked.
