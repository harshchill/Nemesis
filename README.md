# Nemesis

```text
███╗   ██╗███████╗███╗   ███╗███████╗███████╗██╗███████╗
████╗  ██║██╔════╝████╗ ████║██╔════╝██╔════╝██║██╔════╝
██╔██╗ ██║█████╗  ██╔████╔██║█████╗  ███████╗██║███████╗
██║╚██╗██║██╔══╝  ██║╚██╔╝██║██╔══╝  ╚════██║██║╚════██║
██║ ╚████║███████╗██║ ╚═╝ ██║███████╗███████║██║███████║
╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝╚══════╝╚══════╝╚═╝╚══════╝
                                                        
```

Nemesis is a  PR review agent that fetches pull request changes from GitHub, runs focused LLM-based review passes, and posts the result back as a GitHub review comment.

## What It Does

- Reads PR metadata and changed files from the GitHub API.
- Skips noisy or low-value files such as lockfiles and common binary assets.
- Sends each diff chunk to the review model with a strict review prompt.
- Builds a compact review summary and posts it back to the PR.

## Design Goals

- Professional and direct output.
- No emojis, filler, or generic AI tone.
- Actionable findings over broad commentary.
- Clear terminal-style feedback while the agent runs.

## Project Structure

### `main.py`

Entry point that builds the LangGraph workflow and invokes the review run.

### `agent/graph.py`

Defines the review pipeline:

1. Fetch PR metadata
2. Fetch changed files
3. Analyze each file
4. Build a summary
5. Post the review to GitHub

### `agent/nodes.py`

Implements the workflow nodes and the GitHub review body formatting.

### `agent/state.py`

Typed state container for the LangGraph workflow.

### `prompts/review_prompt.py`

The review contract for the model. This is where the review personality is enforced:

- strict
- concise
- specific
- no fluff

### `tools/github_tools.py`

GitHub REST API helpers for PR metadata, changed files, and posting reviews.

### `tools/llm_tools.py`

LLM wrapper that sends each diff to the review prompt and returns the model response.

### `config/setting.py`

Loads environment variables and creates the model client.

## Environment Variables

Create a `.env` file with:

```env
GITHUB_TOKEN=your_github_token
GROQ_API_KEY=your_groq_api_key
```

## How The Review Works

Nemesis does not try to sound helpful by default. It tries to be correct.

The review prompt tells the model to:

- call out real defects
- reference file and line locations when possible
- avoid style noise unless it hides a bug
- return `No actionable findings.` when nothing is worth flagging

That makes the output easier to scan in a PR and much less like a generic chatbot answer.

## Running It

The current setup in `main.py` is hardcoded to a repository and PR number for testing. Update those values or wire the graph into your own trigger flow.

Typical flow:

```python
from agent.graph import build_graph

graph = build_graph()
graph.invoke({
    "repo": "owner/repo",
    "pr_number": 123,
})
```

## Notes

- The repository currently includes a local `venv/` folder, which should stay untracked.
- The agent skips lockfiles and common binary assets to keep review cost focused on meaningful source changes.
- If you want, the next upgrade is to make the posted review more structured per finding, with one bullet per issue and inline severity tags.
