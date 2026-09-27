"""build_ledger.py — regenerates docs/ledger.html from guardrails/reports/*.md.

Usage (from repo root):
    python tools/build_ledger.py
"""

import glob
import os
import re
from datetime import date

REPORTS_DIR = "guardrails/reports"
OUTPUT_FILE = "docs/ledger.html"


def parse_report(path):
    """Return a dict of fields extracted from a guardrail report markdown file."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    # --- Split front-matter ---
    parts = text.split("---")
    # parts[0] is empty, parts[1] is front-matter, parts[2:] is body
    if len(parts) < 3:
        raise ValueError(f"No YAML front-matter found in {path}")

    fm_text = parts[1]
    body = "---".join(parts[2:])

    # Simple key: value front-matter parser (no PyYAML)
    fm = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()

    # Coerce minutes_to_guardrail to int
    if "minutes_to_guardrail" in fm:
        fm["minutes_to_guardrail"] = int(fm["minutes_to_guardrail"])

    # Extract first non-blank line after each section heading
    def first_line_after(heading, text):
        pattern = re.compile(r"^##\s+" + re.escape(heading) + r"\s*$", re.MULTILINE)
        m = pattern.search(text)
        if not m:
            return ""
        rest = text[m.end():]
        for line in rest.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped
        return ""

    fm["root_cause"] = first_line_after("Root cause", body)
    fm["bug_class"] = first_line_after("Bug class", body)
    fm["fix"] = first_line_after("Fix", body)

    return fm


def sev_color(severity):
    """Return an inline style colour for a severity badge."""
    # SEV-1 is most severe → red; SEV-2 → orange; SEV-3+ → amber
    level = int(severity.split("-")[1]) if "-" in severity else 9
    if level == 1:
        return "#da1e28"
    if level == 2:
        return "#ff832b"
    return "#f1c21b"


def escape_html(s):
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


def build_card(report):
    inc = escape_html(report.get("incident", ""))
    title = escape_html(report.get("title", ""))
    severity = escape_html(report.get("severity", ""))
    rule_id = escape_html(report.get("rule_id", ""))
    minutes = report.get("minutes_to_guardrail", "—")
    root_cause = escape_html(report.get("root_cause", ""))
    bug_class = escape_html(report.get("bug_class", ""))
    fix = escape_html(report.get("fix", ""))
    sev_col = sev_color(report.get("severity", ""))

    return f"""\
<article>
  <header>
    <h2>{inc} — {title}</h2>
    <span class="sev" style="color:{sev_col}">{severity}</span>
    <span class="rule">{rule_id}</span>
  </header>
  <dl>
    <dt>Root cause</dt><dd>{root_cause}</dd>
    <dt>Bug class</dt><dd>{bug_class}</dd>
    <dt>Fix</dt><dd>{fix}</dd>
    <dt>Minutes</dt><dd>{minutes}</dd>
  </dl>
</article>"""


def build_html(reports, today):
    count = len(reports)
    avg_minutes = (
        round(sum(r["minutes_to_guardrail"] for r in reports) / count, 1)
        if count else "—"
    )

    cards = "\n".join(build_card(r) for r in reports)

    return f"""\
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Guardrail Ledger</title>
<style>
:root{{--bg:#f6f7f9;--card:#fff;--ink:#16181d;--mute:#5b6270;--line:#e2e5ea;--accent:#0f62fe;--sev:#da1e28}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111318;--card:#1a1d24;--ink:#e8eaee;--mute:#9aa2b1;--line:#2b303a;--accent:#78a9ff;--sev:#ff8389}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"IBM Plex Sans",sans-serif}}
main{{max-width:880px;margin:0 auto;padding:32px 16px}}h1{{margin:0 0 4px;font-size:28px}}.sub{{color:var(--mute);margin:0 0 24px}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:28px}}.stat{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}}
.stat b{{display:block;font-size:26px}}.stat span{{color:var(--mute);font-size:13px}}
article{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:16px}}
header{{display:flex;flex-wrap:wrap;align-items:center;gap:10px}}h2{{font-size:18px;margin:0;flex:1}}
.sev{{font-weight:600;font-size:13px}}.rule{{background:var(--accent);color:#fff;border-radius:999px;padding:2px 10px;font-size:13px;font-weight:600}}
dl{{display:grid;grid-template-columns:130px 1fr;gap:6px 14px;margin:14px 0}}dt{{color:var(--mute)}}dd{{margin:0}}
code{{font:13px ui-monospace,Menlo,monospace;background:var(--bg);padding:1px 5px;border-radius:4px}}
pre{{overflow:auto;background:var(--bg);padding:12px;border-radius:8px;font-size:12px}}summary{{cursor:pointer;color:var(--accent)}}
.empty{{color:var(--mute)}}@media (max-width:560px){{dl{{grid-template-columns:1fr}}.stats{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Guardrail Ledger</h1>
<p class="sub">Every incident fixed once, forever. Built with IBM Bob. Updated {today}.</p>
<section class="stats">
  <div class="stat"><b>{count}</b><span>postmortems closed</span></div>
  <div class="stat"><b>{count}</b><span>guardrails in CI</span></div>
  <div class="stat"><b>{avg_minutes}</b><span>avg minutes, postmortem to guardrail</span></div>
</section>
{cards}
</main></body></html>
"""


def main():
    md_files = sorted(
        f for f in glob.glob(os.path.join(REPORTS_DIR, "*.md"))
        if not f.endswith(".gitkeep")
    )

    if not md_files:
        print("No report files found — nothing to do.")
        return

    reports = []
    for path in md_files:
        try:
            reports.append(parse_report(path))
            print(f"  Parsed {path}")
        except Exception as exc:
            print(f"  WARNING: skipping {path}: {exc}")

    # Sort by incident id string (INC-NNNN sorts correctly lexicographically)
    reports.sort(key=lambda r: r.get("incident", ""))

    today = date.today().isoformat()
    html = build_html(reports, today)

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"\nWrote {OUTPUT_FILE}  ({len(reports)} incident(s), updated {today})")


if __name__ == "__main__":
    main()
