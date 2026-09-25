#!/usr/bin/env bash
# Call the Cloudflare API with the token in ~/.config/trulyfreefonts/cloudflare.env.
# Usage: ops/cf.sh METHOD /path [json-body]
#   ops/cf.sh GET /zones
#   ops/cf.sh PATCH /zones/<zone-id>/settings/ssl '{"value":"strict"}'
set -euo pipefail
token=$(sed -n 's/^CF_API_TOKEN=//p' "$HOME/.config/trulyfreefonts/cloudflare.env")
method=$1 path=$2
curl -sS -X "$method" "https://api.cloudflare.com/client/v4$path" \
  -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
  ${3:+--data "$3"}
