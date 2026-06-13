import requests
from config.setting import GITHUB_TOKEN

BASE_URL = "https://api.github.com" 

def get_header(token :str) -> dict:
    return{
         "authorization": f"bearer {token}",
         "accept":"application/vnd.github.v3+json"
    }


def get_pr_info (repo : str , pr_number : int ,token : str) -> dict:
    url = f"{BASE_URL}/repos/{repo}/pulls/{pr_number}"

    r = requests.get(url,headers=get_header(token))
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

def get_pr_files(repo : str , pr_number :int , token :str) -> list:
    url = f"{BASE_URL}/repos/{repo}/pulls/{pr_number}/files"
    r = requests.get(url,headers=get_header(token))
    r.raise_for_status()
    files = r.json()

    result = []
    for f in files:
        result.append({
            "filename" : f["filename"],
            "status" : f["status"],
            "additions" : f["additions"],
            "deletions" : f["deletions"],
            "patch" : f.get("patch","")
        })
    return result

def post_review(repo:str,pr_number:int,body:str ,token :str)->bool:
    url = f"{BASE_URL}/repos/{repo}/pulls/{pr_number}/reviews"
    payload = {
        "body" : body,
        "event": "COMMENT"
    }    
    r =  requests.post(url,headers=get_header(token), json=payload)
    return r.status_code in [200,201]
