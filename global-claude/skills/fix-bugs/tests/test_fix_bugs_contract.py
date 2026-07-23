#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import unittest
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fix_bugs_contract.py"
spec = importlib.util.spec_from_file_location("fix_bugs_contract", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class FixBugsContractTests(unittest.TestCase):
    def issue(self, number, labels, created="2026-01-01T00:00:00Z", state="OPEN"):
        return module.Issue(number, f"Issue {number}", state, tuple(labels), created)

    def test_01_omitted_argument_defaults_to_one(self):
        self.assertEqual(1, module.parse_maximum([]))

    def test_02_positive_integer_is_valid(self):
        self.assertEqual(5, module.parse_maximum(["5"]))

    def test_03_zero_is_rejected(self):
        with self.assertRaises(module.ContractError):
            module.parse_maximum(["0"])

    def test_04_negative_is_rejected(self):
        with self.assertRaises(module.ContractError):
            module.parse_maximum(["-2"])

    def test_05_decimal_is_rejected(self):
        with self.assertRaises(module.ContractError):
            module.parse_maximum(["2.5"])

    def test_06_text_is_rejected(self):
        with self.assertRaises(module.ContractError):
            module.parse_maximum(["five"])

    def test_07_multiple_arguments_are_rejected(self):
        with self.assertRaises(module.ContractError):
            module.parse_maximum(["2", "4"])

    def test_08_above_cap_is_rejected(self):
        with self.assertRaises(module.ContractError):
            module.parse_maximum(["11"])

    def test_09_p2_orders_before_p3(self):
        selected = module.select_queue(
            [self.issue(1, ["bug", "P3"]), self.issue(2, ["bug", "P2"])], 2
        )
        self.assertEqual([2, 1], [item.number for item in selected])

    def test_10_oldest_first_within_priority(self):
        selected = module.select_queue(
            [
                self.issue(2, ["bug", "P2"], "2026-02-01T00:00:00Z"),
                self.issue(1, ["bug", "P2"], "2026-01-01T00:00:00Z"),
            ],
            2,
        )
        self.assertEqual([1, 2], [item.number for item in selected])

    def test_11_maximum_count_is_enforced(self):
        issues = [self.issue(i, ["bug", "P2"]) for i in range(1, 5)]
        self.assertEqual(2, len(module.select_queue(issues, 2)))

    def test_12_fewer_available_than_requested(self):
        self.assertEqual(1, len(module.select_queue([self.issue(1, ["bug", "P2"])], 5)))

    def test_13_no_eligible_issues(self):
        self.assertEqual([], module.select_queue([self.issue(1, ["enhancement", "P2"])], 5))

    def test_14_duplicate_is_excluded(self):
        self.assertEqual([], module.select_queue([self.issue(1, ["bug", "P2", "duplicate"])], 1))

    def test_15_closed_issue_is_excluded(self):
        self.assertEqual([], module.select_queue([self.issue(1, ["bug", "P2"], state="CLOSED")], 1))

    def test_16_non_bug_p2_is_excluded(self):
        self.assertEqual([], module.select_queue([self.issue(1, ["feature", "P2"])], 1))

    def test_17_bug_without_priority_is_excluded(self):
        self.assertEqual([], module.select_queue([self.issue(1, ["bug"])], 1))

    def test_18_label_variants_are_recognized(self):
        issues = [
            self.issue(1, ["type:bug", "priority:P2"]),
            self.issue(2, ["kind:bug", "priority/p3"]),
        ]
        self.assertEqual([1, 2], [item.number for item in module.select_queue(issues, 2)])

    def test_19_conflicting_priority_is_rejected(self):
        with self.assertRaises(module.ContractError):
            module.select_queue([self.issue(1, ["bug", "P2", "P3"])], 1)

    def test_20_processed_statuses_consume_slots(self):
        for status in module.PROCESSED_STATUSES:
            self.assertTrue(module.consumes_slot(status), status)
        self.assertFalse(module.consumes_slot("unselected"))


if __name__ == "__main__":
    unittest.main()
