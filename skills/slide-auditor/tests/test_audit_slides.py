import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("audit_slides", HERE.parent / "scripts" / "audit_slides.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class PerSlideFrontmatterAndLayoutPlan(unittest.TestCase):
    def setUp(self):
        content = (HERE / "fixtures" / "frontmatter-and-plan.md").read_text()
        self.slides = [s for s in audit.parse_slides(content) if not s.get("is_headmatter")]
        self.report = audit.AuditReport()
        audit.audit_slides(audit.parse_slides(content), self.report, audit.PALETTES["default"])

    def test_frontmatter_block_is_not_a_slide(self):
        self.assertEqual(3, len(self.slides))

    def test_frontmatter_layout_belongs_to_its_slide(self):
        self.assertEqual("two-cols", self.slides[1].get("layout"))

    def test_notes_are_the_last_comment_not_the_layout_plan(self):
        self.assertEqual("These are the real speaker notes for the figure slide.", self.slides[1]["notes"])

    def test_layout_plan_before_svg_counts(self):
        plan_issues = [i for i in self.report.issues if "layout plan" in i.message.lower()]
        self.assertEqual([], plan_issues)


if __name__ == "__main__":
    unittest.main()
