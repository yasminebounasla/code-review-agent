import subprocess
import json
import sys
import urllib.request

# ============================================================
# LES OUTILS — fonctions Python que l'agent peut utiliser
# ============================================================

def read_file(filepath: str) -> str:
    """
    Lit le contenu d'un fichier et le retourne comme string.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"ERROR: fichier '{filepath}' introuvable"
    except Exception as e:
        return f"ERROR: {str(e)}"


def run_pylint(filepath: str) -> list:
    """
    Lance Pylint sur un fichier et retourne les issues en JSON.
    Pylint analyse : style, imports inutiles, variables non utilisées, etc.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pylint", filepath, "--output-format=json"],
        capture_output=True,
        text=True
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        return []


def run_bandit(filepath: str) -> dict:
    """
    Lance Bandit sur un fichier et retourne les issues de sécurité en JSON.
    Bandit détecte : passwords hardcodés, injections SQL, fonctions dangereuses, etc.
    """
    result = subprocess.run(
        [sys.executable, "-m", "bandit", filepath, "-f", "json", "-q"],
        capture_output=True,
        text=True
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        return {}


def fetch_github_pr(pr_url: str) -> str:
    """
    Fetche le diff d'une Pull Request GitHub via l'API.
    Exemple d'URL : https://github.com/owner/repo/pull/123
    Retourne le diff en texte brut.
    """
    try:
        # Convertir l'URL normale en URL API
        # https://github.com/owner/repo/pull/123
        # → https://api.github.com/repos/owner/repo/pulls/123
        parts = pr_url.replace("https://github.com/", "").split("/")
        owner = parts[0]
        repo = parts[1]
        pr_number = parts[3]

        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

        # Fetcher le diff
        req = urllib.request.Request(
            api_url,
            headers={
                "Accept": "application/vnd.github.v3.diff",
                "User-Agent": "code-review-agent"
            }
        )
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")

    except Exception as e:
        return f"ERROR: impossible de fetcher la PR — {str(e)}"


# ============================================================
# DÉFINITIONS JSON des outils — ce qu'on donne au LLM
# pour qu'il sache quels outils existent et comment les utiliser
# ============================================================

TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lit le contenu d'un fichier Python local. Utilise cet outil en premier pour lire le code à reviewer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Le chemin vers le fichier Python à lire"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_pylint",
            "description": "Lance Pylint sur un fichier Python pour détecter les problèmes de style, imports inutiles, variables non utilisées, mauvaises pratiques.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Le chemin vers le fichier Python à analyser"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_bandit",
            "description": "Lance Bandit sur un fichier Python pour détecter les failles de sécurité : passwords hardcodés, injections, fonctions dangereuses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Le chemin vers le fichier Python à analyser"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_github_pr",
            "description": "Fetche le diff d'une Pull Request GitHub. Utilise cet outil quand l'input est une URL GitHub PR.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pr_url": {
                        "type": "string",
                        "description": "L'URL complète de la PR GitHub, ex: https://github.com/owner/repo/pull/123"
                    }
                },
                "required": ["pr_url"]
            }
        }
    }
]


# ============================================================
# DISPATCHER — exécute l'outil demandé par le LLM
# ============================================================

def execute_tool(tool_name: str, tool_args: dict):
    """
    Reçoit le nom de l'outil et ses arguments (décidés par le LLM),
    exécute la bonne fonction, retourne le résultat.
    """
    if tool_name == "read_file":
        return read_file(tool_args["filepath"])
    elif tool_name == "run_pylint":
        return run_pylint(tool_args["filepath"])
    elif tool_name == "run_bandit":
        return run_bandit(tool_args["filepath"])
    elif tool_name == "fetch_github_pr":
        return fetch_github_pr(tool_args["pr_url"])
    else:
        return f"ERROR: outil '{tool_name}' inconnu"