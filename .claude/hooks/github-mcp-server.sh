#!/bin/bash
# Bridge: sources token from gh CLI so no PAT needs to be stored separately.
GITHUB_PERSONAL_ACCESS_TOKEN=$(gh auth token 2>/dev/null)
if [ -z "$GITHUB_PERSONAL_ACCESS_TOKEN" ]; then
    echo "GitHub MCP: gh CLI not authenticated. Run 'gh auth login' first." >&2
    exit 1
fi
export GITHUB_PERSONAL_ACCESS_TOKEN
exec npx -y @modelcontextprotocol/server-github
