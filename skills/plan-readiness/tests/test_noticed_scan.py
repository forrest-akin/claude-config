"""Runs bin/noticed-scan in fixture repos with dated commits and checks its exact output."""
import datetime
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "bin", "noticed-scan")
RECENT = (datetime.date.today() - datetime.timedelta(days=30)).isoformat() + "T00:00:00"
OLD = "2020-01-02T00:00:00"
LEDGER = "# Noticed and left alone\n\n"
ENV = {"PATH": os.environ["PATH"], "HOME": os.environ["HOME"], "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


class Repo:
    def __init__(self):
        self.dir = tempfile.mkdtemp()
        self.git("init", "-q")

    def git(self, *args, date=RECENT):
        env = dict(ENV, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        subprocess.run(["git", *args], cwd=self.dir, env=env, check=True, capture_output=True)

    def commit(self, files, date=RECENT):
        for path, text in files.items():
            full = os.path.join(self.dir, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "c", date=date)

    def run(self, plan_text, *args, cwd=None):
        plan = os.path.join(tempfile.mkdtemp(), "plan.md")
        with open(plan, "w") as f:
            f.write(plan_text)
        return subprocess.run(["python3", SCRIPT, plan, *args], cwd=cwd or self.dir, env=ENV,
                              capture_output=True, text=True)


class NoticedScan(unittest.TestCase):
    def test_entry_for_a_file_the_plan_touches(self):
        repo = Repo()
        repo.commit({"src/a.py": "1\n"})
        repo.commit({"src/a.py": "2\n", ".claude/noticed.md": LEDGER + "- src/a.py:1 — long method — extract method — 2026-01-02\n"})
        out = repo.run("Edit `src/a.py`.\n")
        self.assertEqual((out.stdout, out.returncode), ("touched-file\t2\tsrc/a.py:1 — long method — extract method — 2026-01-02\n", 0))

    def test_entry_in_a_directory_the_plan_touches(self):
        repo = Repo()
        repo.commit({"src/a.py": "1\n", "src/b.py": "1\n", "lib/d.py": "1\n"})
        repo.commit({".claude/noticed.md": LEDGER + "- src/b.py:3 — feature envy — move method — 2026-01-02\n"
                     "- lib/d.py:1 — long method — extract method — 2026-01-02\n"})
        out = repo.run("Edit `src/a.py`.\n")
        self.assertEqual((out.stdout, out.returncode), ("touched-dir\t1\tsrc/b.py:3 — feature envy — move method — 2026-01-02\n", 0))

    def test_entry_at_the_root_when_the_plan_touches_a_root_file(self):
        repo = Repo()
        repo.commit({"README.md": "1\n", "install.sh": "1\n", "src/a.py": "1\n"})
        repo.commit({".claude/noticed.md": LEDGER + "- install.sh:3 — long method — extract method — 2026-01-02\n"})
        out = repo.run("Edit README.md and nothing else.\n")
        self.assertEqual((out.stdout, out.returncode), ("touched-dir\t1\tinstall.sh:3 — long method — extract method — 2026-01-02\n", 0))

    def test_entry_in_a_touched_directory_with_no_commit_this_year_is_a_delete(self):
        repo = Repo()
        repo.commit({"src/a.py": "1\n", "src/c.py": "1\n"}, date=OLD)
        repo.commit({"src/a.py": "2\n", ".claude/noticed.md": LEDGER + "- src/c.py:2 — dead code — delete — 2020-01-02\n"})
        out = repo.run("Edit `src/a.py`.\n")
        self.assertEqual((out.stdout, out.returncode), ("delete\t0\tsrc/c.py:2 — dead code — delete — 2020-01-02\n", 0))

    def test_rows_sorted_by_count_highest_first(self):
        repo = Repo()
        repo.commit({"src/a.py": "1\n", "src/b.py": "1\n"})
        repo.commit({"src/b.py": "2\n"})
        repo.commit({".claude/noticed.md": LEDGER + "- src/a.py:1 — long method — extract method — 2026-01-02\n"
                     "- src/b.py:3 — feature envy — move method — 2026-01-02\n"})
        out = repo.run("Edit `src/a.py`.\n")
        self.assertEqual(out.stdout, "touched-dir\t2\tsrc/b.py:3 — feature envy — move method — 2026-01-02\n"
                                     "touched-file\t1\tsrc/a.py:1 — long method — extract method — 2026-01-02\n")

    def test_no_ledger_prints_nothing(self):
        repo = Repo()
        repo.commit({"src/a.py": "1\n"})
        out = repo.run("Edit `src/a.py`.\n")
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "", 0))

    def test_missing_plan_prints_usage(self):
        out = subprocess.run(["python3", SCRIPT], cwd=Repo().dir, env=ENV, capture_output=True, text=True)
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "usage: noticed-scan <plan> [repo]\n", 2))

    def test_outside_a_git_repo_is_an_error(self):
        out = Repo().run("Edit `src/a.py`.\n", cwd=tempfile.mkdtemp())
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "error: not a git repository\n", 2))

    def test_unreadable_plan_is_an_error(self):
        repo = Repo()
        missing = os.path.join(repo.dir, "nope.md")
        out = subprocess.run(["python3", SCRIPT, missing], cwd=repo.dir, env=ENV, capture_output=True, text=True)
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", f"error: cannot read {missing}\n", 2))

    def test_repo_argument_overrides_the_current_directory(self):
        repo = Repo()
        repo.commit({"src/a.py": "1\n", ".claude/noticed.md": LEDGER + "- src/a.py:1 — long method — extract method — 2026-01-02\n"})
        out = repo.run("Edit `src/a.py`.\n", repo.dir, cwd=tempfile.mkdtemp())
        self.assertEqual((out.stdout, out.returncode), ("touched-file\t1\tsrc/a.py:1 — long method — extract method — 2026-01-02\n", 0))


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
        done = subprocess.run([sys.executable, "-m", "unittest", "test_noticed_scan.NoticedScan"], cwd=HERE,
                              env=dict(os.environ, GIT_DIR=decoy, GIT_WORK_TREE=worktree, PYTHONDONTWRITEBYTECODE="1"),
                              capture_output=True, text=True)
        self.assertEqual(changed(before, snapshot(decoy, worktree)), [])
        self.assertEqual(done.returncode, 0, done.stderr)

