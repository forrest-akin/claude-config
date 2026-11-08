"""Runs bin/notice in a temp directory and checks the ledger it leaves."""
import datetime
import os
import subprocess
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "notice")
TODAY = datetime.date.today().isoformat()
HEADING = "# Noticed and left alone\n\n"


def repo():
    path = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", path], check=True)
    return path


def run(cwd, *args):
    return subprocess.run(["python3", SCRIPT, *args], cwd=cwd, capture_output=True, text=True)


def ledger(cwd):
    with open(os.path.join(cwd, ".claude", "noticed.md")) as f:
        return f.read()


class Notice(unittest.TestCase):
    def test_missing_ledger_is_created_with_its_heading(self):
        cwd = repo()
        out = run(cwd, "src/app.rs:12", "Large method", "Extract Function")
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(ledger(cwd), HEADING + f"- src/app.rs:12 — Large method — Extract Function — {TODAY}\n")

    def test_existing_ledger_gains_one_line(self):
        cwd = repo()
        os.makedirs(os.path.join(cwd, ".claude"))
        earlier = HEADING + "- a.ts:3 — Excess arguments — Introduce Parameter Object — 2026-01-02\n"
        with open(os.path.join(cwd, ".claude", "noticed.md"), "w") as f:
            f.write(earlier)
        run(cwd, "b.ts:9", "Nested complexity", "Replace Nested Conditional with Guard Clauses")
        self.assertEqual(ledger(cwd), earlier
                         + f"- b.ts:9 — Nested complexity — Replace Nested Conditional with Guard Clauses — {TODAY}\n")

    def test_wrong_argument_count_prints_usage_and_writes_nothing(self):
        cwd = repo()
        out = run(cwd, "a.rs:1", "Large method")
        self.assertEqual((out.returncode, out.stderr.startswith("usage: notice <path:line>")), (2, True), out.stderr)
        self.assertFalse(os.path.exists(os.path.join(cwd, ".claude")))

    def test_location_without_a_line_prints_usage_and_writes_nothing(self):
        cwd = repo()
        out = run(cwd, "src/app.rs", "Large method", "Extract Function")
        self.assertEqual((out.returncode, out.stderr.startswith("usage: notice <path:line>")), (2, True), out.stderr)
        self.assertFalse(os.path.exists(os.path.join(cwd, ".claude")))

    def test_run_from_a_subdirectory_writes_at_the_repo_top_level(self):
        top = repo()
        os.makedirs(os.path.join(top, "src"))
        run(os.path.join(top, "src"), "src/app.rs:12", "Large method", "Extract Function")
        self.assertEqual(ledger(top), HEADING + f"- src/app.rs:12 — Large method — Extract Function — {TODAY}\n")

    def test_outside_a_git_repo_is_an_error(self):
        cwd = tempfile.mkdtemp()
        out = run(cwd, "a.rs:1", "Large method", "Extract Function")
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "error: not a git repository\n", 2))


if __name__ == "__main__":
    unittest.main()
