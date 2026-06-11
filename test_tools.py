from tools.github_tools import get_pr_files ,get_pr_info

repo = "harshchill/Vault"
pr_number = 4

print("--- PR INFO ---")
info = get_pr_info(repo, pr_number)
print(info)

print("\n--- PR FILES ---")
files = get_pr_files(repo, pr_number)
for f in files:
    print(f["filename"], "|", f["status"], "| patch length:", len(f["patch"]))