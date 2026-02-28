"""Tests for the core module."""

from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from switch_up.core import create_backup, install_zip, restore_backup, smart_merge


class TestCreateBackup:
    def test_backs_up_existing_files(self, fake_sd: Path, tmp_path: Path) -> None:
        with patch("switch_up.core.BACKUP_DIR", tmp_path / "backups"):
            backup = create_backup(fake_sd)
        assert (Path(backup) / "hekate_ipl.ini").is_file()
        assert (Path(backup) / "exosphere.ini").is_file()
        assert (
            Path(backup) / "atmosphere" / "config" / "system_settings.ini"
        ).is_file()

    def test_backup_content_is_correct(self, fake_sd: Path, tmp_path: Path) -> None:
        with patch("switch_up.core.BACKUP_DIR", tmp_path / "backups"):
            backup = create_backup(fake_sd)
        assert (Path(backup) / "hekate_ipl.ini").read_text() == "autoboot=0\n"

    def test_sd_without_configs_does_not_fail(self, tmp_path: Path) -> None:
        sd = tmp_path / "empty_sd"
        sd.mkdir()
        with patch("switch_up.core.BACKUP_DIR", tmp_path / "backups"):
            backup = create_backup(sd)
        assert list(Path(backup).rglob("*")) == [] or all(
            p.is_dir() for p in Path(backup).rglob("*")
        )

    def test_backup_in_persistent_directory(self, fake_sd: Path, tmp_path: Path) -> None:
        backup_root = tmp_path / "backups"
        with patch("switch_up.core.BACKUP_DIR", backup_root):
            backup = create_backup(fake_sd)
        assert str(backup).startswith(str(backup_root))


class TestRestoreBackup:
    def test_restores_configs(self, fake_sd: Path, tmp_path: Path) -> None:
        with patch("switch_up.core.BACKUP_DIR", tmp_path / "backups"):
            backup = create_backup(fake_sd)
        (fake_sd / "hekate_ipl.ini").write_text("autoboot=1\n")
        restore_backup(backup, fake_sd)
        assert (fake_sd / "hekate_ipl.ini").read_text() == "autoboot=0\n"


class TestSmartMerge:
    def test_merge_preserves_user_files(
        self, fake_sd: Path, tmp_path: Path
    ) -> None:
        src = tmp_path / "update"
        src.mkdir()
        (src / "atmosphere").mkdir()
        (src / "atmosphere" / "package3").write_bytes(b"new_system_file")

        smart_merge(src, fake_sd)

        assert (fake_sd / "atmosphere" / "package3").read_bytes() == b"new_system_file"
        user_mod = (
            fake_sd / "atmosphere" / "contents"
            / "0100000000001000" / "romfs" / "user_mod.txt"
        )
        assert user_mod.is_file()
        assert user_mod.read_text() == "mi mod custom\n"

    def test_merge_overwrites_system_files(
        self, fake_sd: Path, tmp_path: Path
    ) -> None:
        src = tmp_path / "update"
        src.mkdir()
        (src / "hekate_ipl.ini").write_text("autoboot=2\n")

        smart_merge(src, fake_sd)
        assert (fake_sd / "hekate_ipl.ini").read_text() == "autoboot=2\n"


class TestInstallZip:
    def test_full_flow(self, fake_sd: Path, sample_zip: Path, tmp_path: Path) -> None:
        console = Console(quiet=True)
        with patch("switch_up.core.BACKUP_DIR", tmp_path / "backups"):
            install_zip(sample_zip, fake_sd, console)

        assert (fake_sd / "atmosphere" / "package3").is_file()
        assert (fake_sd / "bootloader" / "update.bin").is_file()

        user_mod = (
            fake_sd / "atmosphere" / "contents"
            / "0100000000001000" / "romfs" / "user_mod.txt"
        )
        assert user_mod.is_file()
