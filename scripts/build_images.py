"""Normalize gallery and robot uploads to WebP, retaining source images."""

from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent


def build_images():
    from PIL import Image, ImageOps

    Image.init()
    extensions = Image.registered_extensions()
    replacements = {}
    uploads = []
    for folder, size in (("gallery", 1000), ("robots", 1000)):
        directory = ROOT / "public/assets" / folder
        for source in sorted(directory.iterdir()):
            if not source.is_file() or source.name.startswith(".") or source.suffix.lower() in (".webp", ".md"):
                continue
            if source.suffix.lower() not in extensions:
                raise ValueError(f"Unsupported image format: {source}; upload a Pillow-supported static image")
            target = source.with_suffix(".webp")
            archive = ROOT / "src/assets" / folder / source.name
            if target.exists() or any(item[1] == target for item in uploads):
                raise ValueError(f"WebP filename collision: {target}")
            if archive.exists() and archive.read_bytes() != source.read_bytes():
                raise ValueError(f"Source filename collision: {archive}")
            uploads.append((source, target, archive, size))

    with TemporaryDirectory() as staging:
        for index, (source, target, archive, size) in enumerate(uploads):
            with Image.open(source) as image:
                if getattr(image, "n_frames", 1) > 1:
                    raise ValueError(f"Animated images are not supported: {source}")
                image = ImageOps.exif_transpose(image)
                image = image.convert("RGBA" if "A" in image.getbands() or "transparency" in image.info else "RGB")
                image.thumbnail((size, size), Image.Resampling.LANCZOS)
                image.save(Path(staging) / f"{index}.webp", "WEBP", quality=85, method=6)
        for index, (source, target, archive, _) in enumerate(uploads):
            archive.parent.mkdir(parents=True, exist_ok=True)
            if not archive.exists():
                archive.write_bytes(source.read_bytes())
            target.write_bytes((Path(staging) / f"{index}.webp").read_bytes())
            old = source.relative_to(ROOT / "public").as_posix()
            replacements[old] = target.relative_to(ROOT / "public").as_posix()

    if replacements:
        import json

        for folder in ("gallery", "robots"):
            path = ROOT / "src/content" / f"{folder}.json"
            entries = json.loads(path.read_text())
            for entry in entries:
                entry["src"] = replacements.get(entry["src"], entry["src"])
            path.write_text(json.dumps(entries, indent=2) + "\n")
        path = ROOT / "src/content/news.json"
        entries = json.loads(path.read_text())
        for entry in entries:
            old = "assets/gallery/" + entry["image"]
            if old in replacements:
                entry["image"] = Path(replacements[old]).name
        path.write_text(json.dumps(entries, indent=2) + "\n")
        path = ROOT / "src/site-template.html"
        template = path.read_text()
        for old, new in replacements.items():
            template = template.replace(f'"{old}"', f'"{new}"')
        path.write_text(template)
        for source, _, _, _ in uploads:
            source.unlink()


if __name__ == "__main__":
    build_images()
