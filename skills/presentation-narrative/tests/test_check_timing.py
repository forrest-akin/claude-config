"""Runs scripts/check_timing.py over a synthetic outline and broken copies of it."""
import os
import subprocess
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "check_timing.py")
OUTLINE = """# Talk

Intro prose.

| Time | Minutes | Beat |
|---|---|---|
| 0-2 | 2 | Hook |
| 2-5 | 3 | Problem |
| 5-15 | 10 | Body |

## Beat 1 (0-2, 2 min)
"""


def check(text, window="15"):
    path = os.path.join(tempfile.mkdtemp(), "outline.md")
    with open(path, "w") as f:
        f.write(text)
    out = subprocess.run(["python3", SCRIPT, path, "--window", window], capture_output=True, text=True)
    return out.stdout, out.returncode


class CheckTiming(unittest.TestCase):
    def test_passing_outline_is_silent(self):
        self.assertEqual(check(OUTLINE), ("", 0))

    def test_duration_that_disagrees_with_its_range(self):
        self.assertEqual(check(OUTLINE.replace("| 2-5 | 3 |", "| 2-5 | 4 |"), window="16"),
                         ("2-5: 4 min, range is 3\n", 1))

    def test_gap_between_ranges(self):
        self.assertEqual(check(OUTLINE.replace("| 5-15 | 10 |", "| 6-15 | 9 |"), window="14"),
                         ("gap: 5 to 6\n", 1))

    def test_row_without_a_range_is_skipped(self):
        self.assertEqual(check(OUTLINE.replace("| 5-15 | 10 | Body |\n", "| 5-15 | 10 | Body |\n| Total | 15 | |\n")), ("", 0))

    def test_fractional_minutes_are_compared_to_the_range(self):
        self.assertEqual(check(OUTLINE.replace("| 0-2 | 2 |", "| 0-2 | 1.5 |")),
                         ("0-2: 1.5 min, range is 2\ntotal 14.5 min, window 15\n", 1))

    def test_minutes_cell_that_is_not_a_number_is_one_finding(self):
        self.assertEqual(check(OUTLINE.replace("| 0-2 | 2 |", "| 0-2 | two |")), ("0-2: minutes \"two\" is not a number\ntotal 13 min, window 15\n", 1))

    def test_table_without_a_minutes_column_is_one_finding(self):
        self.assertEqual(check(OUTLINE.replace("| Minutes |", "| Length |")), ("timing table has no min column\n", 1))

    def test_total_that_misses_the_window(self):
        self.assertEqual(check(OUTLINE, window="20"), ("total 15 min, window 20\n", 1))

    def test_missing_table_or_unreadable_outline_is_one_finding(self):
        self.assertEqual(check("# Talk\n\nNo table.\n"), ("no start-end timing table\n", 1))
        out = subprocess.run(["python3", SCRIPT, "/nonexistent/outline.md", "--window", "15"], capture_output=True, text=True)
        self.assertEqual((out.stdout, out.returncode), ("cannot read /nonexistent/outline.md\n", 1))
