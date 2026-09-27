"""Build docs/index.html, the Guardrail Ledger, from guardrails/reports/*.md.

Stdlib only. Run: python tools/build_ledger.py   then publish docs/ with GitHub Pages.
"""
import html
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "guardrails" / "reports"
OUT = ROOT / "docs" / "index.html"


def parse(path: Path) -> dict:
    text = path.read_text()
    meta, body = {}, text
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
        body = match.group(2)
    sections = {}
    for block in re.split(r"^## ", body, flags=re.M)[1:]:
        heading, _, content = block.partition("\n")
        sections[heading.strip()] = content.strip()
    meta["sections"] = sections
    return meta


def inline(text: str) -> str:
    text = html.escape(text)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", text)


def card(r: dict) -> str:
    s = r["sections"]
    rows = "".join(
        f"<dt>{name}</dt><dd>{inline(s.get(name, '—'))}</dd>"
        for name in ("Root cause", "Bug class", "Regression test", "Fix", "Guardrail")
    )
    evidence = html.escape(s.get("Evidence", "").strip("`\n"))
    return f"""
<article>
  <header>
    <span class="sev">{inline(r.get('severity', ''))}</span>
    <h2>{inline(r.get('incident', ''))}: {inline(r.get('title', ''))}</h2>
    <span class="rule">{inline(r.get('rule_id', ''))}</span>
  </header>
  <dl>{rows}</dl>
  <details><summary>Evidence</summary><pre>{evidence}</pre></details>
</article>"""


def main():
    reports = [parse(p) for p in sorted(REPORTS.glob("*.md"))]
    minutes = [float(r["minutes_to_guardrail"]) for r in reports if r.get("minutes_to_guardrail", "").replace(".", "", 1).isdigit()]
    avg = f"{sum(minutes) / len(minutes):.0f}" if minutes else "—"
    body = "".join(card(r) for r in reports) or "<p class='empty'>No guardrail reports yet. Run the Guardrail Orchestrator in Bob.</p>"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(f"""<!doctype html>
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
.sev{{color:var(--sev);font-weight:600;font-size:13px}}.rule{{background:var(--accent);color:#fff;border-radius:999px;padding:2px 10px;font-size:13px;font-weight:600}}
dl{{display:grid;grid-template-columns:130px 1fr;gap:6px 14px;margin:14px 0}}dt{{color:var(--mute)}}dd{{margin:0}}
code{{font:13px ui-monospace,Menlo,monospace;background:var(--bg);padding:1px 5px;border-radius:4px}}
pre{{overflow:auto;background:var(--bg);padding:12px;border-radius:8px;font-size:12px}}summary{{cursor:pointer;color:var(--accent)}}
.empty{{color:var(--mute)}}@media (max-width:560px){{dl{{grid-template-columns:1fr}}.stats{{grid-template-columns:1fr}}}}
</style></head><body><main>
<h1>Guardrail Ledger</h1>
<p class="sub">Every incident fixed once, forever. Built with IBM Bob. Updated {date.today().isoformat()}.</p>
<section class="stats">
  <div class="stat"><b>{len(reports)}</b><span>postmortems closed</span></div>
  <div class="stat"><b>{sum(1 for r in reports if r.get('rule_id'))}</b><span>guardrails in CI</span></div>
  <div class="stat"><b>{avg}</b><span>avg minutes, postmortem to guardrail</span></div>
</section>
{body}
</main></body></html>
""")
    print(f"Wrote {OUT.relative_to(ROOT)} with {len(reports)} report(s)")


if __name__ == "__main__":
    main()
