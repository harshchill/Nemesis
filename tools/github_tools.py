import requests
from config.setting import GITHUB_TOKEN

BASE_URL = "https://api.github.com" 

HEADERS = {
    "authorization": f"bearer {GITHUB_TOKEN}",
    "accept":"application/vnd.github.v3+json"
}

def get_pr_info (repo : str , pr_number : int) -> dict:
    url = f"{BASE_URL}/repos/{repo}/pulls/{pr_number}"

    r = requests.get(url,headers=HEADERS)
    r.raise_for_status()
    data = r.json()

    return {
        "title" : data["title"],
        "body" :  data.get("body") or "no description provided",
        "author": data["user"]["login"],
        "base_branch": data["base"]["ref"],
        "head_branch": data["head"]["ref"],
        "head_sha": data["head"]["sha"]
    }