import json
import os
from dotenv import load_dotenv
from groq import Groq
from tools import TOOLS_DEFINITIONS, execute_tool

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert code reviewer acting as a senior developer.

Your job is to thoroughly review code using the tools available to you.

ALWAYS follow this process:
1. First, read the file or directory to see the code (use read_file for a single file, read_directory for a folder, fetch_github_pr for a PR URL)
2. Run pylint to detect style and quality issues (use run_pylint for a file, run_pylint_directory for a folder)
3. Run bandit to detect security vulnerabilities (use run_bandit for a file, run_bandit_directory for a folder)
4. Reason over everything you found — what did the tools miss? logic bugs? edge cases? bad architecture?
5. Produce a final structured JSON report

Your final response MUST be a valid JSON object with this exact structure:
{
  "score": <number between 0 and 10>,
  "summary": "<2-3 sentences overview of the code quality>",
  "issues": [
    {
      "line": <line number or null>,
      "severity": "HIGH" | "MEDIUM" | "LOW" | "INFO",
      "category": "security" | "bug" | "logic" | "style" | "performance",
      "message": "<clear explanation of the issue>",
      "suggestion": "<how to fix it>"
    }
  ],
  "fixed_code": "<the corrected version of the code as a string, or empty string if multiple files>"
}

Return ONLY the JSON object. No markdown, no explanation outside the JSON."""


def run_agent(target: str) -> dict:
    """
    target : filepath, directory path, or GitHub PR URL
    """
    if target.startswith("http"):
        user_message = f"Please review this GitHub Pull Request: {target}"
    elif os.path.isdir(target):
        user_message = f"Please review all Python files in this directory: {target}"
    else:
        user_message = f"Please review this Python file: {target}"

    messages = [{"role": "user", "content": user_message}]

    print(f"\n🤖 Agent started — target: {target}")
    print("=" * 60)

    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n🔄 Iteration {iteration}...")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            tools=TOOLS_DEFINITIONS,
            tool_choice="auto",
            temperature=0.3,
            max_tokens=4000
        )

        message = response.choices[0].message

        if message.tool_calls:
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            })

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(f"  🔧 Tool called: {tool_name}({tool_args})")

                tool_result = execute_tool(tool_name, tool_args)

                if not isinstance(tool_result, str):
                    tool_result = json.dumps(tool_result, indent=2)

                print(f"  ✅ Tool result: {tool_result[:100]}...")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

        else:
            print("\n✅ Agent finished — parsing final report...")

            final_text = message.content or ""
            clean = final_text.replace("```json", "").replace("```", "").strip()

            try:
                report = json.loads(clean)
                return report
            except json.JSONDecodeError:
                return {
                    "score": 0,
                    "summary": "Agent failed to produce a valid JSON report.",
                    "issues": [],
                    "fixed_code": "",
                    "raw_output": final_text
                }

    return {
        "score": 0,
        "summary": "Agent exceeded maximum iterations.",
        "issues": [],
        "fixed_code": ""
    }