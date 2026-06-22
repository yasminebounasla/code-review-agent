import subprocess
import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run_pylint(filepath):
    result = subprocess.run(
        ["pylint", filepath, "--output-format=json"],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except:
        return []

def run_bandit(filepath):
    result = subprocess.run(
        ["bandit", filepath, "-f", "json", "-q"],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except:
        return {}

def review_with_llm(code, pylint_issues, bandit_issues):
    prompt = f"""
You are a senior developer doing a code review.

Here is the code to review:
```python
{code}
```

Static analysis tools found these issues:

PYLINT:
{json.dumps(pylint_issues, indent=2)}

BANDIT (security):
{json.dumps(bandit_issues, indent=2)}

Your job:
1. Analyze the tools' findings
2. Find additional issues the tools missed (logic bugs, edge cases, bad practices)
3. Return ONLY a JSON array, no markdown, no explanation outside the JSON.

Each issue must follow this exact format:
{{
  "line": <line number or null>,
  "severity": "HIGH" | "MEDIUM" | "LOW" | "INFO",
  "category": "security" | "bug" | "style" | "performance" | "logic",
  "message": "clear explanation of the issue",
  "suggestion": "how to fix it"
}}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content


def display_report(issues_json, filepath):
    print(f"\n{'='*60}")
    print(f"  CODE REVIEW REPORT : {filepath}")
    print(f"{'='*60}\n")
    
    try:
        issues = json.loads(issues_json)
    except:
        clean = issues_json.replace("```json", "").replace("```", "").strip()
        issues = json.loads(clean)
    
    for i, issue in enumerate(issues, 1):
        severity = issue.get("severity", "INFO")
        print(f"[{severity}] Issue #{i} — {issue.get('category', '').upper()}")
        print(f"  Line     : {issue.get('line', 'N/A')}")
        print(f"  Problem  : {issue.get('message')}")
        print(f"  Fix      : {issue.get('suggestion')}")
        print()

        
def main():
    filepath = "sample.py"
    
    with open(filepath, "r") as f:
        code = f.read()
    
    print("Running Pylint...")
    pylint_issues = run_pylint(filepath)
    
    print("Running Bandit...")
    bandit_issues = run_bandit(filepath)
    
    print("Asking LLM for deeper analysis...")
    llm_output = review_with_llm(code, pylint_issues, bandit_issues)
    
    display_report(llm_output, filepath)

if __name__ == "__main__":
    main()