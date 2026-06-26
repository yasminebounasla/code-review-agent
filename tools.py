import subprocess
import json
import sys
import os
import urllib.request

# ============================================================
# LES OUTILS — fonctions Python que l'agent peut utiliser
# ============================================================

def read_file(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"ERROR: fichier '{filepath}' introuvable"
    except Exception as e:
        return f"ERROR: {str(e)}"


def read_directory(dirpath: str) -> str:
    """
    Lit tous les fichiers .py d'un dossier (récursif) et les retourne
    comme un seul string avec des séparateurs clairs.
    """
    py_files = []
    for root, dirs, files in os.walk(dirpath):
        # Ignorer les dossiers inutiles
        dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", "venv", ".venv", "node_modules"]]
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))

    if not py_files:
        return f"ERROR: aucun fichier .py trouvé dans '{dirpath}'"

    result = f"Found {len(py_files)} Python file(s):\n\n"
    for filepath in sorted(py_files):
        result += f"{'='*60}\n"
        result += f"FILE: {filepath}\n"
        result += f"{'='*60}\n"
        result += read_file(filepath)
        result += "\n\n"

    return result


def run_pylint(filepath: str) -> list:
    result = subprocess.run(
        [sys.executable, "-m", "pylint", filepath, "--output-format=json"],
        capture_output=True,
        text=True
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        return []


def run_pylint_directory(dirpath: str) -> list:
    """
    Lance Pylint sur tous les fichiers .py d'un dossier.
    """
    result = subprocess.run(
        [sys.executable, "-m", "pylint", dirpath, "--output-format=json", "--recursive=y"],
        capture_output=True,
        text=True
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        return []


def run_bandit(filepath: str) -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "bandit", filepath, "-f", "json", "-q"],
        capture_output=True,
        text=True
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        return {}


def run_bandit_directory(dirpath: str) -> dict:
    """
    Lance Bandit sur tous les fichiers .py d'un dossier (récursif).
    """
    result = subprocess.run(
        [sys.executable, "-m", "bandit", "-r", dirpath, "-f", "json", "-q"],
        capture_output=True,
        text=True
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        return {}


def fetch_github_pr(pr_url: str) -> str:
    try:
        parts = pr_url.replace("https://github.com/", "").split("/")
        owner = parts[0]
        repo = parts[1]
        pr_number = parts[3]

        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"

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
# DÉFINITIONS JSON des outils
# ============================================================

TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lit le contenu d'un fichier Python local. Utilise cet outil pour lire UN fichier spécifique.",
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
            "name": "read_directory",
            "description": "Lit tous les fichiers .py d'un dossier récursivement. Utilise cet outil quand le target est un dossier/répertoire.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dirpath": {
                        "type": "string",
                        "description": "Le chemin vers le dossier à analyser"
                    }
                },
                "required": ["dirpath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_pylint",
            "description": "Lance Pylint sur UN fichier Python pour détecter les problèmes de style, imports inutiles, variables non utilisées.",
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
            "name": "run_pylint_directory",
            "description": "Lance Pylint sur tous les fichiers .py d'un dossier récursivement. Utilise quand le target est un dossier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dirpath": {
                        "type": "string",
                        "description": "Le chemin vers le dossier à analyser"
                    }
                },
                "required": ["dirpath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_bandit",
            "description": "Lance Bandit sur UN fichier Python pour détecter les failles de sécurité.",
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
            "name": "run_bandit_directory",
            "description": "Lance Bandit sur tous les fichiers .py d'un dossier récursivement. Utilise quand le target est un dossier.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dirpath": {
                        "type": "string",
                        "description": "Le chemin vers le dossier à analyser"
                    }
                },
                "required": ["dirpath"]
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
# DISPATCHER
# ============================================================

def execute_tool(tool_name: str, tool_args: dict):
    if tool_name == "read_file":
        return read_file(tool_args["filepath"])
    elif tool_name == "read_directory":
        return read_directory(tool_args["dirpath"])
    elif tool_name == "run_pylint":
        return run_pylint(tool_args["filepath"])
    elif tool_name == "run_pylint_directory":
        return run_pylint_directory(tool_args["dirpath"])
    elif tool_name == "run_bandit":
        return run_bandit(tool_args["filepath"])
    elif tool_name == "run_bandit_directory":
        return run_bandit_directory(tool_args["dirpath"])
    elif tool_name == "fetch_github_pr":
        return fetch_github_pr(tool_args["pr_url"])
    else:
        return f"ERROR: outil '{tool_name}' inconnu"