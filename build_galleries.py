"""Generate the static gallery catalog from optimized image folders."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent
EXTENSIONS = {".webp", ".jpg", ".jpeg", ".png", ".avif"}


class ImageNotes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.notes = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img":
            self.notes[attrs["src"]] = attrs.get("alt", "")


def build_catalog(write=True):
    parser = ImageNotes()
    parser.feed((ROOT / "index.html").read_text())
    notes = parser.notes
    for folder, document in [("gallery/previews", "gallery/PHOTO-NOTES.md"),
                             ("robots", "robots/README.md")]:
        for line in (ROOT / "assets" / document).read_text().splitlines():
            match = re.search(r"\[([^]]+)\]\([^)]+\)", line)
            if match:
                filename = Path(match[1]).stem + ".webp"
                description = line.split("|")[-2].strip()
                notes.setdefault(f"assets/{folder}/{filename}", description)
    catalog = {}
    for key, folder in [("gallery", "assets/gallery/previews"), ("robots", "assets/robots")]:
        entries = []
        for path in sorted((ROOT / folder).iterdir()):
            if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
                continue
            if path.name == "hero-smart-car.webp" or path.stem.endswith("-hero"):
                continue
            src = path.relative_to(ROOT).as_posix()
            label = notes.get(src) or re.sub(r"[_-]+", " ", path.stem).strip()
            entries.append({"src": src, "alt": label})
        catalog[key] = entries
    if write:
        (ROOT / "assets/image-catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
    return catalog


if __name__ == "__main__":
    catalog = build_catalog()
    print({key: len(images) for key, images in catalog.items()})
