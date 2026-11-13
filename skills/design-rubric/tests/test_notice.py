"""Runs bin/notice in a temp directory and checks the ledger it leaves."""
import datetime
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "bin", "notice")
TODAY = datetime.date.today().isoformat()
HEADING = "# Noticed and left alone\n\n"
ENV = {"PATH": os.environ["PATH"], "HOME": os.environ["HOME"]}


def repo():
    path = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", path], env=ENV, check=True)
    return path


def run(cwd, *args):
    return subprocess.run(["python3", SCRIPT, *args], cwd=cwd, env=ENV, capture_output=True, text=True)


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


def decoy_repo():
    decoy, worktree = tempfile.mkdtemp(), tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", "--bare", decoy], env=ENV, check=True)
    return decoy, worktree


def snapshot(*roots):
    files = {}
    for root in roots:
        for parent, _, names in os.walk(root):
            for name in names:
                with open(os.path.join(parent, name), "rb") as f:
                    files[os.path.join(parent, name)] = f.read()
    return files


def changed(before, after):
    return sorted(path for path in set(before) | set(after) if before.get(path) != after.get(path))


class InheritedGitDir(unittest.TestCase):
    def test_a_git_dir_in_the_callers_environment_is_left_untouched(self):
        decoy, worktree = decoy_repo()
        before = snapshot(decoy, worktree)
        done = subprocess.run([sys.executable, "-m", "unittest", "test_notice.Notice"], cwd=HERE,
                              env=dict(os.environ, GIT_DIR=decoy, GIT_WORK_TREE=worktree, PYTHONDONTWRITEBYTECODE="1"),
                              capture_output=True, text=True)
        self.assertEqual(changed(before, snapshot(decoy, worktree)), [])
        self.assertEqual(done.returncode, 0, done.stderr)


if __name__ == "__main__":
    unittest.main()
