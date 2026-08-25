#!/usr/bin/env python3
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "slopectomy.py"
spec = importlib.util.spec_from_file_location("slopectomy", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SlopectomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = module.load_rules(ROOT / "references" / "rules.json")

    def test_detects_a_cluster(self):
        text = "Не страх, не слабость, не привычка. Психика уже всё поняла. И этого достаточно."
        report = module.scan_text(text, "<test>", self.rules)
        ids = {item["rule_id"] for item in report["findings"]}
        self.assertIn("negative-triad", ids)
        self.assertIn("psyche-as-character", ids)
        self.assertIn("final-sentence", ids)
        self.assertGreaterEqual(report["category_count"], 3)

    def test_masks_code_and_urls(self):
        text = "`Психика уже всё поняла` https://example.com\n\nПсихика уже всё поняла"
        report = module.scan_text(text, "<test>", self.rules)
        matches = [item["match"] for item in report["findings"] if item["rule_id"] == "psyche-as-character"]
        self.assertEqual(matches, ["Психика уже всё поняла"])

    def test_plain_text_has_no_forced_verdict(self):
        report = module.scan_text("Проект завершён в срок.", "<test>", self.rules)
        self.assertEqual(report["category_count"], 0)
        self.assertFalse(report["findings"])

    def test_rules_are_valid_json(self):
        data = json.loads((ROOT / "references" / "rules.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["rules"]), 38)
        self.assertEqual(len({rule["id"] for rule in data["rules"]}), 38)


if __name__ == "__main__":
    unittest.main()
