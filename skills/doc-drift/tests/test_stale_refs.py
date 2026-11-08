"""Runs bin/stale-refs in fixture repos built per test and checks its exact output."""
import os
import subprocess
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "stale-refs")
DATED = dict(os.environ, GIT_AUTHOR_DATE="2026-01-02T00:00:00", GIT_COMMITTER_DATE="2026-01-02T00:00:00",
             GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


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
        return subprocess.run(["python3", SCRIPT, *args], cwd=self.dir, capture_output=True, text=True)


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
        out = subprocess.run(["python3", SCRIPT], cwd=tempfile.mkdtemp(), capture_output=True, text=True)
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


if __name__ == "__main__":
    unittest.main()
