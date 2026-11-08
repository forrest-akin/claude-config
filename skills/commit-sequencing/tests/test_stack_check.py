"""Runs bin/stack-check over a temp repo with one fixture commit per flag."""
import os
import subprocess
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "stack-check")
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


class Repo:
    def __init__(self):
        self.dir = tempfile.mkdtemp()
        self.git("init", "-q")
        self.commit("base", {"README.md": "x\n"})
        self.base = self.git("rev-parse", "HEAD")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.dir, env=ENV, check=True,
                              capture_output=True, text=True).stdout.strip()

    def commit(self, subject, files):
        for path, text in files.items():
            with open(os.path.join(self.dir, path), "w") as f:
                f.write(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", subject)
        return self.git("rev-parse", "--short", "HEAD")

    def run(self, *args):
        return subprocess.run(["python3", SCRIPT, *args], cwd=self.dir, capture_output=True, text=True)


def lines(n):
    return "".join(f"line {i}\n" for i in range(n))


class StackCheck(unittest.TestCase):
    def test_commit_past_300_lines_is_flagged(self):
        repo = Repo()
        sha = repo.commit("feat: big", {"a.py": lines(301)})
        out = repo.run(repo.base)
        self.assertEqual((out.stdout, out.returncode), (f"{sha}\tfeat: big\t1\t301\t0\t>300\ntotal\t301\t0\n", 0))

    def test_claude_lines_have_their_own_column_and_do_not_count_toward_300(self):
        repo = Repo()
        os.makedirs(os.path.join(repo.dir, ".claude", "plans"))
        sha = repo.commit("feat: planned", {"a.py": lines(10), ".claude/plans/p.md": lines(400)})
        out = repo.run(repo.base)
        self.assertEqual(out.stdout, f"{sha}\tfeat: planned\t2\t10\t400\t\ntotal\t10\t400\n")

    def test_placeholder_subject_is_flagged(self):
        for subject in ("WIP parser", "temp", "tmp: try", "fixup! feat: big", "Part 2 of parser"):
            with self.subTest(subject):
                repo = Repo()
                repo.commit("feat: real", {"b.py": lines(60)})
                sha = repo.commit(subject, {"a.py": lines(60)})
                out = repo.run(repo.base)
                self.assertEqual(out.stdout.splitlines()[1], f"{sha}\t{subject}\t1\t60\t0\tplaceholder")

    def test_subject_starting_with_a_longer_word_is_not_a_placeholder(self):
        repo = Repo()
        sha = repo.commit("Template engine for emails", {"a.py": lines(3)})
        self.assertEqual(repo.run(repo.base).stdout.splitlines()[0], f"{sha}\tTemplate engine for emails\t1\t3\t0\t")

    def test_stack_under_100_lines_asks_to_collapse(self):
        repo = Repo()
        repo.commit("feat: one", {"a.py": lines(40)})
        repo.commit("feat: two", {"b.py": lines(59)})
        self.assertEqual(repo.run(repo.base).stdout.splitlines()[-1], "total\t99\t0\tcollapse?")

    def test_single_commit_under_100_lines_is_not_asked_to_collapse(self):
        repo = Repo()
        repo.commit("feat: one", {"a.py": lines(40)})
        self.assertEqual(repo.run(repo.base).stdout.splitlines()[-1], "total\t40\t0")

    def test_unknown_base_is_an_error(self):
        out = Repo().run("nosuchref")
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "error: unknown BASE nosuchref\n", 2))

    def test_outside_a_git_repo_is_an_error(self):
        out = subprocess.run(["python3", SCRIPT, "HEAD"], cwd=tempfile.mkdtemp(), capture_output=True, text=True)
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "error: not a git repository\n", 2))

    def test_missing_base_prints_usage(self):
        out = Repo().run()
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "usage: stack-check BASE\n", 2))

    def test_binary_files_count_as_files_with_no_lines(self):
        repo = Repo()
        sha = repo.commit("feat: logo", {"a.py": lines(3), "logo.bin": "\0\1\2"})
        self.assertEqual(repo.run(repo.base).stdout.splitlines()[0], f"{sha}\tfeat: logo\t2\t3\t0\t")


if __name__ == "__main__":
    unittest.main()
