"""macOS sanitizer: removal of ghost files and extended attributes."""

import os
import shutil
import subprocess
from pathlib import Path


def clean_macos_junk(path: Path) -> int:
    """Recursively remove junk files that macOS injects into the SD card.

    Removes:
    - ._* files (resource fork metadata, ~4KB each)
    - .DS_Store (Finder's visual index)
    - __MACOSX/ directories (created when extracting with Archive Utility)

    Returns the number of items removed.
    """
    path = Path(path)
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    removed = 0

    for root, dirs, files in os.walk(path, topdown=False):
        root_path = Path(root)

        # Remove ._* and .DS_Store files
        for fname in files:
            if fname.startswith("._") or fname == ".DS_Store":
                target = root_path / fname
                target.unlink()
                removed += 1

        # Remove __MACOSX directories
        for dname in dirs:
            if dname == "__MACOSX":
                target = root_path / dname
                shutil.rmtree(target)
                removed += 1

    return removed


def remove_xattrs(path: Path) -> int:
    """Remove extended attributes from all files in the given path.

    Uses the xattr -cr command to clean recursively.
    Returns 0 on success, or the process return code on failure.
    """
    path = Path(path)
    if not path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")

    result = subprocess.run(
        ["xattr", "-cr", str(path)],
        capture_output=True,
        text=True,
    )
    return result.returncode
