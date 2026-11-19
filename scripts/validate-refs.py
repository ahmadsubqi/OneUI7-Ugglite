#!/usr/bin/env python3
"""Check Android local-manifest refs and every project ref in the kernel manifest."""
from pathlib import Path
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ANDROID_MANIFEST = ROOT / "manifests/mi-thorium-lineage-22.2.xml"
KERNEL_MANIFEST_URL = "https://github.com/Mi-Thorium/kernel_manifest.git"
KERNEL_MANIFEST_REF = "mithorium-4.19"
LINEAGE_MANIFEST_URL = "https://github.com/LineageOS/android.git"
LINEAGE_MANIFEST_REF = "lineage-22.2"
KERNEL_MANIFEST_RAW = (
    "https://raw.githubusercontent.com/Mi-Thorium/kernel_manifest/"
    "mithorium-4.19/default.xml"
)

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

    # Validate the Android manifest branch itself and the non-Mi-Thorium
    # LineageOS HAL repositories explicitly referenced by the local manifest.
    for url, branch, label in [
        (LINEAGE_MANIFEST_URL, LINEAGE_MANIFEST_REF, "LineageOS android manifest"),
        ("https://github.com/LineageOS/android_vendor_qcom_opensource_display-commonsys-intf.git", "lineage-22.2", "LineageOS display commonsys interface"),
        ("https://github.com/LineageOS/android_hardware_qcom_media.git", "lineage-21.0-caf-msm8953", "LineageOS CAF media HAL"),
        ("https://github.com/LineageOS/android_hardware_qcom_display.git", "lineage-21.0-caf-msm8953", "LineageOS CAF display HAL"),
    ]:
        ok, detail = check_ref(url, branch)
        checked += 1
        if ok:
            print(f"PASS {label} @ {branch} ({detail[:12]})")
        else:
            failures.append(f"{label} @ {branch}: {detail}")
            print(f"FAIL {label} @ {branch}: {detail}")

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
            print(f"PASS Android {repo_name} @ {branch} ({detail[:12]})")
        else:
            failures.append(f"Android {repo_name} @ {branch}: {detail}")
            print(f"FAIL Android {repo_name} @ {branch}: {detail}")

    ok, detail = check_ref(KERNEL_MANIFEST_URL, KERNEL_MANIFEST_REF)
    checked += 1
    if ok:
        print(f"PASS kernel_manifest @ {KERNEL_MANIFEST_REF} ({detail[:12]})")
    else:
        failures.append(f"kernel_manifest @ {KERNEL_MANIFEST_REF}: {detail}")
        print(f"FAIL kernel_manifest @ {KERNEL_MANIFEST_REF}: {detail}")

    # Verify all individual project revisions declared by the kernel manifest,
    # not merely that the manifest branch itself exists.
    try:
        with urllib.request.urlopen(KERNEL_MANIFEST_RAW, timeout=45) as response:
            kernel_xml = ET.fromstring(response.read())
    except Exception as exc:
        failures.append(f"cannot download/parse kernel manifest XML: {exc}")
        print(f"FAIL kernel manifest XML: {exc}")
        kernel_xml = None

    if kernel_xml is not None:
        kernel_remotes = {
            r.get("name"): r.get("fetch", "").rstrip("/")
            for r in kernel_xml.findall("remote")
        }
        default = kernel_xml.find("default")
        default_remote = default.get("remote") if default is not None else None
        default_revision = default.get("revision") if default is not None else None
        for project in kernel_xml.findall("project"):
            remote_name = project.get("remote") or default_remote
            repo_name = project.get("name")
            branch = project.get("revision") or default_revision
            if not repo_name or not branch or remote_name not in kernel_remotes:
                failures.append(
                    f"kernel project {project.get('path')}: missing name, revision, or remote"
                )
                continue
            branch = branch.removeprefix("refs/heads/")
            url = f"{kernel_remotes[remote_name]}/{repo_name}.git"
            ok, detail = check_ref(url, branch)
            checked += 1
            label = f"kernel {repo_name} @ {branch}"
            if ok:
                print(f"PASS {label} ({detail[:12]})")
            else:
                failures.append(f"{label}: {detail}")
                print(f"FAIL {label}: {detail}")

    if failures:
        print(f"\nFAIL: {len(failures)} of {checked} checked refs failed.")
        return 1
    print(f"\nPASS: all {checked} checked Android and kernel project refs exist.")
    print("Note: this checks Git branch existence, not full Repo sync or build compatibility.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
