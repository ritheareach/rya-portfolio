"""Generate the public image catalog from editable JSON sources."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def build_catalog(write=True):
    catalog = {
        key: json.loads((ROOT / "src/content" / f"{key}.json").read_text())
        for key in ("gallery", "robots")
    }
    for key, entries in catalog.items():
        for entry in entries:
            if not isinstance(entry["caption"], str):
                raise ValueError(f"{key}: caption must be text")
            image = (ROOT / "public" / entry["src"]).resolve()
            if not image.is_relative_to(ROOT / "public/assets") or not image.is_file():
                raise ValueError(f"{key}: image not found in public/assets: {entry['src']}")
    if write:
        (ROOT / "public/assets/image-catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
    return catalog


if __name__ == "__main__":
    from build_images import build_images

    build_images()
    catalog = build_catalog()
    print({key: len(images) for key, images in catalog.items()})
