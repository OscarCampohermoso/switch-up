# switch-up

![License](https://img.shields.io/badge/License-GPLv2-blue.svg)

A safe, automated SD card manager for Nintendo Switch homebrew on macOS.

## Why does this exist?

If you've ever updated your Switch's SD card from a Mac, you know the pain. macOS silently injects hidden files (`.DS_Store`, `._*` files, extended attributes) into every folder it touches. These invisible files **corrupt your SD card** and cause boot failures, black screens, and cryptic errors on the Switch.

On top of that, macOS Finder's "Replace" behavior is destructive — dragging a folder with the same name **deletes the original** instead of merging contents. This means a simple update can wipe out your saves, configurations, and installed homebrew apps.

**switch-up** automates the entire process safely:

1. **Backs up** your configuration files before touching anything
2. **Smart Merges** new files onto your SD without deleting existing content
3. **Cleans** all macOS junk files that would corrupt the SD card
4. **Restores** your backup automatically if anything goes wrong

## The Problem in Detail

| macOS Behavior | What Happens on Switch | switch-up Fix |
|---|---|---|
| Finder replaces folders instead of merging | Your configs, homebrew apps, and settings get deleted | Smart Merge with `dirs_exist_ok=True` preserves everything |
| `.DS_Store` and `._*` files injected everywhere | Switch reads them as corrupted data, fails to boot | Recursive cleanup of all macOS metadata files |
| Extended attributes (xattr) added to files | Hekate and Atmosphere misread files, throw errors | `xattr -cr` strips all extended attributes |
| `__MACOSX/` folders from ZIP extraction | Junk folders confuse the Switch bootloader | Automatic removal during cleanup |

## Installation

### From PyPI

```bash
pip install switch-up
```

### From source

```bash
git clone https://github.com/yourusername/switch-up.git
cd switch-up
pip install -e .
```

## Requirements

- Python 3.8 or higher
- macOS (designed specifically for macOS-related SD card issues)

## Usage

### Update Atmosphere and Hekate to the latest version

Downloads the latest releases from GitHub and installs them safely to your SD card.

```bash
switch-up update --latest
```

The tool will auto-detect your SD card if it's mounted at `/Volumes/`. If you have multiple SD cards or a custom mount point, specify the path:

```bash
switch-up update --latest --sd-path /Volumes/MY_SD
```

### Update only Atmosphere (skip Hekate)

```bash
switch-up update --latest --ams-only
```

### Install a local ZIP file

If you already downloaded a release ZIP manually:

```bash
switch-up install ./atmosphere-1.8.0.zip --sd-path /Volumes/MY_SD
```

### Clean macOS junk files only (no update)

Just remove the hidden files macOS left behind, without updating anything:

```bash
switch-up fix-archive-bit /Volumes/MY_SD
```

## What happens during an update?

```
1. Backup     → Saves hekate_ipl.ini, exosphere.ini, and other configs
                 to ~/.switch-up/backups/ (timestamped)
2. Extract    → Unpacks the ZIP to a temporary directory
3. Smart Merge → Copies new files to SD, preserving your existing content
4. Cleanup    → Removes .DS_Store, ._* files, __MACOSX/, and xattrs
5. Done       → If anything fails at step 3, your backup is auto-restored
```

## Configuration Backups

Before every operation, switch-up saves your critical config files to:

```
~/.switch-up/backups/20260227_143000/
├── hekate_ipl.ini
├── exosphere.ini
├── bootloader/hekate_ipl.ini
└── atmosphere/config/system_settings.ini
```

These backups persist across sessions so you can always recover your settings.

## Commands Reference

| Command | Description |
|---|---|
| `switch-up update --latest` | Download and install the latest Atmosphere + Hekate |
| `switch-up update --latest --ams-only` | Download and install only Atmosphere |
| `switch-up install <zip>` | Install a local ZIP file to the SD card |
| `switch-up fix-archive-bit [path]` | Clean macOS junk files from the SD card |
| `switch-up --version` | Show the current version |
| `switch-up --help` | Show help for all commands |

## License

GPLv3 — See [LICENSE](LICENSE) for details.
