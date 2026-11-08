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


def svg_issues(inner, palette=audit.PALETTES["default"], viewbox="0 0 800 350"):
    report = audit.AuditReport()
    audit.audit_svgs(1, [f'<svg viewBox="{viewbox}">{inner}</svg>'], report, palette)
    return report.issues


def element_findings(inner):
    return [i.severity for i in svg_issues(inner) if "elements" in i.message]


class SvgElementCount(unittest.TestCase):
    def test_more_than_ten_shapes_is_an_error(self):
        self.assertEqual([audit.Severity.ERROR], element_findings('<rect/>' * 12))

    def test_eight_shapes_is_a_warning(self):
        self.assertEqual([audit.Severity.WARNING], element_findings('<rect/>' * 8))

    def test_arrow_path_with_marker_end_counts(self):
        self.assertEqual([audit.Severity.WARNING], element_findings('<rect/>' * 7 + '<path d="M0 0" marker-end="url(#a)"/>'))

    def test_path_inside_marker_does_not_count(self):
        marker = '<defs><marker id="a"><path d="M0 0L10 5z"/></marker></defs>'
        self.assertEqual([], element_findings(marker + '<rect/>' * 7))

    def test_polygon_counts(self):
        self.assertEqual([audit.Severity.WARNING], element_findings('<rect/>' * 7 + '<polygon points="0,0 1,1 0,1"/>'))


def viewbox_findings(viewbox):
    return [i.message for i in svg_issues("", viewbox=viewbox) if "Missing viewBox" in i.message]


class ViewBox(unittest.TestCase):
    def test_decimal_viewbox_is_parsed(self):
        self.assertEqual([], viewbox_findings("0 0 850.5 350"))

    def test_comma_separated_viewbox_is_parsed(self):
        self.assertEqual([], viewbox_findings("0,0,800,400"))


def palette_findings(inner, palette=audit.PALETTES["default"]):
    return [i.message for i in svg_issues(inner, palette) if "not in declared palette" in i.message]


class Palette(unittest.TestCase):
    def test_hex_like_ids_in_references_are_not_colours(self):
        self.assertEqual(palette_findings('<rect fill="url(#abc)"/><use href="#fab"/>'), [])

    def test_eight_digit_hex_is_checked_by_its_colour(self):
        self.assertEqual(palette_findings('<rect fill="#2563EB80"/>'), [])
        self.assertNotEqual(palette_findings('<rect fill="#123456AA"/>'), [])

    def test_short_hex_outside_the_palette_is_flagged(self):
        self.assertEqual(1, len(palette_findings('<rect fill="#123"/>')))

    def test_short_hex_whose_long_form_is_in_the_palette_passes(self):
        self.assertEqual([], palette_findings('<rect fill="#fff"/>'))

    def test_long_hex_in_the_palette_passes(self):
        self.assertEqual([], palette_findings('<rect fill="#2563eb"/>'))


if __name__ == "__main__":
    unittest.main()
