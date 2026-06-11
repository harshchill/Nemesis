from agent.state import PRReviewState
from tools.github_tools import get_pr_files,get_pr_info
from tools.llm_tools import analyze_file
import time
import os

SKIP_EXTENSIONS = ('.lock', '.min.js', '.min.css', '.svg', '.png', '.jpg', '.ico')
SKIP_FILENAMES = {'package-lock.json', 'yarn.lock', 'poetry.lock', 'Pipfile.lock'}

def should_skip(filename:str)-> bool:
    # 1. Check against the full filename for specific skip files
    base = os.path.basename(filename)
    if base in SKIP_FILENAMES:
        return True
    
    # 2. Check if the filename ends with any of the defined extensions
    # .endswith() accepts a tuple of strings
    if filename.lower().endswith(SKIP_EXTENSIONS):
        return True
        
    return False

def fetch_pr_info_node(state:PRReviewState )-> dict :
    print(f"  → Fetching PR #{state['pr_number']}...")
    info = get_pr_info(state["repo"],state["pr_number"])
    print(f"  → '{info['title']}' by @{info['author']}")
    return {"pr_info" : info}

def fetch_files_node(state:PRReviewState)->dict:
    print("  → Fetching changed files...")
    all_files = get_pr_files(state["repo"],state["pr_number"])
    files = [f for f in all_files if not should_skip(f["filename"])]

    skipped = len(all_files) - len (files)

    print(f"  → {len(files)} file(s) changed and {skipped} files skipped")
    return {
        "changed_files" : files
     }

def analyze_file_node(state:PRReviewState)->dict:
    print("--> Analyzing file with AI....")
    reviews=[]
    for i , file in enumerate(state["changed_files"]):
        print(f"     {i+1}/{len(state['changed_files'])}: {file['filename']}")
        review = analyze_file(file,state["pr_info"])
        reviews.append({
            "filename":file["filename"],
            "review":review
        })
        time.sleep(1)

    return {"file_reviews":reviews}
