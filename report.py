import json
from datetime import datetime

SEVERITY_COLORS = {
    "HIGH":   "#f87171",
    "MEDIUM": "#fb923c",
    "LOW":    "#facc15",
    "INFO":   "#60a5fa"
}

SEVERITY_BG = {
    "HIGH":   "rgba(248,113,113,0.08)",
    "MEDIUM": "rgba(251,146,60,0.08)",
    "LOW":    "rgba(250,204,21,0.06)",
    "INFO":   "rgba(96,165,250,0.08)"
}

CATEGORY_ICONS = {
    "security":    "⬡",
    "bug":         "◈",
    "logic":       "◎",
    "style":       "▣",
    "performance": "◐"
}

def generate_html_report(report: dict, target: str) -> str:
    score = report.get("score", 0)
    summary = report.get("summary", "")
    issues = report.get("issues", [])
    fixed_code = report.get("fixed_code", "")

    if score >= 7:
        score_color = "#4ade80"
        score_label = "Good"
    elif score >= 4:
        score_color = "#fb923c"
        score_label = "Needs Work"
    else:
        score_color = "#f87171"
        score_label = "Poor"

    high   = sum(1 for i in issues if i.get("severity") == "HIGH")
    medium = sum(1 for i in issues if i.get("severity") == "MEDIUM")
    low    = sum(1 for i in issues if i.get("severity") == "LOW")
    info   = sum(1 for i in issues if i.get("severity") == "INFO")

    # Build issues HTML
    issues_html = ""
    for i, issue in enumerate(issues, 1):
        severity = issue.get("severity", "INFO")
        category = issue.get("category", "style")
        color = SEVERITY_COLORS.get(severity, "#888")
        bg = SEVERITY_BG.get(severity, "rgba(255,255,255,0.03)")
        icon = CATEGORY_ICONS.get(category, "◆")
        line = issue.get("line")
        line_str = f"L{line}" if line else "—"

        issues_html += f"""
        <div class="issue" style="--accent:{color};--bg:{bg}">
            <div class="issue-meta">
                <span class="issue-index">{i:02d}</span>
                <span class="issue-sev" style="color:{color}">{severity}</span>
                <span class="issue-cat">{icon} {category}</span>
                <span class="issue-line">{line_str}</span>
            </div>
            <p class="issue-msg">{issue.get('message', '')}</p>
            <div class="issue-fix">→ {issue.get('suggestion', '')}</div>
        </div>"""

    fixed_section = ""
    if fixed_code:
        fixed_section = f"""
        <section class="fixed-section">
            <div class="section-label">Suggested fix</div>
            <pre><code>{fixed_code}</code></pre>
        </section>"""

    score_pct = int((score / 10) * 283)  # circumference of circle r=45

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Review — {target}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg: #0a0a0a;
    --surface: #111111;
    --border: #1f1f1f;
    --text: #e2e2e2;
    --muted: #555;
    --mono: 'IBM Plex Mono', monospace;
    --sans: 'Inter', sans-serif;
  }}

  body {{
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 0 0 80px;
  }}

  /* ── TOP BAR ── */
  .topbar {{
    border-bottom: 1px solid var(--border);
    padding: 18px 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}
  .topbar-brand {{
    font-family: var(--mono);
    font-size: 13px;
    color: var(--muted);
    letter-spacing: 0.05em;
  }}
  .topbar-brand span {{ color: var(--text); }}
  .topbar-date {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
  }}

  /* ── HERO ── */
  .hero {{
    padding: 64px 48px 48px;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 40px;
    align-items: start;
    border-bottom: 1px solid var(--border);
  }}
  .hero-target {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 12px;
  }}
  .hero-summary {{
    font-size: 17px;
    font-weight: 300;
    line-height: 1.7;
    color: #c8c8c8;
    max-width: 560px;
  }}

  /* Score ring */
  .score-ring {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
  }}
  .score-ring svg {{ transform: rotate(-90deg); }}
  .score-ring-track {{ fill: none; stroke: var(--border); stroke-width: 3; }}
  .score-ring-fill {{
    fill: none;
    stroke: {score_color};
    stroke-width: 3;
    stroke-linecap: round;
    stroke-dasharray: 283;
    stroke-dashoffset: {283 - score_pct};
    transition: stroke-dashoffset 1s ease;
  }}
  .score-center {{
    position: absolute;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }}
  .score-wrap {{
    position: relative;
    width: 100px;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .score-num {{
    font-size: 28px;
    font-weight: 600;
    color: {score_color};
    font-family: var(--mono);
    line-height: 1;
  }}
  .score-denom {{
    font-size: 11px;
    color: var(--muted);
    font-family: var(--mono);
  }}
  .score-verdict {{
    font-size: 11px;
    color: {score_color};
    font-family: var(--mono);
    letter-spacing: 0.06em;
  }}

  /* ── STATS BAR ── */
  .statsbar {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    border-bottom: 1px solid var(--border);
  }}
  .stat {{
    padding: 28px 48px;
    border-right: 1px solid var(--border);
  }}
  .stat:last-child {{ border-right: none; }}
  .stat-n {{
    font-family: var(--mono);
    font-size: 32px;
    font-weight: 500;
    line-height: 1;
    margin-bottom: 6px;
  }}
  .stat-l {{
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}

  /* ── ISSUES ── */
  .issues-section {{
    padding: 48px;
  }}
  .section-label {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 24px;
  }}

  .issue {{
    background: var(--bg);
    background: var(--bg);
    border: 1px solid var(--border);
    border-left: 2px solid var(--accent);
    border-radius: 4px;
    padding: 20px 24px;
    margin-bottom: 10px;
    background: var(--bg);
  }}
  .issue-meta {{
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 10px;
  }}
  .issue-index {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
  }}
  .issue-sev {{
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.06em;
  }}
  .issue-cat {{
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.04em;
  }}
  .issue-line {{
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    margin-left: auto;
  }}
  .issue-msg {{
    font-size: 14px;
    color: var(--text);
    line-height: 1.55;
    margin-bottom: 10px;
  }}
  .issue-fix {{
    font-size: 13px;
    color: var(--muted);
    line-height: 1.5;
    padding-left: 0;
  }}

  /* ── FIXED CODE ── */
  .fixed-section {{
    padding: 0 48px 48px;
  }}
  pre {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 28px;
    overflow-x: auto;
    font-family: var(--mono);
    font-size: 13px;
    line-height: 1.7;
    color: #a3e635;
  }}

  /* ── FOOTER ── */
  .footer {{
    padding: 24px 48px 0;
    border-top: 1px solid var(--border);
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
  }}
</style>
</head>
<body>

<div class="topbar">
  <div class="topbar-brand">code-review-agent / <span>report</span></div>
  <div class="topbar-date">{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
</div>

<div class="hero">
  <div>
    <div class="hero-target">{target}</div>
    <p class="hero-summary">{summary}</p>
  </div>
  <div class="score-ring">
    <div class="score-wrap">
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle class="score-ring-track" cx="50" cy="50" r="45"/>
        <circle class="score-ring-fill" cx="50" cy="50" r="45"/>
      </svg>
      <div class="score-center">
        <span class="score-num">{score}</span>
        <span class="score-denom">/10</span>
      </div>
    </div>
    <span class="score-verdict">{score_label}</span>
  </div>
</div>

<div class="statsbar">
  <div class="stat">
    <div class="stat-n" style="color:#f87171">{high}</div>
    <div class="stat-l">High</div>
  </div>
  <div class="stat">
    <div class="stat-n" style="color:#fb923c">{medium}</div>
    <div class="stat-l">Medium</div>
  </div>
  <div class="stat">
    <div class="stat-n" style="color:#facc15">{low}</div>
    <div class="stat-l">Low</div>
  </div>
  <div class="stat">
    <div class="stat-n" style="color:#60a5fa">{info}</div>
    <div class="stat-l">Info</div>
  </div>
</div>

<section class="issues-section">
  <div class="section-label">{len(issues)} issue{'s' if len(issues) != 1 else ''} found</div>
  {issues_html}
</section>

{fixed_section}

<div class="footer">
  Pylint · Bandit · llama-3.3-70b-versatile via Groq
</div>

</body>
</html>"""
    return html


def save_report(report: dict, target: str, output_path: str = "report.html"):
    html = generate_html_report(report, target)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n📄 Report saved → {output_path}")
    return output_path