"""Runs bin/stale-refs in fixture repos built per test and checks its exact output."""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "bin", "stale-refs")
ENV = {"PATH": os.environ["PATH"], "HOME": os.environ["HOME"], "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
DATED = dict(ENV, GIT_AUTHOR_DATE="2026-01-02T00:00:00", GIT_COMMITTER_DATE="2026-01-02T00:00:00")


class Repo:
    def __init__(self, files):
        self.dir = tempfile.mkdtemp()
        self.git("init", "-q")
        self.write(files)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.dir, env=DATED, check=True)

    def write(self, files):
        for path, text in files.items():
            full = os.path.join(self.dir, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb" if isinstance(text, bytes) else "w") as f:
                f.write(text)

    def run(self, *args):
        return subprocess.run(["python3", SCRIPT, *args], cwd=self.dir, env=ENV, capture_output=True, text=True)


class StaleRefs(unittest.TestCase):
    def test_renamed_function_still_named_in_a_doc(self):
        repo = Repo({"app.py": "def fetchUser(id):\n    return id\n",
                     "README.md": "# App\n\nCall `fetchUser` with an id.\n"})
        repo.write({"app.py": "def loadUser(id):\n    return id\n"})
        out = repo.run()
        self.assertEqual((out.stdout, out.returncode), ("fetchUser\tname\tREADME.md:3\t2026-01-02\n", 0))

    def test_removed_environment_variable_still_documented(self):
        repo = Repo({"app.py": "import os\ntoken = os.environ[\"API_TOKEN\"]\n",
                     "README.md": "# App\n\nSet API_TOKEN before starting.\n"})
        repo.write({"app.py": "import os\n"})
        out = repo.run()
        self.assertEqual((out.stdout, out.returncode), ("API_TOKEN\tenv\tREADME.md:3\t2026-01-02\n", 0))

    def test_bumped_version_still_stated_in_a_doc(self):
        repo = Repo({"package.json": '{"version": "1.2.0"}\n',
                     "README.md": "# App\n\nInstall version 1.2.0.\n"})
        repo.write({"package.json": '{"version": "1.3.0"}\n'})
        out = repo.run()
        self.assertEqual((out.stdout, out.returncode), ("1.2.0\tversion\tREADME.md:3\t2026-01-02\n", 0))

    def test_token_on_a_reworded_line_is_not_reported(self):
        repo = Repo({"app.py": "import os\n", "README.md": "# App\n\nSet API_TOKEN before starting.\n"})
        repo.write({"README.md": "# App\n\nSet API_TOKEN first.\n"})
        out = repo.run()
        self.assertEqual((out.stdout, out.returncode), ("", 0))

    def test_token_still_in_code_is_not_reported(self):
        repo = Repo({"app.py": "from util import parseConfig\nparseConfig()\n",
                     "util.py": "def parseConfig():\n    pass\n",
                     "README.md": "# App\n\n`parseConfig` reads the settings.\n"})
        repo.write({"app.py": "\n"})
        out = repo.run()
        self.assertEqual((out.stdout, out.returncode), ("", 0))

    def test_outside_a_git_repo_is_an_error(self):
        out = subprocess.run(["python3", SCRIPT], cwd=tempfile.mkdtemp(), env=ENV, capture_output=True, text=True)
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "error: not a git repository\n", 2))

    def test_unknown_base_is_an_error(self):
        out = Repo({"README.md": "# App\n"}).run("nope")
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "error: unknown BASE nope\n", 2))

    def test_unreadable_file_is_listed_not_skipped(self):
        repo = Repo({"app.py": "def fetchUser(id):\n    return id\n",
                     "README.md": "# App\n\nCall `fetchUser` with an id.\n",
                     "notes.md": b"\xff\xfe fetchUser\n"})
        repo.write({"app.py": "def loadUser(id):\n    return id\n"})
        out = repo.run()
        self.assertEqual((out.stdout, out.returncode),
                         ("fetchUser\tname\tREADME.md:3\t2026-01-02\nunread:\nnotes.md\n", 0))

    def test_tracked_file_deleted_from_the_working_tree_is_not_unread(self):
        repo = Repo({"app.py": "def fetchUser(id):\n    return id\n", "old.md": "# Old\n",
                     "README.md": "# App\n\nCall `fetchUser` with an id.\n"})
        repo.write({"app.py": "def loadUser(id):\n    return id\n"})
        os.remove(os.path.join(repo.dir, "old.md"))
        out = repo.run()
        self.assertEqual((out.stdout, out.returncode), ("fetchUser\tname\tREADME.md:3\t2026-01-02\n", 0))

    def test_permission_denied_changed_file_is_unread(self):
        repo = Repo({"app.py": "def fetchUser(id):\n    return id\n", "secret.py": "x = 1\n",
                     "README.md": "# App\n\nCall `fetchUser` with an id.\n"})
        repo.write({"app.py": "def loadUser(id):\n    return id\n", "secret.py": "x = 2\n"})
        os.chmod(os.path.join(repo.dir, "secret.py"), 0)
        out = repo.run()
        self.assertEqual((out.stdout, out.stderr, out.returncode),
                         ("fetchUser\tname\tREADME.md:3\t2026-01-02\nunread:\nsecret.py\n", "", 0))


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
        done = subprocess.run([sys.executable, "-m", "unittest", "test_stale_refs.StaleRefs"], cwd=HERE,
                              env=dict(os.environ, GIT_DIR=decoy, GIT_WORK_TREE=worktree, PYTHONDONTWRITEBYTECODE="1"),
                              capture_output=True, text=True)
        self.assertEqual(changed(before, snapshot(decoy, worktree)), [])
        self.assertEqual(done.returncode, 0, done.stderr)


if __name__ == "__main__":
    unittest.main()
