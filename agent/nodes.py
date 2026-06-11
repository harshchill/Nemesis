from agent.state import PRReviewState
from tools.github_tools import get_pr_files, get_pr_info, post_review
from tools.llm_tools import analyze_file
import time
import os

SKIP_EXTENSIONS = (".lock", ".min.js", ".min.css", ".svg", ".png", ".jpg", ".ico")
SKIP_FILENAMES = {"package-lock.json", "yarn.lock", "poetry.lock", "Pipfile.lock"}


def should_skip(filename: str) -> bool:
    base = os.path.basename(filename)
    if base in SKIP_FILENAMES:
        return True

    if filename.lower().endswith(SKIP_EXTENSIONS):
        return True

    return False


def fetch_pr_info_node(state: PRReviewState) -> dict:
    print(f"  > Fetching PR #{state['pr_number']}...")
    info = get_pr_info(state["repo"], state["pr_number"])
    print(f"  > '{info['title']}' by @{info['author']}")
    return {"pr_info": info}


def fetch_files_node(state: PRReviewState) -> dict:
    print("  > Fetching changed files...")
    all_files = get_pr_files(state["repo"], state["pr_number"])
    files = [f for f in all_files if not should_skip(f["filename"])]

    skipped = len(all_files) - len(files)

    print(f"  > {len(files)} file(s) queued, {skipped} skipped")
    return {"changed_files": files}


def analyze_file_node(state: PRReviewState) -> dict:
    print("> Running review analysis...")
    reviews = []
    for i, file in enumerate(state["changed_files"]):
        print(f"    [{i + 1}/{len(state['changed_files'])}] {file['filename']}")
        review = analyze_file(file, state["pr_info"])
        reviews.append(
            {
                "filename": file["filename"],
                "review": review,
            }
        )
        time.sleep(1)

    return {"file_reviews": reviews}


def generate_summary_node(state: PRReviewState) -> dict:
    print("  > Generating summary...")
    lines = [f"- `{r['filename']}`" for r in state["file_reviews"]]
    summary = f"Reviewed {len(lines)} file(s):\n" + "\n".join(lines)

    return {"summary": summary}


def post_review_node(state: PRReviewState) -> dict:
    print("  > Posting to GitHub...")
    body = "# Nemesis Review Report\n\n"
    body += "Terminal-grade review output focused on actionable findings.\n\n"
    body += f"## Summary\n{state['summary']}\n\n---\n\n"

    for r in state["file_reviews"]:
        body += f"## `{r['filename']}`\n{r['review']}\n\n---\n\n"

    body += "_Issued by Nemesis_"

    success = post_review(state["repo"], state["pr_number"], body)
    print(f"  > {'Posted' if success else 'Failed'}")
    return {"posted": success}
