"""Core logic: config backup, Smart Merge, and restoration."""

import shutil
from datetime import datetime
from pathlib import Path

from rich.console import Console

from switch_up.cleaner import clean_macos_junk, remove_xattrs
from switch_up.utils import extract_zip

# Critical files that are backed up before any operation
BACKUP_FILES = [
    "hekate_ipl.ini",
    "exosphere.ini",
    "bootloader/hekate_ipl.ini",
    "atmosphere/config/system_settings.ini",
]


BACKUP_DIR = Path.home() / ".switch-up" / "backups"


def create_backup(sd_path: Path) -> Path:
    """Create a backup of critical configuration files.

    Backups are saved to ~/.switch-up/backups/ with a timestamp.
    Returns the path of the backup directory.
    """
    sd_path = Path(sd_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_DIR / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    for relpath in BACKUP_FILES:
        source = sd_path / relpath
        if source.is_file():
            dest = backup_dir / relpath
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)

    return backup_dir


def restore_backup(backup_dir: Path, sd_path: Path) -> None:
    """Restore configuration files from a backup."""
    backup_dir = Path(backup_dir)
    sd_path = Path(sd_path)

    for relpath in BACKUP_FILES:
        source = backup_dir / relpath
        if source.is_file():
            dest = sd_path / relpath
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)


def smart_merge(src: Path, dst: Path) -> None:
    """Merge the contents of src into dst without deleting existing files.

    Uses shutil.copytree with dirs_exist_ok=True so that files from
    the ZIP update those on the SD, but files not in the ZIP are
    preserved intact (mods, cheats, user configs).
    """
    shutil.copytree(src, dst, dirs_exist_ok=True)


def install_zip(zip_path: Path, sd_path: Path, console: Console) -> None:
    """Full installation process: backup -> extract -> merge -> clean.

    Orchestrates the entire ZIP installation flow to the SD card.
    If anything fails during the merge, the backup is automatically restored.
    """
    sd_path = Path(sd_path)
    zip_path = Path(zip_path)

    # 1. Backup
    console.print("[bold blue]>[/] Backing up configuration...")
    backup_dir = create_backup(sd_path)
    console.print(f"  Backup saved to: {backup_dir}")

    # 2. Extract
    console.print("[bold blue]>[/] Extracting ZIP...")
    extracted = extract_zip(zip_path)

    # 3. Smart Merge
    try:
        console.print("[bold blue]>[/] Merging files (Smart Merge)...")
        smart_merge(extracted, sd_path)
    except Exception as e:
        console.print(f"[bold red]x[/] Error during merge: {e}")
        console.print("[bold yellow]>[/] Restoring backup...")
        restore_backup(backup_dir, sd_path)
        console.print("[bold green]v[/] Backup restored successfully.")
        raise

    # 4. Clean macOS junk
    console.print("[bold blue]>[/] Cleaning macOS junk files...")
    removed = clean_macos_junk(sd_path)
    remove_xattrs(sd_path)
    console.print(f"  Removed {removed} junk files/folders.")

    # 5. Temp cleanup
    shutil.rmtree(extracted, ignore_errors=True)

    console.print("[bold green]v[/] Installation completed successfully.")
