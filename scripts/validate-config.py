#!/usr/bin/env python3
"""Offline validation for the OneUI7-Ugglite source/build configuration."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / "manifests/mi-thorium-lineage-22.2.xml"
build_path = ROOT / "scripts/build-android15.sh"
workflow_path = ROOT / ".github/workflows/build-android15.yml"
validation_workflow_path = ROOT / ".github/workflows/validate-config.yml"
refs_validator_path = ROOT / "scripts/validate-refs.py"

errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

try:
    tree = ET.parse(manifest_path)
    manifest = tree.getroot()
except (ET.ParseError, OSError) as exc:
    print(f"FAIL: cannot parse local manifest: {exc}")
    sys.exit(1)

remotes = {node.get("name") for node in manifest.findall("remote")}
projects = manifest.findall("project")
paths = [node.get("path") for node in projects]

require(manifest.tag == "manifest", "manifest root element must be <manifest>")
require("mi-thorium" in remotes, "mi-thorium remote is missing")
require(len(paths) == len(set(paths)), "duplicate project path found in local manifest")
require(any(p.get("path") == "device/xiaomi/Mi8937" for p in projects),
        "Mi8937 device-tree project is missing")
require(any(p.get("path") == "vendor/xiaomi/Mi8937" for p in projects),
        "Mi8937 vendor project is missing")
require(any(p.get("path") == "device/xiaomi/mithorium-common" for p in projects),
        "MiThorium common device tree is missing")
for project in projects:
    require(bool(project.get("path")), "project without path attribute")
    require(bool(project.get("name")), "project without name attribute")
    remote = project.get("remote")
    require(remote is None or remote in remotes,
            f"project {project.get('path')} references undefined remote {remote!r}")

try:
    build = build_path.read_text(encoding="utf-8")
except OSError as exc:
    print(f"FAIL: cannot read build script: {exc}")
    sys.exit(1)

for needle, label in [
    ("lineage-22.2", "LineageOS 22.2 branch"),
    ("lineage_Mi8937_4_19-userdebug", "expected lunch target"),
    ("kernel/xiaomi/mithorium-4.19", "nested kernel Repo client path"),
    ("repo manifest -r", "pinned manifest generation"),
    ("mka bacon", "ROM build command"),
]:
    require(needle in build, f"build script is missing {label}")

try:
    workflow = workflow_path.read_text(encoding="utf-8")
except OSError as exc:
    print(f"FAIL: cannot read build workflow: {exc}")
    sys.exit(1)

require("self-hosted" in workflow and "android-build" in workflow,
        "full build must be restricted to the android-build self-hosted runner")
require("actions/upload-artifact@" in workflow,
        "build workflow must upload build artifacts")

try:
    validation_workflow = validation_workflow_path.read_text(encoding="utf-8")
    refs_validator = refs_validator_path.read_text(encoding="utf-8")
except OSError as exc:
    print(f"FAIL: cannot read validation workflow or refs validator: {exc}")
    sys.exit(1)

require("python3 scripts/validate-refs.py" in validation_workflow,
        "lightweight workflow must run upstream branch-reference checks")
require('"ls-remote"' in refs_validator and '"--heads"' in refs_validator,
        "upstream reference validator must check remote Git refs")

if errors:
    for error in errors:
        print(f"FAIL: {error}")
    sys.exit(1)

print(f"PASS: XML parsed; {len(projects)} manifest projects; no duplicate paths.")
print("PASS: required Mi8937 projects and remotes are present.")
print("PASS: build script contains the expected Android/kernel build flow.")
print("PASS: full build is gated behind the android-build self-hosted runner.")
print("PASS: lightweight workflow includes upstream Git reference preflight.")
