"""Helpers: ZIP extraction, automatic SD path detection, and validations."""

import tempfile
import zipfile
from pathlib import Path
from typing import List, Optional


# Markers that identify a Nintendo Switch SD card
SD_MARKERS = ("Nintendo", "bootloader")


def detect_sd_path(path: Path) -> bool:
    """Check if a path looks like a Nintendo Switch SD card.

    Looks for 'Nintendo/' or 'bootloader/' directories as indicators.
    """
    if not path.is_dir():
        return False
    for marker in SD_MARKERS:
        if (path / marker).is_dir():
            return True
    return False


def find_sd_volumes() -> List[Path]:
    """Scan /Volumes/ for mounted volumes that look like Switch SD cards."""
    volumes_dir = Path("/Volumes")
    if not volumes_dir.is_dir():
        return []
    results: List[Path] = []
    for volume in volumes_dir.iterdir():
        if volume.is_dir() and detect_sd_path(volume):
            results.append(volume)
    return results


def resolve_sd_path(sd_path: Optional[Path]) -> Path:
    """Resolve the SD path: use the one provided or try to auto-detect."""
    if sd_path is not None:
        path = Path(sd_path)
        if not path.is_dir():
            raise FileNotFoundError(f"Path does not exist: {path}")
        return path

    volumes = find_sd_volumes()
    if not volumes:
        raise FileNotFoundError(
            "No Switch SD card found mounted at /Volumes/. "
            "Use --sd-path to specify the path manually."
        )
    if len(volumes) > 1:
        names = ", ".join(str(v) for v in volumes)
        raise ValueError(
            f"Multiple SD cards found: {names}. "
            "Use --sd-path to specify which one to use."
        )
    return volumes[0]


def extract_zip(zip_path: Path, dest: Optional[Path] = None) -> Path:
    """Extract a ZIP file to a temporary directory or the specified destination.

    Returns the path where files were extracted.
    """
    zip_path = Path(zip_path)
    if not zip_path.is_file():
        raise FileNotFoundError(f"File not found: {zip_path}")
    if not zipfile.is_zipfile(zip_path):
        raise ValueError(f"Not a valid ZIP file: {zip_path}")

    if dest is None:
        dest = Path(tempfile.mkdtemp(prefix="switch_up_"))
    else:
        dest = Path(dest)
        dest.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest)

    return dest
