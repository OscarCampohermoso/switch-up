"""Tests for the utils module."""

import zipfile
from pathlib import Path

import pytest

from switch_up.utils import detect_sd_path, extract_zip, resolve_sd_path


class TestDetectSdPath:
    def test_detects_nintendo(self, tmp_path: Path) -> None:
        (tmp_path / "Nintendo").mkdir()
        assert detect_sd_path(tmp_path) is True

    def test_detects_bootloader(self, tmp_path: Path) -> None:
        (tmp_path / "bootloader").mkdir()
        assert detect_sd_path(tmp_path) is True

    def test_rejects_empty_directory(self, tmp_path: Path) -> None:
        assert detect_sd_path(tmp_path) is False

    def test_rejects_file(self, tmp_path: Path) -> None:
        f = tmp_path / "file.txt"
        f.write_text("not an SD")
        assert detect_sd_path(f) is False


class TestExtractZip:
    def test_extracts_correctly(self, sample_zip: Path) -> None:
        dest = extract_zip(sample_zip)
        assert (Path(dest) / "atmosphere" / "package3").is_file()
        assert (Path(dest) / "bootloader" / "update.bin").is_file()

    def test_error_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            extract_zip(tmp_path / "noexiste.zip")

    def test_error_not_a_zip(self, tmp_path: Path) -> None:
        fake = tmp_path / "fake.zip"
        fake.write_text("not a zip")
        with pytest.raises(ValueError, match="Not a valid ZIP"):
            extract_zip(fake)


class TestResolveSdPath:
    def test_provided_path(self, fake_sd: Path) -> None:
        assert resolve_sd_path(fake_sd) == fake_sd

    def test_path_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            resolve_sd_path(tmp_path / "no_existe")
