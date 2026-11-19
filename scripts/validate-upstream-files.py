#!/usr/bin/env python3
"""Check critical upstream source files and ugglite-specific markers without repo sync."""
import sys
import urllib.error
import urllib.request

BASE = "https://raw.githubusercontent.com"
CHECKS = [
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "lineage_Mi8937_4_19.mk",
        ["TARGET_KERNEL_VERSION := 4.19", "device/xiaomi/Mi8937/device.mk"],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "AndroidProducts.mk",
        ["lineage_Mi8937_4_19-userdebug"],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "device.mk",
        ["xiaomi_ugglite_overlay", "vendor/xiaomi/Mi8937/Mi8937-vendor.mk"],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "BoardConfig.mk",
        ["ugglite", "BoardConfigCommon.mk"],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "lineage.dependencies",
        ["android_device_xiaomi_mithorium-common", "android_device_xiaomi_mi8937-camera"],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "BoardConfigCommon.mk",
        ["TARGET_KERNEL_SOURCE := kernel/xiaomi/mithorium-$(TARGET_KERNEL_VERSION)/kernel"],
    ),
    (
        "Mi-Thorium/proprietary_vendor_xiaomi_Mi8937",
        "a15_qpr2/master",
        "Mi8937-vendor.mk",
        ["ugglite"],
    ),
    (
        "Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-4.19",
        "a15_qpr2/master",
        "BoardConfigVendor.mk",
        ["setup-makefiles.sh"],
    ),
    (
        "Mi-Thorium/kernel_msm-4.19",
        "mithorium/a13/master",
        "Makefile",
        ["VERSION = 4", "PATCHLEVEL = 19", "SUBLEVEL = 325"],
    ),
    (
        "Mi-Thorium/kernel_msm-4.19",
        "mithorium/a13/master",
        "arch/arm64/configs/vendor/msm8937-perf_defconfig",
        ["CONFIG_ARCH_MSM8937=y"],
    ),
    (
        "Mi-Thorium/kernel_devicetree_xiaomi-msm8937",
        "dts/mi8937/4.19/master",
        "Makefile",
        ["ugglite.dtb"],
    ),
    (
        "Mi-Thorium/kernel_devicetree_xiaomi-msm8937",
        "dts/mi8937/4.19/master",
        "ugglite.dts",
        ["xiaomi,ugglite"],
    ),
    (
        "Mi-Thorium/kernel_manifest",
        "mithorium-4.19",
        "default.xml",
        ['path="kernel"', 'revision="mithorium/a13/master"', "dts/mi8937/4.19/master"],
    ),
]

def fetch_text(owner_repo, ref, path):
    url = f"{BASE}/{owner_repo}/{ref}/{path}"
    request = urllib.request.Request(url, headers={"User-Agent": "OneUI7-Ugglite-source-audit"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read().decode("utf-8", errors="replace")

def main():
    failures = []
    for owner_repo, ref, path, markers in CHECKS:
        label = f"{owner_repo}@{ref}:{path}"
        try:
            content = fetch_text(owner_repo, ref, path)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            failures.append(f"{label}: fetch failed: {exc}")
            print(f"FAIL {label}: {exc}")
            continue
        missing = [marker for marker in markers if marker not in content]
        if missing:
            failures.append(f"{label}: missing markers {missing}")
            print(f"FAIL {label}: missing markers {missing}")
        else:
            print(f"PASS {label} ({len(content)} chars; {len(markers)} markers)")
    if failures:
        print(f"\nFAIL: {len(failures)} of {len(CHECKS)} upstream file checks failed.")
        return 1
    print(f"\nPASS: all {len(CHECKS)} critical upstream files and markers verified.")
    print("Note: file presence/content markers do not prove complete Repo sync or build compatibility.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
