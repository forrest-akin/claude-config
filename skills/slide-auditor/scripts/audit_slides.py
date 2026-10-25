#!/usr/bin/env python3
"""
Slide Auditor — Validates Slidev slides.md files for quality issues.

Checks SVG dimensions, font sizes, element counts, color consistency,
slide word counts, speaker notes presence/length, and structural integrity.

Usage:
    python3 audit_slides.py <path_to_slides.md> [--palette default|mono|warm|custom]
    python3 audit_slides.py slides.md --palette default --timing 15
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Issue:
    severity: Severity
    slide: Optional[int]
    category: str
    message: str

    def __str__(self):
        loc = f"Slide {self.slide}" if self.slide else "Global"
        return f"  [{self.severity.value}] {loc} | {self.category}: {self.message}"


@dataclass
class AuditReport:
    issues: list[Issue] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def add(self, severity: Severity, slide: Optional[int], category: str, message: str):
        self.issues.append(Issue(severity, slide, category, message))

    @property
    def error_count(self):
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self):
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    @property
    def info_count(self):
        return sum(1 for i in self.issues if i.severity == Severity.INFO)

    def print_report(self):
        print("\n" + "=" * 70)
        print("  SLIDE AUDIT REPORT")
        print("=" * 70)

        if self.stats:
            print(f"\n  Slides: {self.stats.get('slide_count', '?')}")
            print(f"  SVGs: {self.stats.get('svg_count', '?')}")
            print(f"  Estimated delivery: {self.stats.get('est_minutes', '?')} min")
            if self.stats.get('target_minutes'):
                print(f"  Target time: {self.stats['target_minutes']} min")

        if not self.issues:
            print("\n  ✓ No issues found. Presentation looks clean.")
            print("=" * 70)
            return

        # Group by severity
        for sev in [Severity.ERROR, Severity.WARNING, Severity.INFO]:
            items = [i for i in self.issues if i.severity == sev]
            if items:
                icon = {"ERROR": "✗", "WARNING": "⚠", "INFO": "ℹ"}[sev.value]
                print(f"\n  {icon} {sev.value}S ({len(items)})")
                print(f"  {'-' * 40}")
                for item in items:
                    print(str(item))

        print(f"\n  Summary: {self.error_count} errors, {self.warning_count} warnings, {self.info_count} info")
        if self.error_count > 0:
            print("  ✗ FIX ERRORS before presenting.")
        elif self.warning_count > 0:
            print("  ⚠ Review warnings for visual quality.")
        else:
            print("  ✓ Looking good — minor suggestions only.")
        print("=" * 70 + "\n")


# Default color palette
PALETTES = {
    "default": {
        "#2563EB", "#F59E0B", "#EF4444", "#10B981",
        "#F3F4F6", "#FFFFFF", "#1F2937", "#E5E7EB", "#6B7280",
        # Common tints/shades that are acceptable
        "#FEF2F2", "#FECACA", "#F0FDF4", "#BBF7D0",
        "#EFF6FF", "#BFDBFE", "#FEF3C7", "#FDE68A",
    },
    "mono": {
        "#1E293B", "#475569", "#94A3B8", "#F1F5F9",
        "#FFFFFF", "#CBD5E1", "#64748B",
    },
    "warm": {
        "#7C3AED", "#F97316", "#DC2626", "#059669",
        "#FAF5FF", "#FFFFFF", "#1F2937", "#E9D5FF", "#6B7280",
    },
}

KNOWN_LAYOUTS = {
    "default", "center", "cover", "end", "full", "none",
    "intro", "quote", "section", "statement", "fact",
    "two-cols", "two-cols-header",
    "image", "image-left", "image-right",
    "iframe", "iframe-left", "iframe-right",
}

MAX_VIEWBOX_W = 900  # slide-svg-figures/references/slidev-canvas.md
MAX_VIEWBOX_H = 380
MAX_ELEMENTS_PER_SVG = 7
MIN_FONT_SIZE = 14
MAX_WORDS_PER_SLIDE = 30
MAX_WORDS_ERROR = 50
MIN_NOTES_WORDS = 80
MAX_NOTES_WORDS = 300
SECONDS_PER_SLIDE = 90


YAML_LINE = re.compile(r'^\s*$|^\s*[\w-]+\s*:|^\s+\S|^\s*-\s')
COMMENT = re.compile(r'<!--(.*?)-->', re.DOTALL)


def split_chunks(lines: list[str]) -> list[list[str]]:
    """Split on `---` lines outside code fences."""
    chunks, current, fenced = [], [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            fenced = not fenced
        if not fenced and line.rstrip() == "---":
            chunks.append(current)
            current = []
        else:
            current.append(line)
    chunks.append(current)
    return chunks


def is_frontmatter(chunk: list[str]) -> bool:
    return any(l.strip() for l in chunk) and all(YAML_LINE.match(l) for l in chunk)


def group_slides(content: str) -> tuple[Optional[str], list[tuple[str, str]]]:
    """Return (headmatter, [(frontmatter, body)]). A YAML chunk right after a separator is the next slide's frontmatter."""
    chunks = split_chunks(content.split("\n"))
    headmatter = None
    if len(chunks) > 2 and not "".join(chunks[0]).strip():
        headmatter = "\n".join(chunks[1])
        chunks = chunks[2:]
    slides, pending = [], ""
    for chunk in chunks:
        text = "\n".join(chunk)
        if not pending and is_frontmatter(chunk):
            pending = text
            continue
        slides.append((pending, text))
        pending = ""
    return headmatter, slides


def parse_slides(content: str) -> list[dict]:
    """Split slides.md into individual slides with metadata."""
    headmatter, grouped = group_slides(content)
    slides = []
    if headmatter is not None:
        slides.append({"index": 0, "is_headmatter": True, "frontmatter_raw": headmatter,
                       "notes": "", "svgs": [], "word_count": 0, "raw": headmatter})

    for i, (frontmatter, body) in enumerate(grouped, start=1):
        slide = {"index": i, "raw": body, "frontmatter_raw": frontmatter, "notes": "", "svgs": []}

        layout_match = re.search(r'^layout:\s*(\S+)', frontmatter, re.MULTILINE)
        if layout_match:
            slide["layout"] = layout_match.group(1)

        comments = list(COMMENT.finditer(body))
        if comments and not body[comments[-1].end():].strip():
            slide["notes"] = comments[-1].group(1).strip()

        slide["svgs"] = re.findall(r'<svg\b[^>]*>.*?</svg>', body, re.DOTALL)
        slide["has_layout_plan"] = bool(re.search(r'<!--\s*layout plan', body, re.IGNORECASE))

        content_clean = COMMENT.sub("", body)
        for svg in slide["svgs"]:
            content_clean = content_clean.replace(svg, "")
        content_clean = re.sub(r'<[^>]+>', ' ', content_clean)
        content_clean = re.sub(r'[#*_`\[\]()]', ' ', content_clean)
        slide["content_text"] = content_clean.strip()
        slide["word_count"] = len([w for w in content_clean.split() if w not in {'v-click', 'v-clicks'}])

        slides.append(slide)

    return slides


def audit_svgs(slide_idx: int, svgs: list[str], report: AuditReport, palette_colors: set):
    """Audit SVG elements within a slide."""
    for svg_i, svg in enumerate(svgs):
        svg_label = f"SVG {svg_i + 1}" if len(svgs) > 1 else "SVG"

        # Check viewBox
        vb_match = re.search(r'viewBox=["\'](\d+)\s+(\d+)\s+(\d+)\s+(\d+)["\']', svg)
        if not vb_match:
            report.add(Severity.ERROR, slide_idx, svg_label, "Missing viewBox attribute")
        else:
            vb_w = int(vb_match.group(3))
            vb_h = int(vb_match.group(4))
            if vb_w > MAX_VIEWBOX_W:
                report.add(Severity.WARNING, slide_idx, svg_label,
                           f"viewBox width {vb_w}px exceeds recommended max {MAX_VIEWBOX_W}px")
            if vb_h > MAX_VIEWBOX_H:
                report.add(Severity.WARNING, slide_idx, svg_label,
                           f"viewBox height {vb_h}px exceeds recommended max {MAX_VIEWBOX_H}px")

        # Check font sizes
        font_sizes = re.findall(r'font-size=["\']?(\d+(?:\.\d+)?)', svg)
        for fs in font_sizes:
            if float(fs) < MIN_FONT_SIZE:
                report.add(Severity.ERROR, slide_idx, svg_label,
                           f"Font size {fs}px below minimum {MIN_FONT_SIZE}px — text will be unreadable")

        # Count major elements
        rect_count = len(re.findall(r'<rect\b', svg))
        circle_count = len(re.findall(r'<circle\b', svg))
        ellipse_count = len(re.findall(r'<ellipse\b', svg))
        line_count = len(re.findall(r'<line\b', svg))
        path_count = len(re.findall(r'<path\b(?![^>]*marker)', svg))  # exclude marker paths
        polygon_count = len(re.findall(r'<polygon\b', svg))
        # Don't count text or markers as "elements" for density purposes
        # but do count polyline
        polyline_count = len(re.findall(r'<polyline\b', svg))

        shape_count = rect_count + circle_count + ellipse_count
        connector_count = line_count + path_count + polyline_count
        total_elements = shape_count + connector_count

        if total_elements > MAX_ELEMENTS_PER_SVG:
            report.add(Severity.WARNING, slide_idx, svg_label,
                       f"{total_elements} elements detected (shapes: {shape_count}, "
                       f"connectors: {connector_count}). Recommended max: {MAX_ELEMENTS_PER_SVG}. "
                       f"Consider simplifying.")
        elif total_elements > MAX_ELEMENTS_PER_SVG + 3:
            report.add(Severity.ERROR, slide_idx, svg_label,
                       f"{total_elements} elements — figure is too complex for a slide. Split into multiple slides.")

        # Check text anchoring inside shapes
        text_elements = re.findall(r'<text\b[^>]*>', svg)
        for text_el in text_elements:
            if 'text-anchor' not in text_el:
                report.add(Severity.INFO, slide_idx, svg_label,
                           "Text element missing text-anchor attribute — may misalign")
            if 'dominant-baseline' not in text_el:
                report.add(Severity.INFO, slide_idx, svg_label,
                           "Text element missing dominant-baseline — vertical centering may be off")

        # Check marker-end references have corresponding defs
        if 'marker-end' in svg and '<marker' not in svg:
            report.add(Severity.ERROR, slide_idx, svg_label,
                       "marker-end referenced but no <marker> defined in <defs>. Arrows won't render.")

        # Check color consistency
        hex_colors = set(re.findall(r'#[0-9A-Fa-f]{6}\b', svg))
        hex_colors_upper = {c.upper() for c in hex_colors}
        palette_upper = {c.upper() for c in palette_colors}
        off_palette = hex_colors_upper - palette_upper
        if off_palette:
            report.add(Severity.INFO, slide_idx, svg_label,
                       f"Colors not in declared palette: {', '.join(sorted(off_palette))}. "
                       f"Consider standardizing.")

        # Check text length inside shapes (look for text between rect and next rect or end)
        text_contents = re.findall(r'>([^<]{20,})<', svg)
        for tc in text_contents:
            words = tc.strip().split()
            if len(words) > 6:
                report.add(Severity.WARNING, slide_idx, svg_label,
                           f"Text block with {len(words)} words inside SVG element: "
                           f"'{' '.join(words[:6])}...' — max 3 words/line, 2 lines recommended")


def audit_slides(slides: list[dict], report: AuditReport, palette_colors: set, target_minutes: int = 0):
    """Run all audits across all slides."""
    content_slides = [s for s in slides if not s.get("is_headmatter")]
    report.stats["slide_count"] = len(content_slides)
    report.stats["svg_count"] = sum(len(s["svgs"]) for s in content_slides)
    report.stats["est_minutes"] = round(len(content_slides) * SECONDS_PER_SLIDE / 60, 1)
    if target_minutes:
        report.stats["target_minutes"] = target_minutes

    # Check headmatter
    headmatter = slides[0] if slides and slides[0].get("is_headmatter") else None
    if not headmatter:
        report.add(Severity.WARNING, None, "Structure", "No headmatter block detected at start of file")

    # Timing check
    if target_minutes and report.stats["est_minutes"] > target_minutes:
        report.add(Severity.WARNING, None, "Timing",
                   f"Estimated {report.stats['est_minutes']} min exceeds target {target_minutes} min. "
                   f"Consider cutting {int((report.stats['est_minutes'] - target_minutes) / (SECONDS_PER_SLIDE / 60))} slides.")

    prev_layout = None
    for slide in content_slides:
        idx = slide["index"]

        # Word count
        wc = slide["word_count"]
        if wc > MAX_WORDS_ERROR:
            report.add(Severity.ERROR, idx, "Content",
                       f"{wc} words on slide — way too dense. Move content to speaker notes. Max: {MAX_WORDS_PER_SLIDE}")
        elif wc > MAX_WORDS_PER_SLIDE:
            report.add(Severity.WARNING, idx, "Content",
                       f"{wc} words on slide — consider moving some to speaker notes. Target: ≤{MAX_WORDS_PER_SLIDE}")

        # Speaker notes
        if not slide["notes"]:
            # Title/cover/end slides can skip notes
            layout = slide.get("layout", "default")
            if layout not in {"cover", "end"}:
                report.add(Severity.WARNING, idx, "Notes", "Missing speaker notes")
        else:
            notes_wc = len(slide["notes"].split())
            if notes_wc < MIN_NOTES_WORDS:
                report.add(Severity.INFO, idx, "Notes",
                           f"Speaker notes only {notes_wc} words — may need more for a full delivery script "
                           f"(target: {MIN_NOTES_WORDS}-{MAX_NOTES_WORDS})")
            elif notes_wc > MAX_NOTES_WORDS:
                report.add(Severity.INFO, idx, "Notes",
                           f"Speaker notes {notes_wc} words — may run long on this slide "
                           f"(target: {MIN_NOTES_WORDS}-{MAX_NOTES_WORDS})")

        # Layout check
        layout = slide.get("layout")
        if layout and layout not in KNOWN_LAYOUTS:
            report.add(Severity.INFO, idx, "Layout",
                       f"Layout '{layout}' not in default Slidev layouts — ensure custom layout exists")
        if layout and layout == prev_layout and layout not in {"default", "center"}:
            report.add(Severity.INFO, idx, "Layout",
                       f"Same layout '{layout}' as previous slide — consider varying for visual interest")
        prev_layout = layout

        # SVG audits
        if slide["svgs"]:
            audit_svgs(idx, slide["svgs"], report, palette_colors)
            if not slide["has_layout_plan"]:
                report.add(Severity.INFO, idx, "SVG",
                           "No layout plan comment found. Adding one helps prevent overlap issues.")


def main():
    parser = argparse.ArgumentParser(description="Audit a Slidev slides.md file for quality issues")
    parser.add_argument("file", help="Path to slides.md")
    parser.add_argument("--palette", choices=["default", "mono", "warm", "custom"],
                        default="default", help="Color palette to check against")
    parser.add_argument("--timing", type=int, default=0,
                        help="Target presentation time in minutes (0 to skip timing check)")
    parser.add_argument("--json", action="store_true", help="Output as JSON instead of formatted report")
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    content = filepath.read_text(encoding="utf-8")
    palette_colors = PALETTES.get(args.palette, set())

    slides = parse_slides(content)
    report = AuditReport()
    audit_slides(slides, report, palette_colors, args.timing)

    if args.json:
        output = {
            "stats": report.stats,
            "issues": [
                {
                    "severity": i.severity.value,
                    "slide": i.slide,
                    "category": i.category,
                    "message": i.message,
                }
                for i in report.issues
            ],
            "summary": {
                "errors": report.error_count,
                "warnings": report.warning_count,
                "info": report.info_count,
            }
        }
        print(json.dumps(output, indent=2))
    else:
        report.print_report()

    sys.exit(1 if report.error_count > 0 else 0)


if __name__ == "__main__":
    main()
