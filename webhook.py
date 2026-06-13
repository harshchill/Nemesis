import hmac
import hashlib
from flask import Flask ,request,jsonify
import os
from dotenv import load_dotenv
from auth.github import get_installation_token
from agent.graph import build_graph

load_dotenv()

app = Flask(__name__)

webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")

def verify_signature(payload:bytes , signature:str)->bool:
     expected = "sha256=" + hmac.new(
        webhook_secret.encode(), payload, hashlib.sha256
    ).hexdigest()
     return hmac.compare_digest(expected, signature)

@app.route("/webhook",methods=["POST"])
def webhook():
    #  verify that it is actually from github
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(request.get_data(),signature):
         return  jsonify({"error": "Invalid signature"}), 401
    data = request.json
    event = request.headers.get("X-GitHub-Event", "")
    action = data.get("action")
    print(f"Received GitHub event={event!r}, action={action!r}", flush=True)

    # making sure the function only run when needed like new pr or commit to pr
    if event != "pull_request":
        return jsonify({"status": "ignored", "event": event, "action": action}), 200

    if action not in ["opened", "synchronize", "reopened"]:
        return jsonify({"status": "ignored", "event": event, "action": action}), 200
    
    repo = data["repository"]["full_name"]
    pr_number = data["pull_request"]["number"]
    installation_id = data["installation"]["id"]

    print(f"\n🔔 PR #{pr_number} {action} in {repo}")

    token = get_installation_token(installation_id)

    # now run the agent
    graph = build_graph()

    graph.invoke({
         "repo": repo,
         "pr_number": pr_number,
         "token": token
    })

    return jsonify({"status": "review posted"}), 200

if __name__ == "__main__":
     app.run(port=5000, debug=True)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "alive"}), 200

