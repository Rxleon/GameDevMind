#!/usr/bin/env python3
"""
图片资源审计：缺失引用、未引用文件、大体积 PNG。

用法:
  python tools/check/check_images.py
  python tools/check/check_images.py --compress   # 需 Pillow，仅优化可安全重写的 PNG
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib_config import ROOT, load_config

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}


def collect_references(mds_root: Path) -> dict[Path, set[Path]]:
    """Map resolved image path → set of md files referencing it."""
    refs: dict[Path, set[Path]] = {}
    for md in mds_root.rglob("*.md"):
        text = md.read_text(encoding="utf-8", errors="ignore")
        for m in IMAGE_RE.finditer(text):
            raw = m.group(1).strip().split()[0].split("?")[0].split("#")[0]
            if raw.startswith(("http://", "https://")):
                continue
            p = (md.parent / raw).resolve() if not raw.startswith("/") else (ROOT / raw.lstrip("/"))
            refs.setdefault(p, set()).add(md)
    return refs


def collect_image_files(dirs: list[Path]) -> set[Path]:
    files: set[Path] = set()
    for d in dirs:
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if p.is_file() and p.suffix.lower() in IMG_EXT:
                files.add(p.resolve())
    return files


def try_compress(path: Path) -> int:
    try:
        from PIL import Image
    except ImportError:
        print("  Pillow not installed — skip compress (pip install Pillow)")
        return 0

    before = path.stat().st_size
    img = Image.open(path)
    img.save(path, optimize=True)
    after = path.stat().st_size
    return before - after


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compress", action="store_true", help="Optimize PNG in place (Pillow)")
    args = parser.parse_args()

    cfg = load_config()
    scan_dirs = [ROOT / d for d in cfg["images"]["scan_dirs"]]
    mds_root = ROOT / cfg["repo"]["mds_dir"]
    large_kb = cfg["images"].get("large_file_kb", 500)

    refs = collect_references(mds_root)
    # Also scan README, cases, etc.
    for extra in ["README.md", "cases", "ai-cases", "code"]:
        p = ROOT / extra
        if p.is_file():
            text = p.read_text(encoding="utf-8", errors="ignore")
            for m in IMAGE_RE.finditer(text):
                raw = m.group(1).strip().split()[0].split("?")[0]
                if not raw.startswith("http"):
                    rp = (p.parent / raw).resolve()
                    refs.setdefault(rp, set()).add(p)
        elif p.is_dir():
            for md in p.rglob("*.md"):
                text = md.read_text(encoding="utf-8", errors="ignore")
                for m in IMAGE_RE.finditer(text):
                    raw = m.group(1).strip().split()[0].split("?")[0]
                    if not raw.startswith("http"):
                        rp = (md.parent / raw).resolve()
                        refs.setdefault(rp, set()).add(md)

    on_disk = collect_image_files(scan_dirs)
    referenced = set(refs.keys())

    missing = [p for p in referenced if not p.is_file()]
    orphan = [p for p in on_disk if p not in referenced]
    large = [p for p in on_disk if p.stat().st_size > large_kb * 1024]

    print("=== Image audit ===")
    if missing:
        print(f"\n❌ Referenced but missing ({len(missing)}):")
        for p in sorted(missing)[:20]:
            print(f"  {p.relative_to(ROOT)}")
    else:
        print("\n✅ No missing referenced images under scan dirs")

    if orphan:
        print(f"\n⚠️  Unreferenced files ({len(orphan)}) — review before delete:")
        for p in sorted(orphan)[:15]:
            print(f"  {p.relative_to(ROOT)}")
        if len(orphan) > 15:
            print(f"  ... and {len(orphan) - 15} more")

    if large:
        print(f"\n⚠️  Large files (>{large_kb}KB, {len(large)}):")
        for p in sorted(large, key=lambda x: -x.stat().st_size)[:10]:
            kb = p.stat().st_size // 1024
            print(f"  {kb:5d} KB  {p.relative_to(ROOT)}")

    if args.compress:
        saved = 0
        for p in on_disk:
            if p.suffix.lower() == ".png":
                saved += try_compress(p)
        print(f"\n💾 Compress saved ~{saved // 1024} KB total")

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
