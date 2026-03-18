#!/bin/bash
# Perplexity Search API wrapper
# Usage: perplexity-search.sh "query" [max_results] [max_tokens]

QUERY="${1:-}"
MAX_RESULTS="${2:-5}"
MAX_TOKENS="${3:-512}"
API_KEY=$(cat ~/.secrets/perplexity.txt 2>/dev/null)

if [ -z "$QUERY" ]; then
  echo "Usage: $0 \"query\" [max_results] [max_tokens]" >&2
  exit 1
fi

if [ -z "$API_KEY" ]; then
  echo "ERROR: Perplexity API key not found at ~/.secrets/perplexity.txt" >&2
  exit 1
fi

RESULT=$(curl -s -X POST 'https://api.perplexity.ai/search' \
  -H "Authorization: Bearer $API_KEY" \
  -H 'Content-Type: application/json' \
  -d "{
    \"query\": $(echo "$QUERY" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))'),
    \"max_results\": $MAX_RESULTS,
    \"max_tokens_per_page\": $MAX_TOKENS
  }")

echo "$RESULT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
results = data.get('results', [])
if not results:
    print('No results found')
    sys.exit(0)
for i, r in enumerate(results, 1):
    print(f'[{i}] {r.get(\"title\", \"No title\")}')
    print(f'    URL: {r.get(\"url\", \"\")}')
    print(f'    {r.get(\"snippet\", \"\")}')
    print()
"
