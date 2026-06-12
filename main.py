from agent.graph import build_graph

graph = build_graph()

result = graph.invoke({
   "repo": "harshchill/prepdom",
    "pr_number": 7
})