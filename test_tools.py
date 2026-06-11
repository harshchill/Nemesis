from agent.graph import build_graph

# repo = "harshchill/Vault"
# pr_number = 4

# print("--- PR INFO ---")
# info = get_pr_info(repo, pr_number)
# print(info)

# print("\n--- PR FILES ---")
# files = get_pr_files(repo, pr_number)
# for f in files:
#     print(f["filename"], "|", f["status"], "| patch length:", len(f["patch"]))

# fake_state = {"repo": "harshchill/Vault", "pr_number": 4}

# state_after_node1 = fetch_pr_info_node(fake_state)
# print(state_after_node1)

# fake_state.update(state_after_node1)
# state_after_node2 = fetch_files_node(fake_state)
# print(state_after_node2)

graph = build_graph()
result = graph.invoke({
    "repo": "harshchill/Vault",
    "pr_number": 4
})

for r in result["file_reviews"]:
    print(f"\n=== {r['filename']} ===")
    print(r["review"])