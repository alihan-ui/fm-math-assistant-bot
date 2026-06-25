"""
Автокоммит materials.json в GitHub через REST Contents API.
Не использует git-бинарник — работает прямым HTTP-запросом к GitHub,
что надёжнее в контейнере Render (нет нужды настраивать git config/ssh-ключи).

Нужны переменные окружения:
  GITHUB_TOKEN   — Personal Access Token с правом "repo" (Contents: Read & Write)
  GITHUB_REPO    — "alihan-ui/fm-math-assistant-bot" (owner/repo)
  GITHUB_BRANCH  — "main" (опционально, по умолчанию main)
"""
import os
import base64
import requests

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO", "alihan-ui/fm-math-assistant-bot")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")


class GithubCommitError(Exception):
    pass


def _headers():
    if not GITHUB_TOKEN:
        raise GithubCommitError("GITHUB_TOKEN орнатылмаған (env variable жоқ)")
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def commit_file(path_in_repo: str, content_bytes: bytes, commit_message: str) -> dict:
    """
    Создаёт/обновляет один файл в репозитории через Contents API.
    GitHub Contents API сам делает commit + push за один вызов — нам не нужен
    локальный git-репозиторий внутри контейнера бота.
    """
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path_in_repo}"

    # Узнаём текущий sha файла (нужен GitHub'у чтобы не было конфликта параллельных правок)
    resp = requests.get(url, headers=_headers(), params={"ref": GITHUB_BRANCH}, timeout=15)
    sha = None
    if resp.status_code == 200:
        sha = resp.json().get("sha")
    elif resp.status_code not in (404,):
        raise GithubCommitError(f"GitHub GET қатесі: {resp.status_code} {resp.text[:200]}")

    payload = {
        "message": commit_message,
        "content": base64.b64encode(content_bytes).decode("utf-8"),
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    put_resp = requests.put(url, headers=_headers(), json=payload, timeout=15)
    if put_resp.status_code not in (200, 201):
        raise GithubCommitError(f"GitHub PUT қатесі: {put_resp.status_code} {put_resp.text[:300]}")

    return put_resp.json()


def commit_materials_json(local_path: str, material_label: str) -> str:
    """
    Коммитит локальный materials.json в GitHub.
    Возвращает короткое сообщение об успехе для показа админу в Telegram.
    """
    with open(local_path, "rb") as f:
        content = f.read()

    commit_message = f"Материал қосылды: {material_label}"
    result = commit_file("materials.json", content, commit_message)
    commit_sha = result.get("commit", {}).get("sha", "")[:7]
    return commit_sha
