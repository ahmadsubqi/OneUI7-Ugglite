#!/usr/bin/env python3
"""Check that Mi-Thorium branch refs in both Repo manifests exist on GitHub."""
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ANDROID_MANIFEST = ROOT / "manifests/mi-thorium-lineage-22.2.xml"
KERNEL_MANIFEST_URL = "https://github.com/Mi-Thorium/kernel_manifest.git"
KERNEL_MANIFEST_REF = "mithorium-4.19"

def check_ref(url, branch):
    ref = f"refs/heads/{branch}"
    result = subprocess.run(
        ["git", "ls-remote", "--exit-code", "--heads", url, ref],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=90, check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        detail = result.stderr.strip() or f"branch {ref} not found"
        return False, detail
    return True, result.stdout.split()[0]

def main():
    try:
        root = ET.parse(ANDROID_MANIFEST).getroot()
    except (OSError, ET.ParseError) as exc:
        print(f"FAIL: cannot parse Android local manifest: {exc}")
        return 1

    remotes = {r.get("name"): r.get("fetch", "").rstrip("/")
               for r in root.findall("remote")}
    checked = 0
    failures = []

    for project in root.findall("project"):
        remote_name = project.get("remote")
        if remote_name != "mi-thorium":
            continue
        repo_name = project.get("name")
        branch = project.get("revision") or next(
            (r.get("revision") for r in root.findall("remote")
             if r.get("name") == remote_name), None
        )
        if not repo_name or not branch:
            failures.append(f"{project.get('path')}: missing repo name or branch")
            continue
        url = f"{remotes[remote_name]}/{repo_name}.git"
        ok, detail = check_ref(url, branch)
        checked += 1
        if ok:
            print(f"PASS {repo_name} @ {branch} ({detail[:12]})")
        else:
            failures.append(f"{repo_name} @ {branch}: {detail}")
            print(f"FAIL {repo_name} @ {branch}: {detail}")

    ok, detail = check_ref(KERNEL_MANIFEST_URL, KERNEL_MANIFEST_REF)
    checked += 1
    if ok:
        print(f"PASS kernel_manifest @ {KERNEL_MANIFEST_REF} ({detail[:12]})")
    else:
        failures.append(f"kernel_manifest @ {KERNEL_MANIFEST_REF}: {detail}")
        print(f"FAIL kernel_manifest @ {KERNEL_MANIFEST_REF}: {detail}")

    if failures:
        print(f"\nFAIL: {len(failures)} of {checked} checked refs failed.")
        return 1
    print(f"\nPASS: all {checked} checked Mi-Thorium refs exist.")
    print("Note: this checks Git branch existence, not full Repo sync or build compatibility.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
