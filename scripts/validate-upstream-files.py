#!/usr/bin/env python3
"""Check critical upstream source files and ugglite-specific markers without repo sync."""
import json
import re
import sys
import xml.etree.ElementTree as ET
import urllib.error
import urllib.request
from pathlib import Path

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
        [
            "PRODUCT_USE_DYNAMIC_PARTITIONS := true",
            "PRODUCT_RETROFIT_DYNAMIC_PARTITIONS := true",
            "xiaomi_ugglite_overlay",
            "init.xiaomi.device.rc",
            "vendor/xiaomi/Mi8937/Mi8937-vendor.mk",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "lineage.dependencies",
        [
            '"android_device_xiaomi_mithorium-common"',
            '"android_device_xiaomi_land-camera"',
            '"android_device_xiaomi_mi8937-camera"',
            '"device/xiaomi/mithorium-common"',
            '"device/xiaomi/land-camera"',
            '"device/xiaomi/mi8937-camera"',
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "rootdir/etc/fstab_4_19.qcom",
        [
            "/dev/block/by-name/boot",
            "/dev/block/by-name/recovery",
            "/system",
            "/system_ext",
            "wait,logical,first_stage_mount",
            "/dev/block/by-name/userdata",
            "fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized",
            "fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized",
            "/dev/block/platform/soc/7824900.sdhci/by-name/persist",
            "/dev/block/platform/soc/7824900.sdhci/by-name/modem",
        ],
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
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "BoardConfigCommon.mk",
        [
            "BOARD_KERNEL_BASE := 0x80000000",
            "BOARD_KERNEL_IMAGE_NAME := Image.gz-dtb",
            "BOARD_KERNEL_PAGESIZE :=  2048",
            "BOARD_MKBOOTIMG_ARGS := --ramdisk_offset 0x01000000 --tags_offset 0x00000100",
            "BOARD_FLASH_BLOCK_SIZE := 131072",
            "TARGET_KERNEL_SOURCE := kernel/xiaomi/mithorium-$(TARGET_KERNEL_VERSION)/kernel",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "BoardConfig.mk",
        [
            "BOARD_BOOTIMAGE_PARTITION_SIZE := 67108864",
            "BOARD_RECOVERYIMAGE_PARTITION_SIZE := 67108864",
            "BOARD_KERNEL_CMDLINE += androidboot.boot_devices=soc/7824900.sdhci",
            "TARGET_OTA_ASSERT_DEVICE := mi8937,land,santoni,prada,ulysse,ugglite,ugg,rolex,riva,Mi8937,Mi8937_4_19,Mi8937_Ld",
        ],
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
        ["obj-$(CONFIG_PRONTO_WLAN)", "prima/"],
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
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "BoardConfig.mk",
        [
            "BOARD_USES_METADATA_PARTITION := true",
            "BOARD_SUPER_PARTITION_BLOCK_DEVICES := cust system",
            "BOARD_SUPER_PARTITION_CUST_DEVICE_SIZE := 536870912",
            "BOARD_SUPER_PARTITION_SYSTEM_DEVICE_SIZE := 3221225472",
            "BOARD_MI8937_DYNPART_PARTITION_LIST := $(ALL_PARTITIONS)",
            "BOARD_VENDOR_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor",
            "BOARD_ODM_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/odm",
            "VENDOR_SECURITY_PATCH := 2017-04-01",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "sepolicy/vendor/file_contexts",
        [
            "mm-qcamera-daemon",
            "system_block_device",
            "metadata_block_device",
            "sysfs_mi8937_ts",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "sepolicy/vendor/property_contexts",
        [
            "persist.s5k3p8sp.",
            "persist.ov16885.",
            "camera_prop",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "sepolicy/vendor/file_contexts",
        [
            "wcnss_persist_file",
            "bt_firmware_file",
            "sensors_persist_file",
            "init_xiaomi_exec",
            "hal_thermal_default_exec",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "sepolicy/vendor/property_contexts",
        [
            "vendor_tee_listener_prop",
            "camera_prop",
            "vendor_wifi_version",
            "vendor_xiaomi_prop",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "manifest.xml",
        [
            '<manifest version="2.0" type="device">',
            "lineage.hardware.radio.config",
            "@1.0::IRadioConfig/default",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "manifest.xml",
        [
            "android.hardware.audio",
            "@7.0::IDevicesFactory/default",
            "android.hardware.bluetooth",
            "android.hardware.sensors",
            "vendor.qti.hardware.perf",
            "vendor.qti.hardware.qseecom",
            "vendor.display.color",
            "vendor.display.config",
            "vendor.display.postproc",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "manifest_k4.19.xml",
        [
            '<manifest version="2.0" type="device" target-level="5">',
            '<kernel target-level="6"/>',
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "framework_compatibility_matrix.xml",
        [
            '<compatibility-matrix version="2.0" type="framework">',
            "vendor.qti.hardware.perf",
            "vendor.display.color",
            "vendor.display.postproc",
            "vendor.qti.hardware.qseecom",
            "vendor.qti.hardware.bluetooth_audio",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_mithorium-common",
        "a15_qpr2/master",
        "framework_manifest.xml",
        [
            '<manifest version="1.0" type="framework">',
            "vendor.qti.hardware.radio.atcmdfwd",
            "vendor.qti.hardware.qccsyshal",
        ],
    ),
    (
        "Mi-Thorium/android_device_xiaomi_Mi8937",
        "a15_qpr2/master",
        "device.mk",
        [
            "android.hardware.biometrics.fingerprint@2.1-service.xiaomi_ulysse",
            "vendor.lineage.touch-service.xiaomi_mi8937",
            "WifiOverlay_prada",
            "fstab.qcom_ramdisk",
            "init.baseband.sh",
            "init.goodix.sh",
            "init.xiaomi.device.rc",
            "libbinder_shim.vendor",
            "camera.ulysse",
            "camera.wingtech",
        ],
    ),
    (
        "Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-4.19",
        "a15_qpr2/master",
        "mithorium-common-4.19-vendor.mk",
        [
            "vendor.qti.hardware.alarm@1.0",
            "vendor.qti.hardware.perf@2.2",
            "vendor.qti.gnss@4.1-service",
            "android.hardware.bluetooth@1.0-impl-qti",
            "libQSEEComAPI",
            "libOmxVpp",
            "libthermalclient",
            "vendor/etc/init/init_thermal-engine.rc",
        ],
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
    # Cross-check upstream device dependencies against the local Repo manifest.
    try:
        manifest_path = Path(__file__).resolve().parents[1] / "manifests/mi-thorium-lineage-22.2.xml"
        manifest_root = ET.parse(manifest_path).getroot()
        local_projects = {
            (project.get("name"), project.get("path"))
            for project in manifest_root.findall("project")
        }
        dependency_data = json.loads(fetch_text(
            "Mi-Thorium/android_device_xiaomi_Mi8937",
            "a15_qpr2/master",
            "lineage.dependencies",
        ))
        for dependency in dependency_data:
            expected = (dependency.get("repository"), dependency.get("target_path"))
            if expected not in local_projects:
                failures.append(
                    f"device dependency missing from local manifest: {expected[0]} -> {expected[1]}"
                )
                print(f"FAIL dependency {expected[0]} -> {expected[1]}")
            else:
                print(f"PASS dependency {expected[0]} -> {expected[1]}")
    except (OSError, ET.ParseError, ValueError, urllib.error.URLError) as exc:
        failures.append(f"dependency-to-manifest consistency check failed: {exc}")
        print(f"FAIL dependency-to-manifest consistency: {exc}")

    # Static partition-layout consistency audit (not a substitute for reading
    # the handset's actual GPT/partition table).
    try:
        board = fetch_text(
            "Mi-Thorium/android_device_xiaomi_Mi8937",
            "a15_qpr2/master",
            "BoardConfig.mk",
        )
        fstab = fetch_text(
            "Mi-Thorium/android_device_xiaomi_Mi8937",
            "a15_qpr2/master",
            "rootdir/etc/fstab_4_19.qcom",
        )
        def make_value(name):
            match = re.search(rf"^\s*{re.escape(name)}\s*:=\s*(.+?)\s*$", board, re.M)
            return match.group(1).strip() if match else None

        ssi = make_value("SSI_PARTITIONS")
        treble = make_value("TREBLE_PARTITIONS")
        all_parts = make_value("ALL_PARTITIONS")
        expected_parts = set((ssi or "").split() + (treble or "").split())
        all_tokens = set((all_parts or "").split())
        if all_tokens == {"$(SSI_PARTITIONS)", "$(TREBLE_PARTITIONS)"}:
            declared_parts = expected_parts
        else:
            declared_parts = all_tokens
        if not expected_parts or declared_parts != expected_parts:
            failures.append("BoardConfig partition groups are missing or inconsistent")
            print(f"FAIL partition groups: SSI={ssi!r}, TREBLE={treble!r}, ALL={all_parts!r}")
        else:
            print(f"PASS dynamic partition groups: {', '.join(sorted(expected_parts))}")

        logical_parts = set()
        for line in fstab.splitlines():
            fields = line.split()
            if len(fields) >= 5 and "logical" in fields[4].split(","):
                logical_parts.add(fields[0])
        if logical_parts != expected_parts:
            failures.append(
                f"fstab logical partitions {sorted(logical_parts)} do not match "
                f"BoardConfig partitions {sorted(expected_parts)}"
            )
            print(f"FAIL fstab logical partition set: {sorted(logical_parts)}")
        else:
            print("PASS fstab logical mounts match all five BoardConfig dynamic partitions")

        expected_layout = {
            "BOARD_SUPER_PARTITION_CUST_DEVICE_SIZE": "536870912",
            "BOARD_SUPER_PARTITION_SYSTEM_DEVICE_SIZE": "3221225472",
            "BOARD_MI8937_DYNPART_SIZE": "$(shell expr $(BOARD_SUPER_PARTITION_SIZE) - 4194304 )",
        }
        for key, value in expected_layout.items():
            if make_value(key) != value:
                failures.append(f"unexpected or missing {key} in BoardConfig")
                print(f"FAIL {key}: expected {value!r}, got {make_value(key)!r}")
        fstab_normalized = " ".join(fstab.split())
        for marker in [
            "/dev/block/by-name/oem /metadata",
            "/dev/block/by-name/userdata /data",
            "/dev/block/by-name/boot /boot",
            "/dev/block/by-name/recovery /recovery",
            "fileencryption=aes-256-xts:aes-256-cts:v2+inlinecrypt_optimized",
            "metadata_encryption=aes-256-xts",
        ]:
            if marker not in fstab_normalized:
                failures.append(f"missing critical fstab entry or encryption option: {marker}")
                print(f"FAIL fstab marker: {marker}")
        print("PASS critical boot/recovery/metadata/userdata and encryption entries present")
    except (OSError, urllib.error.URLError) as exc:
        failures.append(f"partition-layout audit fetch failed: {exc}")
        print(f"FAIL partition-layout audit: {exc}")

    if failures:
        print(f"\nFAIL: {len(failures)} of {len(CHECKS)} upstream file checks failed.")
        return 1
    print(f"\nPASS: all {len(CHECKS)} critical upstream files and markers verified.")
    print("Note: file presence/content markers do not prove complete Repo sync or build compatibility.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
