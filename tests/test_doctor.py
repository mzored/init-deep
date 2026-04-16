"""Tests for the doctor workspace health validator."""

import sys
import tempfile
import unittest
from pathlib import Path

# Ensure src is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# Ensure tools is importable (for build_v2 -> load_command chain)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.init_deep.doctor import (
    HealthCheck,
    _check_config,
    _check_python_version,
    _check_source_exists,
    _check_stale_legacy,
    format_doctor_output,
    run_doctor,
)


class TestHealthCheckDataclass(unittest.TestCase):
    def test_frozen(self):
        hc = HealthCheck("test", "ok", "msg")
        with self.assertRaises(AttributeError):
            hc.status = "error"  # type: ignore[misc]


class TestCheckPythonVersion(unittest.TestCase):
    def test_ok_on_current_python(self):
        check = _check_python_version()
        # We require 3.11+ to run this project, so this must be ok.
        self.assertEqual(check.status, "ok")
        self.assertIn(str(sys.version_info.major), check.message)


class TestCheckSourceExists(unittest.TestCase):
    def test_new_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source" / "commands" / "init-deep").mkdir(parents=True)
            (root / "source" / "commands" / "init-deep" / "spec.toml").write_text("")
            check = _check_source_exists(root)
            self.assertEqual(check.status, "ok")
            self.assertIn("New format", check.message)

    def test_legacy_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source" / "init-deep").mkdir(parents=True)
            (root / "source" / "init-deep" / "canonical.md").write_text("")
            check = _check_source_exists(root)
            self.assertEqual(check.status, "ok")
            self.assertIn("Legacy", check.message)

    def test_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            check = _check_source_exists(Path(tmp))
            self.assertEqual(check.status, "error")
            self.assertIn("No source", check.message)


class TestCheckConfig(unittest.TestCase):
    def test_no_config_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            checks = _check_config(Path(tmp))
            self.assertEqual(len(checks), 1)
            self.assertEqual(checks[0].status, "ok")
            self.assertIn("defaults", checks[0].message)


class TestCheckStaleLegacy(unittest.TestCase):
    def test_finds_stale_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".windsurfrules").write_text("")
            (root / ".clinerules").write_text("")
            checks = _check_stale_legacy(root)
            self.assertEqual(len(checks), 2)
            for c in checks:
                self.assertEqual(c.status, "warning")
                self.assertEqual(c.name, "stale-legacy")

    def test_clean_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            checks = _check_stale_legacy(Path(tmp))
            self.assertEqual(len(checks), 0)


class TestRunDoctor(unittest.TestCase):
    def test_actual_workspace_no_errors(self):
        """Run doctor on the real workspace and ensure no errors."""
        checks = run_doctor(ROOT)
        errors = [c for c in checks if c.status == "error"]
        self.assertEqual(errors, [], f"Unexpected errors: {errors}")


class TestFormatDoctorOutput(unittest.TestCase):
    def test_readable_output(self):
        checks = [
            HealthCheck("py", "ok", "Python 3.12"),
            HealthCheck("src", "warning", "Legacy format"),
            HealthCheck("cfg", "error", "Bad parse"),
        ]
        output = format_doctor_output(checks)
        self.assertIn("[+] py", output)
        self.assertIn("[!] src", output)
        self.assertIn("[x] cfg", output)
        self.assertIn("1 error(s), 1 warning(s)", output)

    def test_no_issues(self):
        checks = [HealthCheck("a", "ok", "fine")]
        output = format_doctor_output(checks)
        self.assertIn("0 error(s), 0 warning(s)", output)


if __name__ == "__main__":
    unittest.main()
