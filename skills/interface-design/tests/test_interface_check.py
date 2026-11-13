"""Runs bin/interface-check on the converged fixture and on one broken copy per failure."""
import os
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "bin", "interface-check")
with open(os.path.join(HERE, "fixtures", "converged.md")) as f:
    CONVERGED = f.read()


def check(path):
    out = subprocess.run(["python3", SCRIPT, path], capture_output=True, text=True)
    return out.stdout, out.returncode


def check_text(text):
    path = os.path.join(tempfile.mkdtemp(), "draft.md")
    with open(path, "w") as f:
        f.write(text)
    return check(path)


def broken(old, new):
    assert CONVERGED.count(old) == 1, old
    return CONVERGED.replace(old, new)


class InterfaceCheck(unittest.TestCase):
    def test_converged_draft_passes_silently(self):
        self.assertEqual(check(os.path.join(HERE, "fixtures", "converged.md")), ("", 0))

    def test_missing_heading_is_reported_where_it_should_be(self):
        out, code = check_text(broken("## 7. Standing rules", ""))
        self.assertEqual((out.splitlines()[0], code), ('heading 7: expected "## 7. Standing rules", found "nothing"', 1))

    def test_renamed_heading_is_reported_by_position(self):
        self.assertEqual(check_text(broken("## 3. Throwaway callers", "## 3. Callers")),
                         ('heading 3: expected "## 3. Throwaway callers", found "## 3. Callers"\n', 1))

    def test_draft_without_the_invariants_heading_reports_both(self):
        self.assertEqual(check_text(broken("## 2. Invariants\n", "")),
                         ('heading 2: expected "## 2. Invariants", found "## 3. Throwaway callers"\n'
                          "no numbered invariants\n", 1))

    def test_invariant_not_numbered_in_sequence_is_reported(self):
        for marker in ("-", "3."):
            with self.subTest(marker):
                item = f"{marker} A revoked grant denies on every path — Ada, 2026-11-01"
                self.assertEqual(check_text(broken("2. A revoked", f"{marker} A revoked")),
                                 (f"invariant 2 is not numbered 2.: {item}\n", 1))

    def test_draft_without_invariants_is_reported(self):
        text = broken("1. Every entry point returns the decision `authorize` returns for the same request — Ada, "
                      "2026-11-01\n2. A revoked grant denies on every path — Ada, 2026-11-01\n", "")
        self.assertEqual(check_text(text), ("no numbered invariants\n", 1))

    def test_unattributed_items_are_listed_with_their_section(self):
        precedence = "- An explicit deny wins over a role grant when both match"
        batch = "- Batch export: `rows.filter(r => authorize(fromRow(r)).allowed)`; awkward to write: nothing"
        for old, new, finding in (
                (f"{precedence} — Ada, 2026-11-01", precedence, f"## 4. Precedence: {precedence}"),
                (f"{precedence} — Ada, 2026-11-01", f"{precedence} — <name>, <YYYY-MM-DD>",
                 f"## 4. Precedence: {precedence} — <name>, <YYYY-MM-DD>"),
                ("  nothing — Ada, 2026-11-01", "  nothing", f"## 3. Throwaway callers: {batch}"),
                ("type — Ada, 2026-11-01", "type", "## 6. Stop conditions: - Whether service accounts get their own "
                 "request type")):
            with self.subTest(new):
                self.assertEqual(check_text(broken(old, new)), (f"unattributed: {finding}\n", 1))

    def test_edited_stop_conditions_are_reported(self):
        self.assertEqual(check_text(broken("weakened, narrowed,\nskipped", "weakened,\nskipped")),
                         ("stop conditions differ from the template\n", 1))

    def test_edited_standing_rules_are_reported(self):
        self.assertEqual(check_text(broken("- Tidy-first outranks smallest diff.\n", "")),
                         ("standing rules differ from the template\n", 1))

    def test_unreadable_draft_is_one_finding(self):
        path = os.path.join(tempfile.mkdtemp(), "missing.md")
        self.assertEqual(check(path), (f"unreadable: {path}\n", 1))

    def test_draft_that_is_not_utf8_is_one_finding(self):
        path = os.path.join(tempfile.mkdtemp(), "draft.md")
        with open(path, "wb") as f:
            f.write(b"\xff\xfe draft\n")
        self.assertEqual(check(path), (f"unreadable: {path}\n", 1))

    def test_wrong_argument_count_prints_usage(self):
        out = subprocess.run(["python3", SCRIPT], capture_output=True, text=True)
        self.assertEqual((out.stdout, out.stderr, out.returncode), ("", "usage: interface-check <draft>\n", 2))


if __name__ == "__main__":
    unittest.main()
