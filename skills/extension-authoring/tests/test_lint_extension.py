"""Runs bin/lint-extension over a fixture directory built per check and checks its exact output."""
import os
import subprocess
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bin", "lint-extension")
GOOD = "Does a thing. Use when asked to do the thing. Not for other things (other)."


def lint(files, arg="."):
    root = tempfile.mkdtemp()
    for path, text in files.items():
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)
    out = subprocess.run(["python3", SCRIPT, arg], cwd=root, capture_output=True, text=True)
    return out.stdout, out.returncode


def skill(front, body="# Body\n"):
    return "---\n" + front + "---\n\n" + body


class Frontmatter(unittest.TestCase):
    def test_clean_skill_passes(self):
        self.assertEqual(lint({"s/SKILL.md": skill(f"name: s\ndescription: {GOOD}\n")}), ("", 0))

    def test_frontmatter_not_on_first_line(self):
        self.assertEqual(lint({"s/SKILL.md": "\n" + skill(f"name: s\ndescription: {GOOD}\n")}),
                         ("s/SKILL.md:1: frontmatter is read only when --- is the first line\n", 1))

    def test_missing_name_or_description(self):
        self.assertEqual(lint({"s/SKILL.md": skill("name: s\n"), "a.md": skill("tools: Read\n")}), (
            "a.md:1: agent is skipped without `name`\n"
            "a.md:1: agent is skipped without `description`\n"
            "s/SKILL.md:1: no `description`: the skill triggers on its first body line\n", 1))

    def test_description_and_when_to_use_over_the_listing_cap(self):
        description, when = GOOD + " " + "x" * 1300, "y" * 236
        total = len(description) + len(when)
        self.assertEqual(lint({"s/SKILL.md": skill(f"name: s\ndescription: {description}\nwhen_to_use: {when}\n")}),
                         (f"s/SKILL.md:3: description + when_to_use is {total:,} characters; the listing cuts at 1,536\n", 1))

    def test_one_use_when_clause(self):
        self.assertEqual(lint({"a/SKILL.md": skill("name: a\ndescription: Does a thing. Use before committing.\n"),
                               "b/SKILL.md": skill("name: b\ndescription: Use when x. Use when y.\n")}), (
            "a/SKILL.md:3: description has 0 \"Use when\" clauses; write one\n"
            "b/SKILL.md:3: description has 2 \"Use when\" clauses; write one\n", 1))

    def test_at_most_one_not_for(self):
        self.assertEqual(lint({"s/SKILL.md": skill(f"name: s\ndescription: {GOOD} Not for y (z).\n")}),
                         ("s/SKILL.md:3: description has 2 \"Not for\" clauses; name only the neighbour that should win\n", 1))

    def test_unknown_keys(self):
        self.assertEqual(lint({"s/SKILL.md": skill(f"name: s\ndescription: {GOOD}\ndisableModelInvocation: true\n"),
                               "a.md": skill(f"name: a\ndescription: {GOOD}\ndisallowed-tools: Bash\nmodel: sonnet\n")}), (
            "a.md:4: unknown agent key `disallowed-tools` is ignored; agent keys are camelCase\n"
            "s/SKILL.md:4: unknown skill key `disableModelInvocation` is ignored; skill keys are hyphenated\n", 1))

    def test_unreadable_path_is_one_finding(self):
        self.assertEqual(lint({}, arg="nope"), ("nope: cannot read: No such file or directory\n", 1))

    def test_directory_with_no_extension_is_one_finding(self):
        self.assertEqual(lint({"notes.txt": "x\n"}), (".: no SKILL.md or agent file found\n", 1))

    def test_skills_dir_entry_without_skill_md(self):
        files = {"skills/s/SKILL.md": skill(f"name: s\ndescription: {GOOD}\n"), "skills/t/references/x.md": "x\n",
                 "agents/sub/notes.txt": "x\n", "agents/a.md": skill(f"name: a\ndescription: {GOOD}\n")}
        self.assertEqual(lint(files, arg="skills"), ("skills/t: holds no SKILL.md, so no skill loads from it\n", 1))
        self.assertEqual(lint(files, arg="agents"), ("", 0))

    def test_folded_description_is_read_across_lines(self):
        self.assertEqual(lint({"s/SKILL.md": skill("name: s\ndescription: >\n  Does a thing.\n  Use when asked.\n")}), ("", 0))

    def test_frontmatter_comment_is_not_joined_onto_the_previous_key(self):
        self.assertEqual(lint({"s/SKILL.md": skill(f"name: s\ndescription: {GOOD}\n# Use when nothing else fits.\n")}), ("", 0))

    def test_skill_that_is_not_utf8_is_one_finding(self):
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "s"))
        with open(os.path.join(root, "s", "SKILL.md"), "wb") as f:
            f.write(b"---\nname: s\ndescription: \xff\n---\n")
        out = subprocess.run(["python3", SCRIPT, "s"], cwd=root, capture_output=True, text=True)
        self.assertEqual((out.stdout, out.returncode), ("s/SKILL.md: cannot read: not UTF-8\n", 1))

    def test_one_skill_dir_or_one_file(self):
        files = {"s/SKILL.md": skill("name: s\ndescription: Does s.\n"), "s/example.md": "# Example\n",
                 "a.md": skill("name: a\n")}
        self.assertEqual(lint(files, arg="s"), ("s/SKILL.md:3: description has 0 \"Use when\" clauses; write one\n", 1))
        self.assertEqual(lint(files, arg="a.md"), ("a.md:1: agent is skipped without `description`\n", 1))


class Files(unittest.TestCase):
    def test_relative_links_resolve(self):
        body = "# Body\n\nSee [ref](references/ref.md), [gone](references/gone.md#top) and [web](https://x.dev).\n"
        self.assertEqual(lint({"s/SKILL.md": skill(f"name: s\ndescription: {GOOD}\n", body), "s/references/ref.md": "x\n"}),
                         ("s/SKILL.md:8: link target references/gone.md does not exist\n", 1))

    def test_links_in_code_are_not_checked(self):
        body = "# Body\n\n```md\nSee [ref](references/gone.md).\n```\n\nWrite `[ref](references/gone.md)` like this.\n"
        self.assertEqual(lint({"s/SKILL.md": skill(f"name: s\ndescription: {GOOD}\n", body)}), ("", 0))

    def test_preprocessing_hazards_in_a_skill_body(self):
        body = "# Body\n\nRun `$ARGUMENTS` on $0, not \\$1.\n!`date`\n"
        self.assertEqual(lint({"s/SKILL.md": skill(f"name: s\ndescription: {GOOD}\n", body), "s/notes.md": "$0 !`date`\n"}), (
            "s/SKILL.md:8: `$ARGUMENTS` is substituted at load, code fences included; escape it as `\\$`\n"
            "s/SKILL.md:8: `$0` is substituted at load, code fences included; escape it as `\\$`\n"
            "s/SKILL.md:9: !`command` runs at load, before Claude reads the body; show it in a supporting file\n", 1))

    def test_bash_4_syntax_under_bin_bash(self):
        script = "#!/bin/bash\ndeclare -A seen\nmapfile -t xs < f\necho \"${name,,}\"\n"
        self.assertEqual(lint({"s/SKILL.md": skill(f"name: s\ndescription: {GOOD}\n"), "s/bin/run": script,
                               "s/bin/ok": "#!/usr/bin/env zsh\ndeclare -A seen\n"}), (
            "s/bin/run:2: declare -A needs bash 4; macOS /bin/bash is 3.2\n"
            "s/bin/run:3: mapfile needs bash 4; macOS /bin/bash is 3.2\n"
            "s/bin/run:4: ${name,,} needs bash 4; macOS /bin/bash is 3.2\n", 1))

    def test_bash_4_syntax_under_bash_with_flags_or_env(self):
        self.assertEqual(lint({"s/SKILL.md": skill(f"name: s\ndescription: {GOOD}\n"),
                               "s/bin/a": "#!/bin/bash -eu\nreadarray -t xs < f\n",
                               "s/bin/b": "#!/usr/bin/env bash\necho \"${name^^}\"\n"}), (
            "s/bin/a:2: readarray needs bash 4; macOS /bin/bash is 3.2\n"
            "s/bin/b:2: ${name^^} needs bash 4; macOS /bin/bash is 3.2\n", 1))


if __name__ == "__main__":
    unittest.main()
