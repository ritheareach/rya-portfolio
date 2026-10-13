"""Run with python3 -m unittest discover -s scripts -p 'test_*.py'."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PIL import Image
import build_images


class ImageBuildTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.patch = patch.object(build_images, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        for folder in ("gallery", "robots"):
            (self.root / "public/assets" / folder).mkdir(parents=True)
        (self.root / "src/content").mkdir(parents=True)
        for name, entries in (
            ("gallery", [{"src": "assets/gallery/photo.JPG", "caption": "Photo"}]),
            ("robots", [{"src": "assets/robots/robot.png", "caption": "Robot"}]),
            ("news", [{"image": "photo.JPG"}]),
        ):
            (self.root / "src/content" / f"{name}.json").write_text(json.dumps(entries))
        (self.root / "src/site-template.html").write_text('<img src="assets/gallery/photo.JPG"><img src="assets/robots/robot.png">')

    def test_conversion_preserves_sources_and_updates_references(self):
        gallery = self.root / "public/assets/gallery"
        robots = self.root / "public/assets/robots"
        exif = Image.Exif()
        exif[274] = 6
        Image.new("RGB", (1600, 400), "red").save(gallery / "photo.JPG", exif=exif)
        Image.new("RGBA", (600, 1800), (0, 255, 0, 80)).save(robots / "robot.png")
        Image.new("RGB", (30, 15), "blue").save(gallery / "small.bmp")
        Image.new("RGB", (17, 23), "black").save(gallery / "existing.webp")
        originals = {path: path.read_bytes() for path in (gallery / "photo.JPG", robots / "robot.png", gallery / "small.bmp")}
        existing = (gallery / "existing.webp").read_bytes()

        build_images.build_images()

        for source, data in originals.items():
            self.assertFalse(source.exists())
            self.assertEqual((self.root / "src/assets" / source.parent.name / source.name).read_bytes(), data)
        for path, size in ((gallery / "photo.webp", (250, 1000)), (robots / "robot.webp", (333, 1000)), (gallery / "small.webp", (30, 15))):
            with Image.open(path) as image:
                self.assertEqual(image.format, "WEBP")
                self.assertEqual(image.size, size)
        with Image.open(robots / "robot.webp") as image:
            self.assertEqual(image.getpixel((10, 10))[3], 80)
        self.assertEqual((gallery / "existing.webp").read_bytes(), existing)
        self.assertEqual(json.loads((self.root / "src/content/gallery.json").read_text())[0]["src"], "assets/gallery/photo.webp")
        self.assertEqual(json.loads((self.root / "src/content/robots.json").read_text())[0]["src"], "assets/robots/robot.webp")
        self.assertEqual(json.loads((self.root / "src/content/news.json").read_text())[0]["image"], "photo.webp")
        self.assertEqual((self.root / "src/site-template.html").read_text(), '<img src="assets/gallery/photo.webp"><img src="assets/robots/robot.webp">')
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        build_images.build_images()
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_invalid_uploads_do_not_remove_or_overwrite_images(self):
        gallery = self.root / "public/assets/gallery"
        Image.new("RGB", (10, 20), "red").save(gallery / "photo.JPG")
        Image.new("RGB", (20, 10), "blue").save(gallery / "photo.webp")
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with self.assertRaisesRegex(ValueError, "collision"):
            build_images.build_images()
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        (gallery / "photo.webp").unlink()
        (gallery / "z-corrupt.png").write_bytes(b"not an image")
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with self.assertRaises(OSError):
            build_images.build_images()
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
