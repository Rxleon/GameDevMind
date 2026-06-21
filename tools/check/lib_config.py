"""Load tools/config.yaml."""
from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "tools" / "config.yaml"


def load_config() -> dict:
    if yaml is None or not CONFIG_PATH.is_file():
        return _defaults()
    with CONFIG_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {**_defaults(), **data}


def _defaults() -> dict:
    return {
        "repo": {
            "mds_dir": "mds",
            "exports_dir": "exports",
            "images_dir": "images",
        },
        "check": {
            "leaf_doc_pattern": r"^\d+\.\d+\.\d+.+\.md$",
            "skip_filenames": ["阅读说明.md"],
            "skip_dir_names": ["topics"],
            "require_keywords": True,
            "require_tags": True,
            "warn_raw_true": True,
        },
        "images": {"scan_dirs": ["exports", "images"], "large_file_kb": 500},
    }
