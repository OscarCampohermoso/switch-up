"""CLI entry point. Defines commands with Typer and orchestrates modules."""

import shutil
import tempfile
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from switch_up import __version__
from switch_up.cleaner import clean_macos_junk, remove_xattrs
from switch_up.core import install_zip
from switch_up.network import (
    download_asset,
    find_zip_asset,
    get_atmosphere_latest,
    get_hekate_latest,
)
from switch_up.utils import resolve_sd_path

app = typer.Typer(
    name="switch-up",
    help="A secure Nintendo Switch updater for macOS.",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"switch-up v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """switch-up: A secure Nintendo Switch updater for macOS."""


@app.command()
def update(
    sd_path: Optional[Path] = typer.Option(
        None, "--sd-path", "-s", help="Path to the Switch SD card."
    ),
    latest: bool = typer.Option(
        False, "--latest", "-l", help="Download and install the latest version."
    ),
    ams_only: bool = typer.Option(
        False, "--ams-only", help="Only update Atmosphere (skip Hekate)."
    ),
) -> None:
    """Download and install the latest versions of Atmosphere and Hekate."""
    try:
        sd = resolve_sd_path(sd_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(1)

    console.print(f"[bold]SD detected:[/] {sd}\n")
    tmp_dir = Path(tempfile.mkdtemp(prefix="switch_up_dl_"))

    try:
        # Atmosphere
        console.print("[bold cyan]== Atmosphere ==[/]")
        ams_release = get_atmosphere_latest()
        ams_version = ams_release.get("tag_name", "unknown")
        console.print(f"Latest version: {ams_version}")

        ams_url = find_zip_asset(ams_release)
        if not ams_url:
            console.print("[bold red]x[/] No .zip found in the release.")
            raise typer.Exit(1)

        ams_zip = download_asset(ams_url, tmp_dir, console)
        install_zip(ams_zip, sd, console)
        console.print()

        # Hekate
        if not ams_only:
            console.print("[bold cyan]== Hekate ==[/]")
            hek_release = get_hekate_latest()
            hek_version = hek_release.get("tag_name", "unknown")
            console.print(f"Latest version: {hek_version}")

            hek_url = find_zip_asset(hek_release)
            if not hek_url:
                console.print("[bold red]x[/] No .zip found in the release.")
                raise typer.Exit(1)

            hek_zip = download_asset(hek_url, tmp_dir, console)
            install_zip(hek_zip, sd, console)

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[bold red]Unexpected error:[/] {e}")
            raise typer.Exit(1)
        raise
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    console.print("\n[bold green]Update completed![/]")


@app.command(name="fix-archive-bit")
def fix_archive_bit(
    sd_path: Optional[Path] = typer.Argument(
        None, help="Path to the Switch SD card."
    ),
) -> None:
    """Clean macOS junk files without updating anything."""
    try:
        sd = resolve_sd_path(sd_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(1)

    console.print(f"[bold]SD detected:[/] {sd}\n")
    console.print("[bold blue]>[/] Cleaning macOS junk files...")

    removed = clean_macos_junk(sd)
    xattr_rc = remove_xattrs(sd)

    console.print(f"  Removed {removed} junk files/folders.")
    if xattr_rc == 0:
        console.print("  Extended attributes cleaned successfully.")
    else:
        console.print("[yellow]  Warning: could not clean some xattrs.[/]")

    console.print("\n[bold green]Cleanup completed![/]")


@app.command()
def install(
    zip_path: Path = typer.Argument(..., help="Path to the .zip file to install."),
    sd_path: Optional[Path] = typer.Option(
        None, "--sd-path", "-s", help="Path to the Switch SD card."
    ),
) -> None:
    """Install a local ZIP file to the Switch SD card."""
    try:
        sd = resolve_sd_path(sd_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise typer.Exit(1)

    if not zip_path.is_file():
        console.print(f"[bold red]Error:[/] File not found: {zip_path}")
        raise typer.Exit(1)

    console.print(f"[bold]SD detected:[/] {sd}")
    console.print(f"[bold]ZIP:[/] {zip_path}\n")

    install_zip(zip_path, sd, console)
    console.print("\n[bold green]Installation completed![/]")


if __name__ == "__main__":
    app()
