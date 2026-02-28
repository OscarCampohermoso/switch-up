"""Tests for the cleaner module."""

from pathlib import Path

import pytest

from switch_up.cleaner import clean_macos_junk


class TestCleanMacosJunk:
    def test_removes_ds_store(self, fake_sd_with_junk: Path) -> None:
        clean_macos_junk(fake_sd_with_junk)
        ds_files = list(fake_sd_with_junk.rglob(".DS_Store"))
        assert len(ds_files) == 0

    def test_removes_dot_underscore(self, fake_sd_with_junk: Path) -> None:
        clean_macos_junk(fake_sd_with_junk)
        dot_files = list(fake_sd_with_junk.rglob("._*"))
        assert len(dot_files) == 0

    def test_removes_macosx_dir(self, fake_sd_with_junk: Path) -> None:
        clean_macos_junk(fake_sd_with_junk)
        assert not (fake_sd_with_junk / "__MACOSX").exists()

    def test_returns_correct_count(self, fake_sd_with_junk: Path) -> None:
        # 2x .DS_Store + 2x ._* + 1x ._ignored (inside __MACOSX) + 1x __MACOSX = 6
        removed = clean_macos_junk(fake_sd_with_junk)
        assert removed == 6

    def test_preserves_normal_files(self, fake_sd_with_junk: Path) -> None:
        clean_macos_junk(fake_sd_with_junk)
        mod_file = (
            fake_sd_with_junk / "atmosphere" / "contents"
            / "0100000000001000" / "romfs" / "user_mod.txt"
        )
        assert mod_file.is_file()
        assert mod_file.read_text() == "mi mod custom\n"

    def test_error_if_not_directory(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("test")
        with pytest.raises(NotADirectoryError):
            clean_macos_junk(f)

    def test_clean_directory_returns_zero(self, fake_sd: Path) -> None:
        removed = clean_macos_junk(fake_sd)
        assert removed == 0
