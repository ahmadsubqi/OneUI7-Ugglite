#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <repo-client-root> <output-xml>" >&2
  exit 2
fi

CLIENT_ROOT="$(cd "$1" && pwd)"
OUTPUT="$2"
command -v repo >/dev/null || { echo "ERROR: repo launcher is missing." >&2; exit 1; }
mkdir -p "$(dirname "$OUTPUT")"

echo "=== Pinning synchronized Repo projects ==="
echo "Repo client: $CLIENT_ROOT"
echo "Lock file:   $OUTPUT"
(
  cd "$CLIENT_ROOT"
  repo manifest -r -o "$OUTPUT"
)

python3 - "$OUTPUT" <<'PY'
import re
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
root = ET.parse(path).getroot()
projects = root.findall("project")
if not projects:
    raise SystemExit("ERROR: pinned manifest contains no projects")
bad = []
for project in projects:
    name = project.get("name") or project.get("path") or "<unnamed>"
    revision = project.get("revision", "")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        bad.append(f"{name}: revision is not a full 40-character commit SHA ({revision!r})")
if bad:
    raise SystemExit("ERROR: manifest is not fully pinned:\n" + "\n".join(bad))
print(f"PASS: {len(projects)} projects pinned to immutable commit SHAs.")
PY

sha256sum "$OUTPUT"
