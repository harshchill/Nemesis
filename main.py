from agent.graph import build_graph

graph = build_graph()

result = graph.invoke({
   "repo": "harshchill/Vault",
    "pr_number": 4
})