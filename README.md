# Nemesis    

```brand
███╗   ██╗███████╗███╗   ███╗███████╗███████╗██╗███████╗
████╗  ██║██╔════╝████╗ ████║██╔════╝██╔════╝██║██╔════╝
██╔██╗ ██║█████╗  ██╔████╔██║█████╗  ███████╗██║███████╗
██║╚██╗██║██╔══╝  ██║╚██╔╝██║██╔══╝  ╚════██║██║╚════██║
██║ ╚████║███████╗██║ ╚═╝ ██║███████╗███████║██║███████║
╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝╚══════╝╚══════╝╚═╝╚══════╝
                                                        
```


Nemesis is a GitHub App powered PR review agent. It receives pull request webhook events, authenticates as the installed GitHub App, fetches the PR diff, runs focused LLM review passes, and posts a review comment back to the pull request.

The goal is simple: surface real defects with a direct, professional review style.

## Features

- Runs from a Flask webhook server.
- Verifies GitHub webhook signatures with `GITHUB_WEBHOOK_SECRET`.
- Authenticates as a GitHub App using an app ID and private key.
- Exchanges the GitHub App JWT for an installation access token.
- Handles pull request events only.
- Reviews PRs when they are opened, reopened, or synchronized.
- Fetches PR metadata and changed files from the GitHub REST API.
- Skips low-value files such as lockfiles, minified assets, and common binary assets.
- Uses a strict review prompt to prioritize actionable findings.
- Posts a consolidated GitHub pull request review comment.

## Webhook Flow

1. GitHub sends a webhook request to `POST /webhook`.
2. `webhook.py` verifies the `X-Hub-Signature-256` header.
3. The handler logs the received GitHub event and action.
4. Non-`pull_request` events are ignored with a `200` response.
5. Pull request actions other than `opened`, `synchronize`, and `reopened` are ignored.
6. Nemesis reads the repository name, PR number, and installation ID from the payload.
7. The app generates a GitHub App JWT and exchanges it for an installation token.
8. The LangGraph workflow fetches PR data, reviews changed files, builds a summary, and posts the review.

## Project Structure

```text
.
|-- webhook.py              # Flask webhook entry point for GitHub App events
|-- main.py                 # Manual graph invocation entry point for local testing
|-- auth/
|   `-- github.py           # GitHub App JWT and installation token helpers
|-- agent/
|   |-- graph.py            # LangGraph workflow definition
|   |-- nodes.py            # Workflow node implementations
|   `-- state.py            # Typed workflow state
|-- tools/
|   |-- github_tools.py     # GitHub REST API helpers
|   `-- llm_tools.py        # LLM review and summary helpers
|-- prompts/
|   |-- review_prompt.py    # Per-file review prompt
|   `-- summary_prompt.py   # Final summary prompt
`-- config/
    `-- setting.py          # Environment loading and model client setup
```

##Main Architecture Flow

```text
┌─────────────┐
│ GitHub User │
└──────┬──────┘
       │ Creates / Updates PR
       ▼
┌─────────────────────────────┐
│ GitHub Repository           │
│ Pull Request Event          │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ GitHub Webhook              │
│ POST /webhook               │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Flask Webhook Server        │
│ webhook.py                  │
│ Signature Verification      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ GitHub App Authentication   │
│ Generate JWT                │
│ Exchange Installation Token │
└──────────────┬──────────────┘
               │
               ▼
┌────────────────────────────────────┐
│ Nemesis LangGraph Workflow         │
│                                    │
│ 1. Fetch PR Metadata               │
│ 2. Fetch Changed Files             │
│ 3. Filter Noisy Files              │
│ 4. LLM Code Review                 │
│ 5. Generate Summary                │
│ 6. Build Review Report             │
└──────────────┬─────────────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Groq LLM                    │
│ Review Prompt               │
│ Summary Prompt              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ Consolidated Review Output  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│ GitHub Pull Request Review  │
│ Comment Posted             │
└─────────────────────────────┘
```

## Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key

GITHUB_APP_ID=your_github_app_id
GITHUB_WEBHOOK_SECRET=your_webhook_secret
GITHUB_PRIVATE_KEY_PATH=path_to_your_github_app_private_key.pem
```

`GITHUB_TOKEN` may still be useful for older manual tests, but the webhook app flow uses GitHub App installation tokens instead.

Keep `.env` and private key files out of git. If a real token or private key is committed, shared, or exposed, rotate it immediately.

## GitHub App Setup

Create a GitHub App and configure:

- Webhook URL: `https://your-public-url/webhook`
- Webhook secret: the same value as `GITHUB_WEBHOOK_SECRET`
- Subscribe to events: `Pull request`
- Repository permissions:
  - Pull requests: read and write
  - Contents: read
  - Metadata: read

Install the app on the repositories Nemesis should review.

For local development, expose the Flask server with a tunnel such as ngrok and set the GitHub App webhook URL to:

```text
https://your-ngrok-url.ngrok-free.app/webhook
```

The path must be `/webhook`. Posting to `/` will return `404` because the app does not register a root webhook route.

## Running The Webhook Server

Start the Flask server:

```bash
python webhook.py
```

By default, it runs on:

```text
http://127.0.0.1:5000
```

The webhook endpoint is:

```text
POST http://127.0.0.1:5000/webhook
```

When a delivery arrives, the server logs the GitHub event and action:

```text
Received GitHub event='pull_request', action='opened'
```

If GitHub sends a `ping`, `push`, or unsupported pull request action, Nemesis returns `200` with an ignored status and does not run the review workflow.

## Review Workflow

The LangGraph workflow runs these nodes:

1. Fetch PR metadata.
2. Fetch changed files.
3. Filter out noisy files.
4. Analyze each remaining file with the review prompt.
5. Generate a summary.
6. Post a GitHub review comment.

The posted review includes a summary and per-file review sections.

## Manual Testing

`main.py` can still be used for direct local graph testing, but the production-style flow is now the GitHub App webhook in `webhook.py`.

For manual invocation, build the graph and provide:

```python
from agent.graph import build_graph

graph = build_graph()
graph.invoke({
    "repo": "owner/repo",
    "pr_number": 123,
    "token": "github_installation_or_access_token",
})
```

## Troubleshooting

### `POST / HTTP/1.1" 404`

The webhook URL is missing the `/webhook` path. Use:

```text
https://your-public-url/webhook
```

### `POST /webhook HTTP/1.1" 200` but no review is posted

Check the console log:

```text
Received GitHub event='...', action='...'
```

Nemesis only runs for:

- `event='pull_request'`
- `action='opened'`
- `action='synchronize'`
- `action='reopened'`

Other events are acknowledged and ignored.

### `401 Invalid signature`

The webhook secret in GitHub does not match `GITHUB_WEBHOOK_SECRET`, or the request was not sent by GitHub with the correct signature header.

### Review workflow starts but no comment appears

Check that the GitHub App has pull request write permission and is installed on the target repository.

## Notes

- The local `venv/` directory should stay untracked.
- Private key `.pem` files should stay untracked.
- The Flask development server is for local development only. Use a production WSGI server for deployment.
- Review output is intentionally direct and concise. The agent should return `No actionable findings.` when there is nothing useful to flag.
