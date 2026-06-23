import json
from datetime import datetime

# ============================================================
# COULEURS PAR SÉVÉRITÉ
# ============================================================

SEVERITY_COLORS = {
    "HIGH":   "#ff4d4d",
    "MEDIUM": "#ff9900",
    "LOW":    "#ffd700",
    "INFO":   "#4d94ff"
}

CATEGORY_ICONS = {
    "security":    "🔒",
    "bug":         "🐛",
    "logic":       "🧠",
    "style":       "✏️",
    "performance": "⚡"
}

# ============================================================
# GÉNÉRATION DU RAPPORT HTML
# ============================================================

def generate_html_report(report: dict, target: str) -> str:
    """
    Prend le dict retourné par l'agent et génère un fichier HTML lisible.
    """

    score = report.get("score", 0)
    summary = report.get("summary", "")
    issues = report.get("issues", [])
    fixed_code = report.get("fixed_code", "")

    # Couleur du score selon la valeur
    if score >= 7:
        score_color = "#4caf50"   # vert
    elif score >= 4:
        score_color = "#ff9900"   # orange
    else:
        score_color = "#ff4d4d"   # rouge

    # Générer les cartes d'issues
    issues_html = ""
    for i, issue in enumerate(issues, 1):
        severity = issue.get("severity", "INFO")
        category = issue.get("category", "style")
        color = SEVERITY_COLORS.get(severity, "#888")
        icon = CATEGORY_ICONS.get(category, "📌")

        issues_html += f"""
        <div class="issue-card" style="border-left: 4px solid {color}">
            <div class="issue-header">
                <span class="issue-number">#{i}</span>
                <span class="badge" style="background:{color}">{severity}</span>
                <span class="category">{icon} {category.upper()}</span>
                <span class="line">Line {issue.get('line', 'N/A')}</span>
            </div>
            <p class="issue-message">{issue.get('message', '')}</p>
            <div class="suggestion">
                <strong>💡 Fix:</strong> {issue.get('suggestion', '')}
            </div>
        </div>
        """

    # Compter par sévérité
    high   = sum(1 for i in issues if i.get("severity") == "HIGH")
    medium = sum(1 for i in issues if i.get("severity") == "MEDIUM")
    low    = sum(1 for i in issues if i.get("severity") == "LOW")
    info   = sum(1 for i in issues if i.get("severity") == "INFO")

    # HTML complet
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Review Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #0d0d0d;
            color: #e0e0e0;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        /* HEADER */
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}

        .header h1 {{
            font-size: 2rem;
            color: #fff;
            margin-bottom: 8px;
        }}

        .header .target {{
            color: #888;
            font-size: 0.9rem;
            font-family: monospace;
        }}

        .header .date {{
            color: #555;
            font-size: 0.8rem;
            margin-top: 4px;
        }}

        /* SCORE */
        .score-section {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 30px;
            background: #1a1a1a;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
        }}

        .score-circle {{
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: 4px solid {score_color};
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}

        .score-number {{
            font-size: 2rem;
            font-weight: bold;
            color: {score_color};
        }}

        .score-label {{
            font-size: 0.7rem;
            color: #888;
        }}

        .summary {{
            flex: 1;
            color: #ccc;
            line-height: 1.6;
            font-size: 0.95rem;
        }}

        /* STATS */
        .stats {{
            display: flex;
            gap: 12px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            flex: 1;
            background: #1a1a1a;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }}

        .stat-number {{
            font-size: 1.8rem;
            font-weight: bold;
        }}

        .stat-label {{
            font-size: 0.75rem;
            color: #888;
            margin-top: 4px;
        }}

        /* ISSUES */
        .section-title {{
            font-size: 1.1rem;
            color: #fff;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #222;
        }}

        .issue-card {{
            background: #1a1a1a;
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 12px;
        }}

        .issue-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }}

        .issue-number {{
            color: #555;
            font-size: 0.85rem;
            font-family: monospace;
        }}

        .badge {{
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: bold;
            color: #000;
        }}

        .category {{
            font-size: 0.8rem;
            color: #aaa;
        }}

        .line {{
            margin-left: auto;
            font-size: 0.8rem;
            color: #555;
            font-family: monospace;
        }}

        .issue-message {{
            color: #ddd;
            font-size: 0.9rem;
            margin-bottom: 10px;
            line-height: 1.5;
        }}

        .suggestion {{
            background: #111;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 0.85rem;
            color: #aaa;
            line-height: 1.5;
        }}

        /* FIXED CODE */
        .fixed-code-section {{
            margin-top: 30px;
        }}

        pre {{
            background: #111;
            border-radius: 12px;
            padding: 20px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            line-height: 1.6;
            color: #a8ff78;
            border: 1px solid #222;
        }}

        /* FOOTER */
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #333;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
<div class="container">

    <div class="header">
        <h1>🔍 Code Review Report</h1>
        <div class="target">{target}</div>
        <div class="date">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
    </div>

    <div class="score-section">
        <div class="score-circle">
            <span class="score-number">{score}</span>
            <span class="score-label">/ 10</span>
        </div>
        <div class="summary">{summary}</div>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-number" style="color:#ff4d4d">{high}</div>
            <div class="stat-label">HIGH</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="color:#ff9900">{medium}</div>
            <div class="stat-label">MEDIUM</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="color:#ffd700">{low}</div>
            <div class="stat-label">LOW</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="color:#4d94ff">{info}</div>
            <div class="stat-label">INFO</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" style="color:#fff">{len(issues)}</div>
            <div class="stat-label">TOTAL</div>
        </div>
    </div>

    <div class="issues-section">
        <div class="section-title">⚠️ Issues Found ({len(issues)})</div>
        {issues_html}
    </div>

    {"" if not fixed_code else f'''
    <div class="fixed-code-section">
        <div class="section-title">✅ Suggested Fixed Code</div>
        <pre>{fixed_code}</pre>
    </div>
    '''}

    <div class="footer">
        Generated by Code Review Agent — Pylint + Bandit + LLM
    </div>

</div>
</body>
</html>"""

    return html


def save_report(report: dict, target: str, output_path: str = "report.html"):
    """
    Génère et sauvegarde le rapport HTML dans un fichier.
    """
    html = generate_html_report(report, target)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n📄 Report saved → {output_path}")
    return output_path