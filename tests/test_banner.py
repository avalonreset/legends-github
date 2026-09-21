"""Deterministic banner contracts without redistributing the Legends font."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageFont
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'github/scripts'))
from render_banner import render_banner
from local_assets import render_social_preview_from_banner


class BannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.font = self.root / 'fixture-font'
        self.font.write_bytes(b'test font identity')
        default_font = ImageFont.load_default()
        self.font_patch = patch('render_banner.ImageFont.truetype', return_value=default_font)
        self.font_patch.start()
        self.addCleanup(self.font_patch.stop)

    def test_render_lossless_and_refuse_overwrite(self):
        output = self.root / 'draft'
        result = render_banner('demo-project', ['a useful tool'], self.font, output)
        with Image.open(output / 'banner.png') as png, Image.open(output / 'banner.webp') as webp:
            self.assertEqual(png.size, (4096, 1024))
            self.assertEqual(png.convert('RGB').tobytes(), webp.convert('RGB').tobytes())
        self.assertFalse(result['published'])
        before = (output / 'banner.webp').read_bytes()
        with self.assertRaises(FileExistsError):
            render_banner('demo-project', ['different copy'], self.font, output)
        self.assertEqual(before, (output / 'banner.webp').read_bytes())

    def test_invalid_or_overflowing_copy_writes_nothing(self):
        output = self.root / 'invalid'
        with self.assertRaises(ValueError):
            render_banner('Wrong Name', ['copy'], self.font, output)
        with patch('render_banner.ImageDraw.ImageDraw.textbbox', return_value=(192, 212, 5000, 500)):
            with self.assertRaises(ValueError):
                render_banner('demo', ['copy'], self.font, output)
        self.assertFalse(output.exists())

    def test_social_preview_preserves_both_edges_without_crop(self):
        source = self.root / 'edges.png'
        image = Image.new('RGB', (400, 100), 'white')
        for x in range(30):
            for y in range(100):
                image.putpixel((x, y), (255, 0, 0))
                image.putpixel((399-x, y), (0, 0, 255))
        image.save(source)
        target = self.root / 'preview.jpg'
        render_social_preview_from_banner(source, target)
        with Image.open(target) as preview:
            self.assertEqual(preview.size, (1280, 640))
            self.assertGreater(preview.getpixel((20, 320))[0], 200)
            self.assertGreater(preview.getpixel((1260, 320))[2], 200)
            self.assertLess(max(preview.getpixel((640, 20))), 10)


if __name__ == '__main__':
    unittest.main()
