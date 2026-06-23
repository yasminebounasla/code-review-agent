import json
import os
from dotenv import load_dotenv
from groq import Groq
from tools import TOOLS_DEFINITIONS, execute_tool

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ============================================================
# SYSTEM PROMPT — la personnalité et les instructions de l'agent
# ============================================================

SYSTEM_PROMPT = """You are an expert code reviewer acting as a senior developer.

Your job is to thoroughly review code using the tools available to you.

ALWAYS follow this process:
1. First, read the file or fetch the PR to see the code
2. Run pylint to detect style and quality issues
3. Run bandit to detect security vulnerabilities
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
  "fixed_code": "<the corrected version of the code as a string>"
}

Return ONLY the JSON object. No markdown, no explanation outside the JSON."""


# ============================================================
# LA BOUCLE AGENTIQUE — le coeur du projet
# ============================================================

def run_agent(target: str) -> dict:
    """
    target : soit un filepath local (ex: "sample.py")
              soit une URL GitHub PR (ex: "https://github.com/owner/repo/pull/1")
    
    Retourne le rapport final en dict Python.
    """

    # Message initial à l'agent — on lui dit juste quoi reviewer
    # C'est lui qui décide comment faire
    if target.startswith("http"):
        user_message = f"Please review this GitHub Pull Request: {target}"
    else:
        user_message = f"Please review this Python file: {target}"

    # L'historique de la conversation — on accumule tout ici
    # C'est comme ça que le LLM "se souvient" de ce qu'il a fait
    messages = [
        {"role": "user", "content": user_message}
    ]

    print(f"\n🤖 Agent started — target: {target}")
    print("=" * 60)

    # ---- LA BOUCLE ----
    # On tourne jusqu'à ce que l'agent décide qu'il a fini
    # (quand il répond sans demander d'outil = réponse finale)
    
    max_iterations = 10  # sécurité pour éviter une boucle infinie
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n🔄 Iteration {iteration}...")

        # Appel au LLM avec les outils disponibles
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            tools=TOOLS_DEFINITIONS,
            tool_choice="auto",  # le LLM décide seul s'il veut un outil ou pas
            temperature=0.3,
            max_tokens=4000
        )

        message = response.choices[0].message

        # ---- CAS 1 : le LLM veut utiliser un outil ----
        if message.tool_calls:
            
            # Ajouter la décision du LLM à l'historique
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

            # Exécuter chaque outil demandé
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(f"  🔧 Tool called: {tool_name}({tool_args})")

                # Exécuter l'outil réel
                tool_result = execute_tool(tool_name, tool_args)

                # Convertir le résultat en string si c'est pas déjà le cas
                if not isinstance(tool_result, str):
                    tool_result = json.dumps(tool_result, indent=2)

                print(f"  ✅ Tool result: {tool_result[:100]}...")  # affiche juste le début

                # Ajouter le résultat de l'outil à l'historique
                # Le LLM va lire ça dans la prochaine itération
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

        # ---- CAS 2 : le LLM a fini, il donne sa réponse finale ----
        else:
            print("\n✅ Agent finished — parsing final report...")
            
            final_text = message.content or ""

            # Nettoyer au cas où le LLM met des backticks markdown
            clean = final_text.replace("```json", "").replace("```", "").strip()

            try:
                report = json.loads(clean)
                return report
            except json.JSONDecodeError:
                # Si le JSON est cassé, retourner un rapport d'erreur
                return {
                    "score": 0,
                    "summary": "Agent failed to produce a valid JSON report.",
                    "issues": [],
                    "fixed_code": "",
                    "raw_output": final_text
                }

    # Si on dépasse max_iterations
    return {
        "score": 0,
        "summary": "Agent exceeded maximum iterations.",
        "issues": [],
        "fixed_code": ""
    }