"""Tests for upstream target-drift monitoring."""

import unittest
from datetime import date
from pathlib import Path

from src.init_deep.drift import (
    DriftWarning,
    TargetMeta,
    check_drift,
    format_drift_report,
    load_registry_meta,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "targets" / "registry.toml"


class TestLoadRegistryMeta(unittest.TestCase):
    def test_loads_all_targets(self):
        metas = load_registry_meta(REGISTRY_PATH)
        names = [m.name for m in metas]
        self.assertEqual(len(metas), 9)
        for expected in [
            "claude",
            "cline",
            "codex",
            "continue",
            "copilot",
            "cursor",
            "gemini",
            "roo",
            "windsurf",
        ]:
            self.assertIn(expected, names)

    def test_all_have_valid_dates(self):
        metas = load_registry_meta(REGISTRY_PATH)
        for meta in metas:
            self.assertIsInstance(meta.last_reviewed, date)

    def test_all_have_doc_urls(self):
        metas = load_registry_meta(REGISTRY_PATH)
        for meta in metas:
            self.assertTrue(
                meta.doc_url.startswith("https://"), f"{meta.name} missing doc_url"
            )

    def test_all_have_status(self):
        metas = load_registry_meta(REGISTRY_PATH)
        for meta in metas:
            self.assertIn(meta.status, ("stable", "beta", "legacy", "deprecated"))


class TestCheckDrift(unittest.TestCase):
    def _make_meta(self, name: str, reviewed: date) -> TargetMeta:
        return TargetMeta(
            name=name,
            doc_url=f"https://example.com/{name}",
            last_reviewed=reviewed,
            status="stable",
        )

    def test_recent_dates_no_warnings(self):
        today = date(2026, 4, 16)
        metas = [self._make_meta("test", date(2026, 4, 1))]
        warnings = check_drift(metas, threshold_days=90, today=today)
        self.assertEqual(warnings, [])

    def test_old_date_returns_warning(self):
        today = date(2026, 7, 10)
        metas = [self._make_meta("test", date(2026, 4, 1))]
        warnings = check_drift(metas, threshold_days=90, today=today)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].target, "test")
        self.assertEqual(warnings[0].days_since_review, 100)

    def test_threshold_days_parameter(self):
        today = date(2026, 4, 16)
        metas = [self._make_meta("test", date(2026, 4, 1))]
        # 15 days old, threshold 10 -> warning
        warnings = check_drift(metas, threshold_days=10, today=today)
        self.assertEqual(len(warnings), 1)
        # 15 days old, threshold 20 -> no warning
        warnings = check_drift(metas, threshold_days=20, today=today)
        self.assertEqual(warnings, [])

    def test_exactly_at_threshold_no_warning(self):
        today = date(2026, 7, 1)
        metas = [self._make_meta("test", date(2026, 4, 2))]
        # 90 days exactly — not > 90
        warnings = check_drift(metas, threshold_days=90, today=today)
        self.assertEqual(warnings, [])

    def test_multiple_targets_mixed(self):
        today = date(2026, 7, 10)
        metas = [
            self._make_meta("fresh", date(2026, 7, 1)),
            self._make_meta("stale", date(2026, 1, 1)),
        ]
        warnings = check_drift(metas, threshold_days=90, today=today)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0].target, "stale")


class TestFormatDriftReport(unittest.TestCase):
    def test_produces_readable_output(self):
        metas = [
            TargetMeta("claude", "https://example.com", date(2026, 4, 3), "stable", "Skills"),
            TargetMeta("cursor", "https://example.com", date(2026, 1, 1), "stable", "Rules"),
        ]
        warnings = [
            DriftWarning("cursor", 100, "https://example.com", "cursor last reviewed 100 days ago (threshold: 90)")
        ]
        report = format_drift_report(metas, warnings)
        self.assertIn("Target Platform Status:", report)
        self.assertIn("cursor", report)
        self.assertIn("1 target(s) need review", report)

    def test_no_warnings_message(self):
        metas = [
            TargetMeta("claude", "https://example.com", date(2026, 4, 3), "stable"),
        ]
        report = format_drift_report(metas, [])
        self.assertIn("All targets reviewed within threshold.", report)


class TestDataclassFrozen(unittest.TestCase):
    def test_target_meta_is_frozen(self):
        meta = TargetMeta("test", "https://example.com", date(2026, 1, 1), "stable")
        with self.assertRaises(AttributeError):
            meta.name = "changed"  # type: ignore[misc]

    def test_drift_warning_is_frozen(self):
        warning = DriftWarning("test", 100, "https://example.com", "msg")
        with self.assertRaises(AttributeError):
            warning.target = "changed"  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
