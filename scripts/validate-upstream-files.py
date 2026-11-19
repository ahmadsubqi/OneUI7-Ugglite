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
        ["ugglite", "BoardConfigCommon.mk", "TARGET_USES_MITHORIUM_KERNEL := true"],
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
    (
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "mithorium.mk",
        ["TARGET_USES_XIAOMI_MITHORIUM_COMMON_TREE := true"],
    ),
    # Kernel config fragments selected by BoardConfigCommon.mk and Mi8937/BoardConfig.mk.
    *[
        ("Mi-Thorium/kernel_msm-4.19", "mithorium/a13/master", f"arch/arm64/configs/{name}", [])
        for name in [
            "vendor/common.config",
            "vendor/debugfs.config",
            "vendor/msm8937-legacy.config",
            "vendor/feature/android-12.config",
            "vendor/feature/compat-vdso.config",
            "vendor/feature/erofs.config",
            "vendor/feature/exfat.config",
            "vendor/feature/kprobes.config",
            "vendor/feature/lmkd.config",
            "vendor/feature/wireguard.config",
            "vendor/feature/ntfs.config",
            "vendor/feature/no-camera-stack.config",
            "vendor/feature/no-wlan-driver.config",
            "vendor/xiaomi/msm8937/common.config",
            "vendor/xiaomi/msm8937/mi8937.config",
        ]
    ],
    # Includes imported by the ugglite DTS across the two DTS repositories.
    *[
        ("Mi-Thorium/kernel_devicetree_xiaomi-msm8937", "dts/mi8937/4.19/master", name, [])
        for name in [
            "common/include/config.h",
            "common/common.dtsi",
            "common/fragments/delete-msm89x7-camera-sensor-mtp.dtsi",
            "ulysse/common/common.dtsi",
            "ulysse/ugglite/ugglite.dtsi",
        ]
    ],
    *[
        ("Mi-Thorium/kernel_devicetree_msm-4.19", "dts/master", name, [])
        for name in [
            "qcom/msm8917.dtsi",
            "qcom/msm8917-audio.dtsi",
            "qcom/msm8917-mtp.dtsi",
            "qcom/msm8917-pmi8937.dtsi",
        ]
    ],
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
