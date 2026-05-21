#!/usr/bin/env python3
"""
Convert and renumber a folder of photos.

Reads every image file in INPUT_DIR (heic / heif / jpg / jpeg / png /
webp / tif / bmp / gif), sorts them, converts each to JPEG, and writes
them into OUTPUT_DIR renamed 1.jpg, 2.jpg, … with zero-padded
numbering chosen automatically based on the file count.

Defaults are tuned for "pull a folder of iPhone photos and prep them
for a Jekyll site":
  * sort by EXIF capture date (falls back to file mtime)
  * JPEG quality 88
  * preserve EXIF metadata, ICC color profile, and orientation
  * no resize (pass --max-side to enable, e.g. --max-side 2400 for web)

Usage:
    python3 scripts/import_photos.py INPUT_DIR OUTPUT_DIR [options]

Examples:
    # Basic: convert everything in ~/Desktop/iphone-batch → assets/images/2026-05/
    python3 scripts/import_photos.py ~/Desktop/iphone-batch assets/images/2026-05

    # Also resize for the web (longest side <= 2400px), slightly lower quality
    python3 scripts/import_photos.py ~/Desktop/iphone-batch assets/images/2026-05 \\
        --max-side 2400 --quality 85

    # Start numbering at 100 with a prefix (→ trail-100.jpg, trail-101.jpg, ...)
    python3 scripts/import_photos.py ~/Photos/trail assets/images/trail \\
        --start 100 --prefix trail-

Dependencies:
    pip3 install pillow pillow-heif --break-system-packages

(On Apple Silicon, pillow-heif ships prebuilt wheels for the common
Python versions, so the install should be instant. If pip tries to
build from source you'll need `brew install libheif` first.)
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit(
        "Missing dependency: Pillow.\n"
        "Run:  pip3 install pillow pillow-heif --break-system-packages"
    )

# Register HEIC/HEIF support with Pillow if available.
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HEIC_OK = True
except ImportError:
    HEIC_OK = False


IMAGE_EXTS = {
    ".heic", ".heif",
    ".jpg", ".jpeg",
    ".png",
    ".webp",
    ".tif", ".tiff",
    ".bmp",
    ".gif",
}


def _exif_datetime(img):
    """Return EXIF DateTimeOriginal as a datetime, or None."""
    try:
        exif = img.getexif()
        if not exif:
            return None
        # 36867 = DateTimeOriginal, 36868 = DateTimeDigitized, 306 = DateTime
        for tag in (36867, 36868, 306):
            v = exif.get(tag)
            if v:
                try:
                    return datetime.strptime(
                        str(v).strip("\x00").strip(),
                        "%Y:%m:%d %H:%M:%S",
                    )
                except ValueError:
                    continue
    except Exception:
        pass
    return None


def _sort_key(path, mode):
    if mode == "name":
        return (path.name.lower(),)
    if mode == "mtime":
        return (path.stat().st_mtime, path.name.lower())
    # mode == "date": EXIF DateTimeOriginal → mtime fallback
    dt = None
    try:
        with Image.open(path) as img:
            dt = _exif_datetime(img)
    except Exception:
        dt = None
    if dt is None:
        dt = datetime.fromtimestamp(path.stat().st_mtime)
    return (dt, path.name.lower())


def collect_images(input_dir, sort_mode):
    files = [
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    ]
    if not files:
        return []
    files.sort(key=lambda p: _sort_key(p, sort_mode))
    return files


def convert_one(src, dst, quality, max_side):
    with Image.open(src) as img:
        # Respect EXIF orientation (iPhone shots are tagged, not rotated).
        img = ImageOps.exif_transpose(img)

        # Preserve color profile + EXIF if present.
        icc = img.info.get("icc_profile")
        exif_bytes = img.info.get("exif")

        # JPEG can't store alpha or palette; flatten to RGB.
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Optional resize.
        if max_side and max(img.size) > max_side:
            ratio = max_side / max(img.size)
            new_size = (round(img.width * ratio), round(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        save_kwargs = {
            "format": "JPEG",
            "quality": quality,
            "optimize": True,
            "progressive": True,
        }
        if icc:
            save_kwargs["icc_profile"] = icc
        if exif_bytes:
            save_kwargs["exif"] = exif_bytes

        img.save(dst, **save_kwargs)


def main():
    p = argparse.ArgumentParser(
        description="Convert and renumber a directory of photos to JPEG."
    )
    p.add_argument("input_dir", type=Path,
                   help="Directory containing source images.")
    p.add_argument("output_dir", type=Path,
                   help="Directory to write renumbered .jpg files.")
    p.add_argument("--quality", type=int, default=88,
                   help="JPEG quality 1-100 (default: 88).")
    p.add_argument("--max-side", type=int, default=0,
                   help="Resize so longest side <= N px. 0 = no resize "
                        "(default). Try 2400 for web.")
    p.add_argument("--sort", choices=("date", "name", "mtime"), default="date",
                   help="Sort source files by EXIF capture date (default), "
                        "filename, or mtime.")
    p.add_argument("--start", type=int, default=1,
                   help="First number to use (default: 1).")
    p.add_argument("--prefix", default="",
                   help='Prefix before the number, e.g. "img-" → img-01.jpg.')
    p.add_argument("--dry-run", action="store_true",
                   help="Show planned actions without writing files.")
    args = p.parse_args()

    in_dir = args.input_dir.expanduser().resolve()
    out_dir = args.output_dir.expanduser().resolve()

    if not in_dir.is_dir():
        sys.exit(f"ERROR: input dir not found: {in_dir}")
    if in_dir == out_dir:
        sys.exit("ERROR: input and output directories must differ.")

    files = collect_images(in_dir, args.sort)
    if not files:
        sys.exit(f"No supported image files found in {in_dir}")

    has_heic = any(f.suffix.lower() in (".heic", ".heif") for f in files)
    if has_heic and not HEIC_OK:
        sys.exit(
            "ERROR: HEIC files detected but pillow-heif is not installed.\n"
            "Install with:  pip3 install pillow-heif --break-system-packages"
        )

    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    # Zero-pad width based on the highest number we'll produce.
    end = args.start + len(files) - 1
    width = max(2, len(str(end)))

    print(f"Found {len(files)} image(s) in {in_dir}")
    print(f"Writing to        {out_dir}")
    print(f"Sort mode         {args.sort}")
    print(f"Quality           {args.quality}")
    print(f"Max side          {args.max_side if args.max_side else 'no resize'}")
    print(f"Numbering         {args.prefix}{args.start:0{width}d}.jpg .. "
          f"{args.prefix}{end:0{width}d}.jpg")
    print()

    failures = 0
    for i, src in enumerate(files):
        n = args.start + i
        dst_name = f"{args.prefix}{n:0{width}d}.jpg"
        dst = out_dir / dst_name

        if args.dry_run:
            print(f"  [dry-run] {src.name} → {dst_name}")
            continue

        try:
            convert_one(src, dst, args.quality, args.max_side)
            sz_in = src.stat().st_size / 1024
            sz_out = dst.stat().st_size / 1024
            print(f"  {src.name:40s} → {dst_name}   "
                  f"({sz_in:7.0f} KB → {sz_out:7.0f} KB)")
        except Exception as e:
            failures += 1
            print(f"  FAILED: {src.name} — {e}", file=sys.stderr)

    if args.dry_run:
        print(f"\n[dry-run] Would have written {len(files)} file(s).")
        return

    if failures:
        print(f"\n⚠  Done with {failures} failure(s). "
              f"{len(files) - failures} file(s) written to {out_dir}",
              file=sys.stderr)
        sys.exit(1)
    print(f"\n✓ Done. {len(files)} file(s) written to {out_dir}")


if __name__ == "__main__":
    main()
