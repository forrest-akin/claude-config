"""Runs bin/health-delta over before/after fixture pairs committed in temp repos."""
import os
import shutil
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "bin", "health-delta")
FIXTURES = os.path.join(HERE, "fixtures")
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


class Repo:
    def __init__(self):
        self.dir = tempfile.mkdtemp()
        self.git("init", "-q")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.dir, env=ENV, check=True, capture_output=True)

    def put(self, source, dest):
        shutil.copyfile(source, os.path.join(self.dir, dest))

    def run(self, *args, env=ENV, cwd=None):
        return subprocess.run(["python3", SCRIPT, *args], cwd=cwd or self.dir, env=env, capture_output=True, text=True)

    def commit_pair(self, before, after, dest):
        self.write(dest, before)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.write(dest, after)

    def write(self, dest, text):
        full = os.path.join(self.dir, dest)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)


def delta(case, ext, env=ENV):
    repo = Repo()
    repo.put(os.path.join(FIXTURES, case, "before." + ext), "lib." + ext)
    repo.git("add", "-A")
    repo.git("commit", "-q", "-m", "base")
    repo.put(os.path.join(FIXTURES, case, "after." + ext), "lib." + ext)
    return repo.run(env=env)


class HealthDelta(unittest.TestCase):
    def assertReports(self, case, rows):
        for ext in ("rs", "ts"):
            with self.subTest(ext=ext):
                out = delta(case, ext)
                expected = "".join(f"lib.{ext}:{row}\n" for row in rows)
                self.assertEqual((out.stdout, out.stderr, out.returncode), (expected, "", 1 if rows else 0))

    def test_function_grown_past_30_lines_is_a_large_method(self):
        self.assertReports("large-method", ["1\ttotal\tLarge method\t7\t34\tExtract Function"])

    def test_function_past_7_branches_is_a_complex_method(self):
        self.assertReports("complex-method", ["1\tscore\tComplex method\t2\t9\tDecompose Conditional; Replace Conditional with Polymorphism"])

    def test_function_nested_past_2_levels_has_nested_complexity(self):
        self.assertReports("nested-complexity", ["1\tfirst\tNested complexity\t1\t3\tReplace Nested Conditional with Guard Clauses"])

    def test_fourth_parameter_is_excess_arguments(self):
        self.assertReports("excess-arguments", ["1\tsum\tExcess arguments\t3\t4\tIntroduce Parameter Object"])

    def test_function_under_an_accepted_smell_comment_is_skipped(self):
        self.assertReports("accepted-smell", [])

    def test_smell_the_diff_did_not_worsen_is_not_reported(self):
        self.assertReports("unchanged-smell", [])

    def test_new_function_past_a_threshold_is_reported_with_no_before(self):
        self.assertReports("new-function", ["5\textra\tExcess arguments\t-\t4\tIntroduce Parameter Object"])

    def test_run_from_a_subdirectory_measures_files_named_from_the_top_level(self):
        repo = Repo()
        with open(os.path.join(FIXTURES, "excess-arguments", "before.rs")) as f, \
                open(os.path.join(FIXTURES, "excess-arguments", "after.rs")) as g:
            repo.commit_pair(f.read(), g.read(), "src/lib.rs")
        out = repo.run(cwd=os.path.join(repo.dir, "src"))
        self.assertEqual((out.stdout, out.stderr, out.returncode),
                         ("src/lib.rs:1\tsum\tExcess arguments\t3\t4\tIntroduce Parameter Object\n", "", 1))

    def test_same_named_functions_are_compared_in_order(self):
        repo = Repo()
        impls = "struct A;\nimpl A {\n    fn new(%s) -> A { A }\n}\nstruct B;\nimpl B {\n    fn new(a: i32) -> B { B }\n}\n"
        repo.commit_pair(impls % "a: i32", impls % "a: i32, b: i32, c: i32, d: i32", "lib.rs")
        out = repo.run()
        self.assertEqual((out.stdout, out.stderr, out.returncode),
                         ("lib.rs:3\tnew\tExcess arguments\t1\t4\tIntroduce Parameter Object\n", "", 1))

    def test_extensionless_python_script_is_measured_by_its_shebang(self):
        repo = Repo()
        script = "#!/usr/bin/env python3\ndef f(%s):\n    return 1\n"
        repo.commit_pair(script % "a", script % "a, b, c, d", "bin/tool")
        out = repo.run()
        self.assertEqual((out.stdout, out.stderr, out.returncode),
                         ("bin/tool:2\tf\tExcess arguments\t1\t4\tIntroduce Parameter Object\n", "", 1))

    def test_extensionless_file_lizard_cannot_read_is_listed_as_unread(self):
        repo = Repo()
        repo.commit_pair("#!/bin/bash\necho 1\n", "#!/bin/bash\necho 2\n", "bin/tool")
        out = repo.run()
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("unread:\nbin/tool\n", "", 0))

    def test_lizard_installed_by_mise_is_found_without_either_on_path(self):
        home = tempfile.mkdtemp()
        bindir = os.path.join(home, ".local", "bin")
        os.makedirs(bindir)
        lizard = os.path.join(home, "lizard")
        for path, text in ((os.path.join(bindir, "mise"), f"#!/bin/sh\necho {lizard}\n"), (lizard, "#!/bin/sh\n")):
            with open(path, "w") as f:
                f.write(text)
            os.chmod(path, 0o755)
        out = delta("large-method", "rs", env=dict(ENV, PATH="/usr/bin:/bin", HOME=home))
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "", 0))

    def test_missing_lizard_warns_and_exits_0(self):
        out = delta("large-method", "rs", env=dict(ENV, PATH="/usr/bin:/bin", HOME=tempfile.mkdtemp()))
        self.assertEqual((out.stdout, out.stderr, out.returncode),
                         ("", "warning: lizard not found; health-delta skipped\n", 0))

    def test_outside_a_git_repository_is_an_error(self):
        out = subprocess.run(["python3", SCRIPT], cwd=tempfile.mkdtemp(), capture_output=True, text=True)
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "error: not a git repository\n", 2))

    def test_unknown_base_is_an_error(self):
        out = Repo().run("nope")
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "error: unknown BASE nope\n", 2))

    def test_undecodable_file_is_listed_as_unread(self):
        repo = Repo()
        repo.put(os.path.join(FIXTURES, "large-method", "before.rs"), "lib.rs")
        repo.git("add", "-A")
        repo.git("commit", "-q", "-m", "base")
        with open(os.path.join(repo.dir, "lib.rs"), "wb") as f:
            f.write(b"\xff\xfe fn x() {}\n")
        out = repo.run()
        self.assertEqual((out.stdout, out.returncode), ("unread:\nlib.rs\n", 0), out.stderr)


if __name__ == "__main__":
    unittest.main()
