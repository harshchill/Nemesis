from langgraph.graph import StateGraph,END
from agent.state import PRReviewState
from agent.nodes import fetch_files_node,fetch_pr_info_node,analyze_file_node


def build_graph():
    workflow = StateGraph(PRReviewState)

    workflow.add_node("fetch_pr_info",fetch_pr_info_node)
    workflow.add_node("fetch_files",fetch_files_node)
    workflow.add_node("analyze_files",analyze_file_node)

    workflow.set_entry_point("fetch_pr_info")
    workflow.add_edge("fetch_pr_info" , "fetch_files")
    workflow.add_edge("fetch_files","analyze_files")
    workflow.add_edge("analyze_files", END)

    return workflow.compile()