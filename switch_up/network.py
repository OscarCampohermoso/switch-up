"""GitHub API client: query and download releases for Atmosphere and Hekate."""

from pathlib import Path
from typing import Optional

import requests
from rich.console import Console
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn

ATMOSPHERE_REPO = "Atmosphere-NX/Atmosphere"
HEKATE_REPO = "CTCaer/hekate"
GITHUB_API = "https://api.github.com"


def get_latest_release(repo: str) -> dict:
    """Fetch the latest release info from a GitHub repository."""
    url = f"{GITHUB_API}/repos/{repo}/releases/latest"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def get_atmosphere_latest() -> dict:
    """Fetch the latest Atmosphere release."""
    return get_latest_release(ATMOSPHERE_REPO)


def get_hekate_latest() -> dict:
    """Fetch the latest Hekate release."""
    return get_latest_release(HEKATE_REPO)


def find_zip_asset(release: dict) -> Optional[str]:
    """Find the .zip asset download URL in a release.

    Returns the URL of the first .zip asset, or None if not found.
    """
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if name.endswith(".zip"):
            return asset["browser_download_url"]
    return None


def download_asset(url: str, dest: Path, console: Console) -> Path:
    """Download an asset from a URL with a Rich progress bar.

    Returns the path of the downloaded file.
    """
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    filename = url.split("/")[-1]
    filepath = dest / filename

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    total = int(response.headers.get("content-length", 0))

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        DownloadColumn(),
        TransferSpeedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(f"Downloading {filename}", total=total)
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress.update(task, advance=len(chunk))

    return filepath
