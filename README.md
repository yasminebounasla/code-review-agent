# 🔍 Code Review Agent

An AI-powered code reviewer that combines static analysis tools with an LLM to produce structured, actionable code reviews — like having a senior developer look at your code.

## How it works

Most "AI code review" tools just paste your code into an LLM and print whatever it says. This agent is different: it's a proper **agentic loop** where the LLM decides which tools to use, reads their output, reasons over it, and produces a structured report.

```
You give it a file / folder / GitHub PR
        ↓
Agent reads the code (read_file or read_directory)
        ↓
Agent runs Pylint → gets deterministic style/quality issues
        ↓
Agent runs Bandit → gets deterministic security issues
        ↓
LLM reasons over everything: tool results + code logic
  → catches what tools missed: logic bugs, edge cases, bad architecture
        ↓
Structured JSON report → rendered as an HTML report
```

The key idea: **tools for precision, LLM for understanding.** Pylint and Bandit give exact line numbers and rule violations. The LLM catches the semantic issues they can't.

## Features

- ✅ Reviews single Python files
- ✅ Reviews entire directories (recursive, all `.py` files)
- ✅ Reviews GitHub Pull Requests (via GitHub API diff)
- ✅ Static analysis with **Pylint** (style, unused imports, bad practices)
- ✅ Security scanning with **Bandit** (hardcoded secrets, dangerous functions)
- ✅ LLM reasoning layer (logic bugs, edge cases, architecture issues)
- ✅ Structured output: score /10, severity levels, fix suggestions
- ✅ Visual HTML report (dark theme)
- ✅ Optional JSON export

## Setup

```bash
# Clone the repo
git clone https://github.com/yasminebounasla/code-review-agent
cd code-review-agent

# Install dependencies
pip install groq pylint bandit python-dotenv

# Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

## Usage

```bash
# Review a single file
python cli.py review sample.py

# Review an entire directory
python cli.py review my_project/

# Review a GitHub Pull Request
python cli.py review https://github.com/owner/repo/pull/123

# Custom output filename
python cli.py review sample.py --output my_report.html

# Print to terminal only (no HTML)
python cli.py review sample.py --no-html

# Also export JSON report
python cli.py review sample.py --json
```

## Example — reviewing real (bad) code

**Input** (`sample.py`):
```python
import os
import sys
password = "admin123"

def divide(a, b):
    return a / b

def unused_function():
    x = 5
    pass

result = divide(10, 0)
print(result)
```

**Terminal output:**
```
🤖 Agent started — target: sample.py
============================================================
🔄 Iteration 1...
  🔧 Tool called: read_file({'filepath': 'sample.py'})
  ✅ Tool result: import os...
🔄 Iteration 2...
  🔧 Tool called: run_pylint({'filepath': 'sample.py'})
  ✅ Tool result: [{"type": "warning"...
🔄 Iteration 3...
  🔧 Tool called: run_bandit({'filepath': 'sample.py'})
  ✅ Tool result: {"results": [{"issue_text": "Possible hardcoded...
🔄 Iteration 4...
✅ Agent finished — parsing final report...

============================================================
  SCORE   : 4/10
  SUMMARY : The code has a hardcoded password, unhandled division
            by zero, unused imports, and an unused function.
  ISSUES  : 5 found
============================================================
📄 Report saved → report.html
```

**Issues found:**

| # | Severity | Category | Line | Issue |
|---|----------|----------|------|-------|
| 1 | 🔴 HIGH | Security | 3 | Hardcoded password — use environment variables |
| 2 | 🟠 MEDIUM | Bug | 5 | No ZeroDivisionError handling in `divide()` |
| 3 | 🟡 LOW | Style | 1 | Unused import `os` |
| 4 | 🟡 LOW | Style | 1 | Unused import `sys` |
| 5 | 🟡 LOW | Style | 8 | Unused function `unused_function` |

The HTML report also includes the corrected version of the code.

## Project structure

```
code-review-agent/
├── agent.py      # Agentic loop — the core logic
├── tools.py      # Tool implementations + JSON definitions for the LLM
├── report.py     # HTML report generator
├── cli.py        # CLI interface (argparse)
├── sample.py     # Deliberately buggy file for testing
├── .env          # Your GROQ_API_KEY (not committed)
└── README.md
```

## Tech stack

| Component         | Tool                                 |
|-------------------|--------------------------------------|
| LLM               | Groq API — `llama-3.3-70b-versatile` |
| Style analysis    | Pylint                               |
| Security analysis | Bandit                               |
| CLI               | argparse (stdlib)                    |
| HTTP              | urllib (stdlib)                      |
| Config            | python-doten                         |

Groq was chosen for its speed — the agent makes multiple LLM calls per review (one per iteration), so latency matters. `llama-3.3-70b-versatile` gives a good balance of reasoning quality and speed.

