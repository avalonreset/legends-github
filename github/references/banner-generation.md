# Optional local artwork

Artwork is optional. A repository can have a complete README and portfolio plan
without a banner, avatar, badges, or social preview. Follow the repository owner's
design direction; do not add a missing-artwork task merely to increase a score.

## Runtime behavior

The portable runtime does not configure or call image-generation services. It does
not read image-provider credentials. The existing flags are compatibility names
for local asset preparation:

```text
python legends_github.py readme --path <repository> --generate-assets
python legends_github.py empire --path <repository> --generate-avatar
```

These commands write local reports and may create the derivatives described below.
They do not publish files or upload images to GitHub. Existing asset files and their
originals are preserved. Running the commands without those flags does not prepare
images.

| Command | Supplied files | Behavior |
| --- | --- | --- |
| `readme --generate-assets` | `assets/banner.webp`, `.png`, `.jpg`, or `.jpeg` | Reuse the first matching banner; prepare a missing social preview locally. |
| `readme --generate-assets` | `assets/originals/banner.png`, `.webp`, `.jpg`, or `.jpeg` | If no banner exists, convert the original into `assets/banner.webp`. |
| `empire --generate-avatar` | `assets/avatar.jpg`, `.jpeg`, `.png`, or `.webp` | Reuse the first matching avatar without conversion. |
| `empire --generate-avatar` | `assets/originals/avatar.png`, `.jpg`, `.jpeg`, or `.webp` | If no avatar exists, convert the original into `assets/avatar.jpg`. |

If no local source is available, the command records that artwork was not supplied
and continues the repository plan. This is not a readiness failure. No artwork is
invented or downloaded. Existing social previews are reused.

## Local preparation

Pillow is needed only to create a derivative, not to reuse an existing asset or
complete repository planning. The helpers in `github/scripts/local_assets.py`:

- Preserve original files and refuse to overwrite an existing destination.
- Apply stored image orientation and strip metadata from new derivatives.
- Convert supplied banner originals to WebP and avatar originals to JPEG.
- Fit the complete banner inside a 1280 by 640 JPEG social preview with padding.

The entire source image is retained without slicing or stretching. Review the result before deciding
to use it. Choose formats according to the supplied artwork; diagrams and logos
may need different treatment than photographs. There is no unconditional rule to
convert every PNG or add decorative artwork.

The payload keeps compatibility fields such as `banner_generated` and
`avatar.generated`; these remain false because no new artwork is generated.
`banner_prepared`, `avatar.prepared`, and `social_preview_generated` describe local
derivatives. The asset mode is `local-only`.

## Working with an agent

Use supplied artwork when it fits the user's request. If the user asks for new
artwork, use an image tool already available in the current host, or let the user
supply a file. Tool availability and authorization determine that separate action;
this toolkit requires no particular host, model, account, key, or paid provider.
Do not run account setup or silently substitute a paid service.

Keep meaningful alt text for images included in a README. GitHub social-preview
and profile-photo uploads remain separate user-directed actions through GitHub's
interface. Report what was actually prepared and inspected; a local image is not
proof that an upload or publication occurred.

## Typography-first option

For the optional black, red, and white Legends treatment, use the [typography recipe](legends-banner-style.md) and `scripts/render_banner.py` with a supplied font and explicit copy. No image service is involved. Existing README content is preserved; placing new artwork is a targeted editing task.
