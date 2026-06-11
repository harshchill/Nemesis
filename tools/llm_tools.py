from config.setting import getLLM
from prompts.review_prompt import review_prompt

llm = getLLM()
chain = review_prompt | llm

def analyze_file(file:dict ,pr_info:dict)->str:
    diff = file["patch"]
    if not diff:
        return "No diff avaliable - skipped"
    if len(diff) > 6000:
        diff = diff[:6000] + "\n... [truncated]"

    response = chain.invoke({
        "pr_title":pr_info["title"],
        "filename":file["filename"],
        "status":file["status"],
        "diff":diff
    })
    return response.content