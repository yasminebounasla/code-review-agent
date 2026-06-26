import argparse
import sys
import os
import json
from agent import run_agent
from report import save_report

# ============================================================
# CLI — interface en ligne de commande
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="🔍 Code Review Agent — AI-powered code reviewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py review sample.py
  python cli.py review my_project/
  python cli.py review https://github.com/owner/repo/pull/123
  python cli.py review sample.py --output my_report.html
  python cli.py review sample.py --json
  python cli.py review sample.py --no-html
        """
    )

    subparsers = parser.add_subparsers(dest="command")

    review_parser = subparsers.add_parser("review", help="Review a file, directory, or GitHub PR")
    review_parser.add_argument(
        "target",
        help="Path to a Python file, a directory, OR a GitHub PR URL"
    )
    review_parser.add_argument(
        "--output",
        default="report.html",
        help="Output HTML report filename (default: report.html)"
    )
    review_parser.add_argument(
        "--no-html",
        action="store_true",
        help="Print report to terminal only, don't save HTML"
    )
    review_parser.add_argument(
        "--json",
        action="store_true",
        help="Also save a JSON report (report.json)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "review":
        target = args.target

        # Validation : si c'est pas une URL, le fichier/dossier doit exister
        if not target.startswith("http") and not os.path.exists(target):
            print(f"❌ Error: '{target}' not found (not a file, directory, or valid URL)")
            sys.exit(1)

        # Info sur ce qu'on va reviewer
        if target.startswith("http"):
            print(f"\n🚀 Starting Code Review Agent...")
            print(f"🔗 Target: GitHub PR — {target}")
        elif os.path.isdir(target):
            py_count = sum(1 for _, _, files in os.walk(target) for f in files if f.endswith(".py"))
            print(f"\n🚀 Starting Code Review Agent...")
            print(f"📁 Target: directory — {target} ({py_count} Python file(s) found)")
        else:
            print(f"\n🚀 Starting Code Review Agent...")
            print(f"📄 Target: file — {target}")

        # Lancer l'agent
        report = run_agent(target)

        # Résumé terminal
        print("\n" + "=" * 60)
        print(f"  SCORE   : {report.get('score', 'N/A')}/10")
        print(f"  SUMMARY : {report.get('summary', '')}")
        print(f"  ISSUES  : {len(report.get('issues', []))} found")
        print("=" * 60)

        # Sauvegarder JSON si demandé
        if args.json:
            json_path = args.output.replace(".html", ".json") if args.output.endswith(".html") else "report.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📄 JSON report saved → {json_path}")

        # Sauvegarder HTML
        if not args.no_html:
            output_path = save_report(report, target, args.output)
            print(f"✅ Open '{output_path}' in your browser to see the full report")


if __name__ == "__main__":
    main()
