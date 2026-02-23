import os

MAX_CHARS = 12000

def collect_files(repo_path: str):
    collected = []
    for root, dirs, files in os.walk(repo_path):
        if ".git" in root or "node_modules" in root or "__pycache__" in root:
            continue

        for f in files:
            if f.endswith((".py", ".js", ".ts", ".tsx", ".md", ".json")):
                full_path = os.path.join(root, f)
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as fh:
                        content = fh.read()
                        collected.append((full_path, content))
                except Exception:
                    pass
    return collected

def build_prompt(files):
    prompt = "You are an expert software engineer. Generate a clean, professional README and architecture overview for this project.\n\n"
    total = 0
    for path, content in files:
        snippet = content[:2000]
        block = f"\n### File: {path}\n{snippet}\n"
        if total + len(block) > MAX_CHARS:
            break
        prompt += block
        total += len(block)
    return prompt
