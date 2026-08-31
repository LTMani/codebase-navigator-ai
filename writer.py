import os

def write_file(rel_path, content):
    full_path = os.path.join("t:/Git Project/codebase-navigator-ai", rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {rel_path} ({len(content.splitlines())} lines)")

if __name__ == "__main__":
    print("Writer initialized.")
