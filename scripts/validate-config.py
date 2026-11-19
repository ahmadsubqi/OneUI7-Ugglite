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
upstream_files_validator_path = ROOT / "scripts/validate-upstream-files.py"
audio_patch_path = ROOT / "patches/0001-audio-extn-name-unused-pthread-parameters.patch"
product_patch_path = ROOT / "patches/0002-fix-mi8937-product-build-prop-override.patch"
media_copy_patch_path = ROOT / "patches/0003-fix-mithorium-msm8937-media-copy-entry.patch"

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
require(any(p.get("path") == "hardware/mithorium/display/LA.UM.8.6.2.r1-09500-89xx.0/display" for p in projects),
        "upstream LA.UM.8.6.2 display HAL project path is missing")
require(not any(p.get("path") == "device/xiaomi/Mi8937_4_19" for p in projects),
        "obsolete empty Mi8937_4_19 helper checkout must not be included")
require(any(p.get("path") == "device/xiaomi/MiThoriumSSI" and p.get("revision") == "a15/master" for p in projects),
        "MiThoriumSSI must use its verified a15/master branch")
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
    ("kernel/xiaomi/mithorium-4.19", "expected kernel source destination"),
    ("KERNEL_SYNC_ROOT=", "separate kernel sync workspace"),
    ("repo init -u https://github.com/Mi-Thorium/kernel_manifest", "kernel manifest initialization"),
    ("mv \"$KERNEL_SYNC_ROOT\" \"$KERNEL_ROOT\"", "kernel checkout move into expected source path"),
    ("repo manifest -r", "pinned manifest generation"),
    ("mka bacon", "ROM build command"),
    ("vendor/xiaomi/msm8937/mi8937.config", "device-specific kernel config fragment"),
    ('DTS_XIAOMI_ROOT="$KERNEL_ROOT/dts/xiaomi-msm8937"', "DTS repository path from kernel manifest"),
    ('DTS_VENDOR_ROOT="$KERNEL_ROOT/dts/vendor-legacy"', "vendor legacy DTS repository path"),
    ('"$DTS_XIAOMI_ROOT/ugglite.dts"', "ugglite DTS check at manifest project path"),
    ('"$DTS_XIAOMI_ROOT/ulysse/ugglite/camera.dtsi"', "ugglite camera sensor DTS include"),
    ('#include "camera.dtsi"', "ugglite camera DTS include wiring"),
    ('"$UGGLITE_CAMERA_CONFIG"', "ugglite camera XML preflight"),
    ('overlayfs/ugglite/camera/camera_config.xml:', "ugglite camera XML vendor packaging check"),
    ('"$KERNEL_SOURCE/arch/arm64/boot/dts/xiaomi-msm8937/ugglite.dts"', "DTS linkfile consumed by kernel Kbuild"),
    ('"$KERNEL_SOURCE/arch/arm64/boot/dts/vendor-legacy/qcom/msm8917.dtsi"', "vendor DTS linkfile consumed by kernel Kbuild"),
    ('"$KERNEL_SOURCE/techpack/camera-legacy/Makefile"', "camera techpack linkfile consumed by Kbuild"),
    ('"$KERNEL_SOURCE/techpack/audio-legacy/Makefile"', "audio techpack linkfile consumed by Kbuild"),
    ('"$KERNEL_SOURCE/techpack/camera-legacy-m/Makefile"', "alternate camera techpack linkfile consumed by Kbuild"),
    ('"$KERNEL_SOURCE/techpack/xiaomi-msm8937/Makefile"', "Xiaomi MSM8937 techpack linkfile consumed by Kbuild"),
    ('"$KERNEL_SOURCE/drivers/staging/prima/Makefile"', "prima WLAN driver linkfile consumed by Kbuild"),
    ("vendor/feature/no-camera-stack.config", "recovery kernel config fragment"),
    ("AUDIO_PATCH=", "audio HAL compatibility patch integration"),
    ('git -C "$AUDIO_HAL_ROOT" apply', "audio HAL patch application"),
    ("apply_local_patch", "idempotent local upstream patch application"),
    ("0002-fix-mi8937-product-build-prop-override.patch", "Mi8937 product makefile patch"),
    ("0003-fix-mithorium-msm8937-media-copy-entry.patch", "MiThorium media copy patch"),
]:
    require(needle in build, f"build script is missing {label}")

require(build.find("cd \"$KERNEL_SYNC_ROOT\"") < build.find("repo init -u https://github.com/Mi-Thorium/kernel_manifest"),
        "kernel Repo init must run from the separate sync workspace, not inside the Android Repo client")

try:
    workflow = workflow_path.read_text(encoding="utf-8")
except OSError as exc:
    print(f"FAIL: cannot read build workflow: {exc}")
    sys.exit(1)

require("self-hosted" in workflow and "android-build" in workflow,
        "full build must be restricted to the android-build self-hosted runner")
require("actions/upload-artifact@" in workflow,
        "build workflow must upload build artifacts")
require("github.workspace" in workflow and "runner.workspace" not in workflow,
        "job-level ANDROID_ROOT must use the supported github.workspace context")

try:
    validation_workflow = validation_workflow_path.read_text(encoding="utf-8")
    refs_validator = refs_validator_path.read_text(encoding="utf-8")
    upstream_files_validator = upstream_files_validator_path.read_text(encoding="utf-8")
    audio_patch = audio_patch_path.read_text(encoding="utf-8")
    product_patch = product_patch_path.read_text(encoding="utf-8")
    media_copy_patch = media_copy_patch_path.read_text(encoding="utf-8")
except OSError as exc:
    print(f"FAIL: cannot read validation workflow or refs validator: {exc}")
    sys.exit(1)

require("python3 scripts/validate-refs.py" in validation_workflow,
        "lightweight workflow must run upstream branch-reference checks")
require("python3 scripts/validate-upstream-files.py" in validation_workflow,
        "lightweight workflow must run critical upstream source-file checks")
require("lineage_Mi8937_4_19-userdebug" in upstream_files_validator and "ugglite.dts" in upstream_files_validator and "msm8937-legacy.config" in upstream_files_validator and "cirrus_playback.c" in upstream_files_validator,
        "upstream file validator must check ugglite and the known audio HAL issue")
require('"TARGET_KERNEL_CONFIG +="' in upstream_files_validator and '"vendor/msm8937-legacy.config"' in upstream_files_validator,
        "upstream file validator must separately verify the MSM8937 legacy kernel config selection")
require("AUDIO_PATCH=" in build and 'git -C "$AUDIO_HAL_ROOT" apply' in build,
        "build script must apply the audio HAL compatibility patch")
require("void *arg __unused" in audio_patch and "spkr_calibration_thread" in audio_patch,
        "audio HAL Clang compatibility patch is missing or incomplete")
require('BuildDesc="land-user 6.0.1 MMB29M V10.2.2.0.MALMIXM release-keys" \\' in product_patch,
        "Mi8937 product build-property patch is missing the required continuation")
require("media_codecs_8956.xml:$(TARGET_COPY_OUT_VENDOR)" in media_copy_patch and
        "media_codecs_8956.xml::" not in media_copy_patch,
        "MiThorium malformed PRODUCT_COPY_FILES entry patch is missing")
require(audio_patch_path.is_file(), "audio HAL compatibility patch file is missing")
require("lineage_Mi8937_4_19-userdebug" in upstream_files_validator and "ugglite.dts" in upstream_files_validator and "msm8937-legacy.config" in upstream_files_validator,
        "upstream file validator must check the ugglite product and kernel DTS")
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
