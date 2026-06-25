import base64
import json
import os
import sys
import urllib.error
import urllib.request


def text_node(text):
    return {"type": "text", "text": text}


def paragraph(text):
    return {"type": "paragraph", "content": [text_node(text)] if text else []}


def build_description(repo_full, issue_number, issue_url, body):
    content = [paragraph(f"Aberto via GitHub: {repo_full}#{issue_number} ({issue_url})")]
    for chunk in (body or "(sem descrição)").split("\n\n"):
        chunk = chunk.strip()
        if chunk:
            content.append(paragraph(chunk.replace("\n", " ")))
    return {"type": "doc", "version": 1, "content": content}


def main():
    base_url = os.environ["JIRA_BASE_URL"].rstrip("/")
    email = os.environ["JIRA_EMAIL"]
    token = os.environ["JIRA_API_TOKEN"]
    prefix = os.environ["PREFIX"]
    repo_name = os.environ["REPO_NAME"]
    repo_full = os.environ["REPO_FULL"]
    issue_number = os.environ["ISSUE_NUMBER"]
    issue_title = os.environ["ISSUE_TITLE"]
    issue_body = os.environ.get("ISSUE_BODY", "")
    issue_url = os.environ["ISSUE_URL"]
    project = os.environ["PROJECT"]
    issuetype = os.environ["ISSUETYPE"]

    label = f"gh-{repo_name}-{issue_number}"
    summary = f"{prefix} {issue_title}".strip()[:255]

    payload = {
        "fields": {
            "project": {"key": project},
            "summary": summary,
            "issuetype": {"name": issuetype},
            "description": build_description(repo_full, issue_number, issue_url, issue_body),
            "labels": [label],
        }
    }

    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    req = urllib.request.Request(
        f"{base_url}/rest/api/3/issue",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(e.read().decode(), file=sys.stderr)
        raise

    key = result["key"]
    print(f"Criado: {key}")

    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as f:
            f.write(f"jira_key={key}\n")


if __name__ == "__main__":
    main()
