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
        ["ugglite", "BoardConfigCommon.mk", "TARGET_USES_MITHORIUM_KERNEL := true",
         "TARGET_KERNEL_CONFIG +=", "vendor/msm8937-legacy.config"],
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
        ["CONFIG_ARCH_MSM8937=y", "CONFIG_CFG80211=y", "CONFIG_WCNSS_CORE=y", "CONFIG_WCNSS_CORE_PRONTO=y", "CONFIG_SND=y", "CONFIG_SND_SOC=y", "CONFIG_MSMB_CAMERA=y", "CONFIG_MSMB_JPEG=y", "CONFIG_MSM_FD=y"],
    ),
    (
        "Mi-Thorium/kernel_msm-4.19",
        "mithorium/a13/master",
        "arch/arm64/configs/vendor/common.config",
        ["CONFIG_PRONTO_WLAN=y"],
    ),
    (
        "Mi-Thorium/kernel_msm-4.19",
        "mithorium/a13/master",
        "arch/arm64/configs/vendor/xiaomi/msm8937/mi8937.config",
        ["CONFIG_MSMB_CAMERA_LEGACY=y", "CONFIG_MSMB_CAMERA_LEGACY_M=y", "CONFIG_MACH_XIAOMI_UGGLITE=y"],
    ),
    (
        "Mi-Thorium/kernel_msm-4.19",
        "mithorium/a13/master",
        "drivers/staging/Makefile",
        ["obj-$(CONFIG_PRONTO_WLAN) += prima/"],
    ),
    (
        "Mi-Thorium/kernel_msm-4.19",
        "mithorium/a13/master",
        "drivers/staging/Kconfig",
        ['source "drivers/staging/prima/Kconfig"'],
    ),
    (
        "Mi-Thorium/vendor_qcom_opensource_wlan_prima",
        "wlan/LA.UM.9.6.4/mithorium/master",
        "Kconfig",
        ["if CFG80211 && WCNSS_CORE_PRONTO", "config PRONTO_WLAN"],
    ),
    (
        "Mi-Thorium/vendor_qcom_opensource_wlan_prima",
        "wlan/LA.UM.9.6.4/mithorium/master",
        "Kbuild",
        ["obj-$(CONFIG_PRONTO_WLAN) += $(MODNAME).o"],
    ),
    (
        "Mi-Thorium/kernel_techpack_audio-legacy",
        "audio/4.19/mithorium/master",
        "Makefile",
        ["CONFIG_ARCH_MSM8937", "sdm450auto.conf", "sdm450autoconf.h"],
    ),
    (
        "Mi-Thorium/kernel_techpack_audio-legacy",
        "audio/4.19/mithorium/master",
        "config/sdm450auto.conf",
        ["CONFIG_SND_SOC_SDM450=y", "CONFIG_SND_SOC_EXT_CODEC_SDM450=y"],
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
    (
        "Mi-Thorium/android_hardware_qcom_audio_mithorium",
        "mithorium/LA.UM.9.6.4.r2-04300-89xx.QSSI13r2.0",
        "hal/audio_extn/cirrus_playback.c",
        ["audio_extn_cirrus_calibration_thread(void*)", "audio_extn_cirrus_config_thread(void*)"],
    ),
    (
        "Mi-Thorium/android_hardware_qcom_audio_mithorium",
        "mithorium/LA.UM.9.6.4.r2-04300-89xx.QSSI13r2.0",
        "hal/audio_extn/spkr_protection.c",
        ["spkr_calibration_thread(void*)", "spkr_v_vali_thread(void*)"],
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
    (
        "Mi-Thorium/kernel_devicetree_xiaomi-msm8937",
        "dts/mi8937/4.19/master",
        "ulysse/ugglite/ugglite.dtsi",
        ['#include "camera.dtsi"', '#include "battery_usb.dtsi"'],
    ),
    (
        "Mi-Thorium/kernel_devicetree_xiaomi-msm8937",
        "dts/mi8937/4.19/master",
        "ulysse/ugglite/camera.dtsi",
        ["qcom,eeprom@", "qcom,camera@0", "qcom,camera@1"],
    ),
    # Includes imported by the ugglite DTS across the two DTS repositories.
    *[
        ("Mi-Thorium/kernel_devicetree_xiaomi-msm8937", "dts/mi8937/4.19/master", name, [])
        for name in [
            "common/include/config.h",
            "common/common.dtsi",
            "common/fragments/delete-msm89x7-camera-sensor-mtp.dtsi",
            "ulysse/common/common.dtsi",
            "ulysse/ugglite/ugglite.dtsi",
            "ulysse/ugglite/camera.dtsi",
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
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "lineage_Mi8937_4_19.mk",
        ['BuildDesc="land-user 6.0.1 MMB29M V10.2.2.0.MALMIXM release-keys"', "BuildFingerprint=Xiaomi/land/land:6.0.1"],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "mithorium.mk",
        ["media_codecs_8956.xml::$(TARGET_COPY_OUT_VENDOR)/etc/media_codecs_8956.xml"],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "media/msm8937/media_codecs_8956.xml",
        ["<MediaCodecs"],
    ),
    (
        "Mi-Thorium/proprietary_vendor_xiaomi_Mi8937",
        "a15_qpr2/master",
        "proprietary/vendor/etc/overlayfs/ugglite/camera/camera_config.xml",
        ["CameraModuleConfig"],
    ),
    (
        "Mi-Thorium/proprietary_vendor_xiaomi_Mi8937",
        "a15_qpr2/master",
        "Mi8937-vendor.mk",
        ["overlayfs/ugglite/camera/camera_config.xml:", "ugglite_libmmcamera_s5k5e8_f5e8ybf_d6"],
    ),
    (
        "Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-4.19",
        "a15_qpr2/master",
        "mithorium-common-4.19-vendor.mk",
        ["vendor/xiaomi/mithorium-common-4.19", "PRODUCT_COPY_FILES +="],
    ),
    (
        "Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-4.19",
        "a15_qpr2/master",
        "Android.bp",
        ["soong_namespace {"],
    ),
    (
        "Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-graphics",
        "a15_qpr2/master",
        "mithorium-common-graphics-vendor.mk",
        ["LA.UM.9.6.3.r1-06200-89xx.0/extract-vendor.mk"],
    ),
    (
        "Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-graphics",
        "a15_qpr2/master",
        "LA.UM.9.6.3.r1-06200-89xx.0/extract-vendor.mk",
        ["libEGL_adreno", "vulkan.adreno"],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "BoardConfig.mk",
        ["TARGET_KERNEL_CONFIG +=", "vendor/msm8937-legacy.config"],
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
