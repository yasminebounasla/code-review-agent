import argparse
import sys
import os
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
  python cli.py review https://github.com/owner/repo/pull/123
  python cli.py review sample.py --output my_report.html
        """
    )

    subparsers = parser.add_subparsers(dest="command")

    # Commande "review"
    review_parser = subparsers.add_parser("review", help="Review a file or GitHub PR")
    review_parser.add_argument(
        "target",
        help="Path to a Python file OR a GitHub PR URL"
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

    args = parser.parse_args()

    # Si aucune commande donnée → afficher l'aide
    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "review":
        target = args.target

        # Vérifier que le fichier existe si c'est un fichier local
        if not target.startswith("http") and not os.path.exists(target):
            print(f"❌ Error: file '{target}' not found")
            sys.exit(1)

        # Lancer l'agent
        print(f"\n🚀 Starting Code Review Agent...")
        print(f"📂 Target: {target}")

        report = run_agent(target)

        # Afficher le résumé dans le terminal
        print("\n" + "=" * 60)
        print(f"  SCORE : {report.get('score', 'N/A')}/10")
        print(f"  SUMMARY : {report.get('summary', '')}")
        print(f"  ISSUES FOUND : {len(report.get('issues', []))}")
        print("=" * 60)

        # Sauvegarder le rapport HTML
        if not args.no_html:
            output_path = save_report(report, target, args.output)
            print(f"✅ Open '{output_path}' in your browser to see the full report")


if __name__ == "__main__":
    main()