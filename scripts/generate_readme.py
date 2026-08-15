#!/usr/bin/env python3
"""Generate Readme1.md from incidents.yaml (the single source of truth).

Usage:
    python scripts/generate_readme.py            # (re)write Readme1.md
    python scripts/generate_readme.py --check    # exit non-zero if stale

Workflow: edit incidents.yaml, then run this script. Never hand-edit
Readme1.md -- it is a generated artifact and CI enforces that it stays in
sync with incidents.yaml.
"""
import argparse
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "incidents.yaml"
OUT = ROOT / "Readme1.md"

MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse_date(value):
    """Return (year, month) ints from a 'YYYY' or 'YYYY-MM' value."""
    parts = str(value).split("-")
    year = int(parts[0])
    month = int(parts[1]) if len(parts) > 1 else 0
    return year, month


def fmt_date(value):
    year, month = parse_date(value)
    return f"{MONTHS[month]} {year}" if month else str(year)


def row(cells):
    return "| " + " | ".join(cells) + " |"


def render_leak_table(entries):
    lines = [
        row(["Date", "Organization", "Category", "Description", "Records / Volume", "Notes"]),
        row(["---"] * 6),
    ]
    for e in sorted(entries, key=lambda e: parse_date(e["date"]), reverse=True):
        anchor = f'<a href="{e["url"]}">{e["description"]}</a>'
        lines.append(row([
            fmt_date(e["date"]),
            e.get("org") or "",
            e.get("category") or "",
            anchor,
            e.get("records") or "",
            e.get("notes") or "",
        ]))
    return "\n".join(lines)


def render_iam_table(entries):
    lines = [
        "| # | Organization / Date | Root Cause / Credential Exposure | Impact & Details | Relevance to Static Keys / S3 Usage |",
        "|---|----------------------|----------------------------------|------------------|--------------------------------------|",
    ]
    ordered = sorted(entries, key=lambda e: parse_date(e["date"]), reverse=True)
    for i, e in enumerate(ordered, start=1):
        lines.append(row([
            f"**{i}**",
            f'**{e["org_date"]}**',
            e["root_cause"],
            e["impact"],
            e["relevance"],
        ]))
    return "\n".join(lines)


def build(data):
    parts = [
        "# s3-leaks",
        "",
        "## List of AWS S3 Leaks",
        "",
        "Feel free to send in a PR if you know of other leaks.",
        "",
        "Scope: this list covers **Amazon S3** exposures. Leaks from other object "
        "stores (Azure Blob Storage, Google Cloud Storage, Cloudflare R2 and the "
        "like) are out of scope, however large.",
        "",
        render_leak_table(data["s3_leaks"]),
        "",
        "## ElasticSearch",
        "",
        render_leak_table(data["elasticsearch"]),
        "",
        "## AWS IAM Static Credentials",
        "",
        "Public incidents involving exposed AWS IAM static keys or AWS credentials.",
        "",
        render_iam_table(data["iam_credentials"]),
        "",
        "## Research & Scale Studies",
        "",
        "Industry-wide studies of bucket exposure, rather than single-organisation "
        "incidents. These scans span several cloud providers; they are listed here "
        "because Amazon S3 is consistently a large share of what they find.",
        "",
        render_leak_table(data["research"]),
        "",
    ]
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="Exit non-zero if Readme1.md is out of sync with incidents.yaml")
    args = ap.parse_args()

    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    content = build(data)

    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != content:
            sys.stderr.write(
                "Readme1.md is out of sync with incidents.yaml.\n"
                "Run:  python scripts/generate_readme.py\n"
            )
            return 1
        print("Readme1.md is in sync with incidents.yaml.")
        return 0

    OUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUT.name} from {DATA.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
