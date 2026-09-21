# social preview production and upload

## formula

Use the approved banner's exact product name, subtitle, font and colors.
Recompose the text directly on a **1280 × 640 (2:1)** canvas. Never stretch or
crop the README banner, generate the lettering with AI, or introduce a mascot.
KIE.ai and the retired wolf graphics are not part of this workflow.

The Legends `legends-social-v1` layout is fixed:

| element | specification |
|---|---|
| background | solid black |
| font | actual Legends Regular, explicitly supplied; no silent substitution |
| title | exact lowercase product slug, red `#ff0000`, 64 px, one line |
| subtitle | approved copy, white, 36 px, up to three lines, 48 px line spacing |
| text safe area | 80 px from every edge |
| title position | left 80, top 176 |
| divider | x 80–1200, y 282, gray `#666666`, 1 px |
| subtitle position | left 80, top 324 |
| left rule | red, 4 px, full height |
| delivery | opaque RGB PNG, under 1,000,000 bytes |

Type sizes and positions do not change between projects. Wrap subtitles at word
boundaries using measured font widths. If copy does not fit, stop with a clear
overflow report; preserve the product name and obtain shorter approved copy or
an explicitly approved template revision. Never silently shrink text.

This is the Legends house formula. Preserve other owners' branding unless they
request it. Do not redistribute a proprietary font without a license; request
the user's font file when unavailable. Rendering needs Python and Pillow.

```powershell
python scripts/render_social_preview.py --title legends-github --subtitle "agent-led repository audits, repairs, and search optimization" --font "E:\legends-clip-hunter\public\fonts\Legends-Regular.ttf" --output assets/social-preview.png
```

Inspect the full PNG and a 640 × 320 thumbnail. Confirm spelling, safe margins,
line breaks, readable text, exact dimensions and file size. The neighboring JSON
records the font hash, fixed sizes, text bounds and image hash. Generating or
committing this file does **not** configure GitHub's social preview.

## agent uploads first

1. Confirm the exact repository, current authorization and local PNG. Reuse
   existing authorization to update repository presentation; do not ask again.
2. Discover tools actually available in the session. A client name is not proof
   it has browser control, file upload or computer use. On Benjamin's fleet use
   Legends Chrome Kit first, then a supported Legends Shell Kit action. Elsewhere
   use the available Claude/Codex browser extension or computer-use tool if it
   actually supports the required actions. Do not install new tooling implicitly.
3. Open the repository's **Settings → General → Social preview**. Inspect the
   actual page. Do not infer upload eligibility solely from privacy or plan.
4. Identify **Edit inside Social preview**, not Edit beside Default branch.
   Prefer an exact scoped element. If ambiguous, inspect again; do not repeatedly
   click the first Edit. Choose **Upload an image…**, supply the exact local PNG
   through a supported upload control or native file picker, and complete any
   save/crop confirmation shown. Preserve the full 2:1 image and its safe area.
5. If the primary tool cannot complete an action, try the next available supported
   route once the exact limitation is understood. Do not bypass blocked transports,
   extract cookies, or invent a private GitHub upload API. A blocked upload does
   not prevent generation and delivery of the finished image.
6. Reload Settings and visually inspect the saved thumbnail. Read repository
   `openGraphImageUrl` / `usesCustomOpenGraphImage` through GraphQL when available,
   and inspect the served image. A true custom-image flag alone may describe the
   OLD image, so compare the actual new design. Record uploaded-and-verified only
   when the new image is confirmed. Social networks may cache older previews.

## bounded manual fallback

If no supported route works, or authentication requires the human, provide the
finished local image link, its raw GitHub download link if pushed, the exact
repository settings URL, and the specific blocker. State **image ready; upload
not completed**. Give only the remaining steps: Social preview → Edit → Upload
an image → choose the provided PNG → complete the shown save control. Do not
pretend a repository commit updated this separate setting.

## source and acceptance

[GitHub's official social-preview documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)
recommends 1280 × 640 and accepts PNG, JPG or GIF under 1 MB. PNG is intentional
for crisp typography; JPEG is not required. This layout protects the text in the
2:1 source; arbitrary third-party crops cannot be guaranteed.

Done means a visually checked image plus an honest upload status: not attempted,
blocked with reason, or uploaded and verified. Existing custom imagery is not a
reason to skip a user-requested replacement.
