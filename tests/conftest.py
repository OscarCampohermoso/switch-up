"""Shared fixtures for switch-up tests."""

import zipfile
from pathlib import Path

import pytest


@pytest.fixture
def fake_sd(tmp_path: Path) -> Path:
    """Create a fake SD card structure with Switch markers."""
    sd = tmp_path / "SD"
    sd.mkdir()
    (sd / "Nintendo").mkdir()
    (sd / "bootloader").mkdir()
    (sd / "atmosphere").mkdir()
    (sd / "atmosphere" / "config").mkdir(parents=True)

    # Existing configs that should be preserved
    (sd / "hekate_ipl.ini").write_text("autoboot=0\n")
    (sd / "exosphere.ini").write_text("log_enabled=1\n")
    (sd / "atmosphere" / "config" / "system_settings.ini").write_text(
        "dmnt_cheats_enabled_by_default=1\n"
    )

    # Simulate user mods
    (sd / "atmosphere" / "contents").mkdir()
    user_mod = sd / "atmosphere" / "contents" / "0100000000001000"
    user_mod.mkdir(parents=True)
    (user_mod / "romfs").mkdir()
    (user_mod / "romfs" / "user_mod.txt").write_text("mi mod custom\n")

    return sd


@pytest.fixture
def fake_sd_with_junk(fake_sd: Path) -> Path:
    """Fake SD card with macOS junk files injected."""
    (fake_sd / ".DS_Store").write_bytes(b"\x00\x00\x00\x01")
    (fake_sd / "atmosphere" / ".DS_Store").write_bytes(b"\x00\x00\x00\x01")
    (fake_sd / "._somefile").write_bytes(b"\x00\x05\x16")
    (fake_sd / "atmosphere" / "._config").write_bytes(b"\x00\x05\x16")
    (fake_sd / "__MACOSX").mkdir()
    (fake_sd / "__MACOSX" / "._ignored").write_bytes(b"\x00")
    return fake_sd


@pytest.fixture
def sample_zip(tmp_path: Path) -> Path:
    """Create a sample ZIP simulating an Atmosphere update."""
    zip_content = tmp_path / "zip_content"
    zip_content.mkdir()

    # Simulate an Atmosphere release structure
    atm = zip_content / "atmosphere"
    atm.mkdir()
    (atm / "package3").write_bytes(b"new_package3_data")
    (atm / "config").mkdir()

    boot = zip_content / "bootloader"
    boot.mkdir()
    (boot / "update.bin").write_bytes(b"new_bootloader")

    zip_path = tmp_path / "atmosphere-update.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file in zip_content.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(zip_content))
    return zip_path
