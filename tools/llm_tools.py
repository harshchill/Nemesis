from config.setting import getLLM
from prompts.review_prompt import review_prompt
from prompts.summary_prompt import summary_prompt

llm = getLLM()
chain = review_prompt | llm
summary_chain = summary_prompt | llm

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

def generate_summary(file_reviews:list,pr_info:dict)->str:
    all_reviews = "\n\n".join([
        f"File: {r['filename']}\n{r['review']}"
        for r in file_reviews
        ])
    response = summary_chain.invoke({
        "pr_title": pr_info["title"],
        "all_reviews": all_reviews
    })
     
    return response.content
    
    
    