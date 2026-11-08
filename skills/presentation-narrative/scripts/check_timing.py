#!/usr/bin/env python3
"""Checks an outline's timing table: each row's minutes match its start-end range, ranges are
contiguous, and the minutes sum to the window. Silent on pass; one line per mismatch, exit 1.

Usage: check_timing.py <outline.md> --window <minutes>
The table is the first markdown table whose first column holds `start-end` ranges; its minutes
column is the first header containing "min".
"""
import argparse
import re
import sys

RANGE = re.compile(r"^(\d+)-(\d+)$")


def cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


class TableError(Exception):
    pass


def timing_rows(text):
    """Returns (start, end, minutes cell) per range row of the timing table, or None when there is none."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|") or i + 2 >= len(lines) or not RANGE.match(cells(lines[i + 2])[0]):
            continue
        columns = [n for n, name in enumerate(cells(line)) if "min" in name.lower()]
        if not columns:
            raise TableError("timing table has no min column")
        rows = []
        for row in lines[i + 2:]:
            if not row.lstrip().startswith("|"):
                break
            match = RANGE.match(cells(row)[0])
            if match:
                rows.append((*map(int, match.groups()), cells(row)[columns[0]]))
        return rows
    return None


def findings(rows, window):
    found = []
    previous_end = rows[0][0]
    total = 0
    for start, end, cell in rows:
        if start != previous_end:
            found.append(f"gap: {previous_end} to {start}")
        previous_end = end
        try:
            minutes = float(cell)
        except ValueError:
            found.append(f'{start}-{end}: minutes "{cell}" is not a number')
            continue
        total += minutes
        if minutes != end - start:
            found.append(f"{start}-{end}: {minutes:g} min, range is {end - start}")
    if total != window:
        found.append(f"total {total:g} min, window {window}")
    return found


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("outline")
    parser.add_argument("--window", type=int, required=True)
    args = parser.parse_args(argv[1:])
    try:
        with open(args.outline, encoding="utf-8") as f:
            rows = timing_rows(f.read())
    except OSError:
        print(f"cannot read {args.outline}")
        return 1
    except TableError as error:
        print(error)
        return 1
    if not rows:
        print("no start-end timing table")
        return 1
    found = findings(rows, args.window)
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
