# Source verification plan

## Device identity

- Device: Xiaomi Redmi Note 5A Lite / Redmi Y1 Lite
- Codename: `ugglite`
- SoC: Qualcomm MSM8937 / Snapdragon 425
- GPU: Adreno 308
- Memory/storage: 2 GB RAM / 16 GB storage
- Current software reported by owner: custom LineageOS, Android 16
- Bootloader reported unlocked; handset is temporarily unavailable for ADB inspection

The Mi-Thorium Mi8937 unified device tree explicitly includes `ugglite` in its OTA assert list and packages an ugglite overlay. The product is unified as `Mi8937`, not a standalone `ugglite` lunch product.

## Android 15 source lead

The Mi-Thorium `local_manifests/lineage-22.2.xml` manifest selects the `a15_qpr2/master` source family. It references:

- `Mi-Thorium/android_device_xiaomi_Mi8937`
- `Mi-Thorium/android_device_xiaomi_mithorium-common`
- `Mi-Thorium/proprietary_vendor_xiaomi_Mi8937`
- `Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common`
- `Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-4.19`

The Mi8937 tree on `a15_qpr2/master` declares `lineage_Mi8937_4_19`, with `TARGET_KERNEL_VERSION := 4.19`. Its BoardConfig includes `ugglite` in `TARGET_OTA_ASSERT_DEVICE`. This establishes a credible Android 15 device-tree lead, not a successful build or boot on this user's physical handset.

## Kernel validation — source pairing found, exact pin still needed

The Android source manifest does not directly declare the kernel project. The separate repository `Mi-Thorium/kernel_manifest` has a branch named `mithorium-4.19`; its `default.xml` was inspected.

That kernel manifest maps the expected kernel stack as follows:

- Kernel project: `Mi-Thorium/kernel_msm-4.19`
- Kernel branch: `mithorium/a13/master`
- DTS project: `Mi-Thorium/kernel_devicetree_msm-4.19`, branch `dts/master`
- Xiaomi MSM8937 DTS project: `Mi-Thorium/kernel_devicetree_xiaomi-msm8937`, branch `dts/mi8937/4.19/master`
- Xiaomi MSM8937 techpack project: `Mi-Thorium/kernel_techpack_xiaomi-msm8937`, branch `techpack/mi8937/4.19/master`
- Additional audio, camera and WLAN techpack/module projects are also declared by that kernel manifest.

The kernel manifest's kernel project uses path `kernel` inside the kernel-manifest checkout. The Android common BoardConfig constructs `TARGET_KERNEL_SOURCE` as `kernel/xiaomi/mithorium-$(TARGET_KERNEL_VERSION)/kernel`; therefore the kernel manifest must be initialized in the expected nested directory/layout, not blindly synced at the Android source root. Confirm the maintainer's intended integration instructions before writing CI checkout steps.

The kernel branch Makefile reports Linux 4.19.325. Its `arch/arm64/configs/vendor/msm8937-perf_defconfig` exists and enables `CONFIG_ARCH_MSM8937=y`. Relevant MSM8937 clock, board, pinctrl and platform code is present. The 4.19-specific DTS and techpack branches also exist.

Independent community build evidence was found for Mi8937 / Android 15:
- LineageOS 22.1 / Android 15 builds for `Mi8937_4_19` were reported in January 2025 with kernel 4.19.325.
- A LineageOS 22.2 / Android 15 build for the unified Mi8937 family was reported on 4 November 2026 with a 4.19.325 Mi8937 kernel.

This is meaningful evidence that the MiThorium 4.19 kernel family can be used with Android 15 on Mi8937 devices. It does **not** guarantee that the current `a15_qpr2/master` device/vendor revisions and the floating kernel branches are mutually synchronized, or that this user's handset will boot.

## Kernel assessment

Status: `PROMISING — NEEDS EXACT REVISION AND INTEGRATION CHECK`.

A branch name containing `a13` does not mean the kernel is Android-13-only: the separate kernel manifest deliberately selects that branch for its 4.19 kernel stack, and community Android 15 builds provide supporting evidence. However, the manifest points to moving branch names rather than immutable commit SHAs. Record the actual resolved SHAs for every kernel/DTS/module project before CI build reproducibility can be claimed.

The Android 15 common BoardConfig appends kernel fragments under `arch/arm64/configs/vendor/`, including `vendor/msm8937-legacy.config`. The inspected kernel branch contains that file, but its contents mainly enable legacy MSM8917/MSM8920/MSM8940 options; it does not by itself establish complete ugglite support. The base `msm8937-perf_defconfig` does enable MSM8937. A full fragment merge and kernel build test is still required.

## Vendor and partition cautions

The vendor/common projects are referenced by the Android 15 manifest, but proprietary blob compatibility and redistribution rights remain to be assessed. The device tree enables retrofit dynamic partitions and declares a super layout; this is not proof of the handset's actual partition map. Do not flash or repartition based on build files alone.

## Current feasibility assessment

There is a plausible Android 15 LineageOS/AOSP device baseline to investigate. It is not Samsung One UI 7. Samsung framework services, proprietary libraries, SELinux rules, camera/audio/radio HALs, graphics, and vendor interfaces remain major compatibility work. A full One UI 7 port is high risk on a 2 GB / 16 GB Snapdragon 425 device.

## Next source-audit gates

1. Confirm the expected nested checkout layout for `kernel_manifest` and its integration with the Android source tree.
2. Resolve and record immutable commit SHAs for the kernel, MSM8937 DTS, and techpack/module projects.
3. Inspect the Mi8937 4.19 device tree, common tree, vendor tree, fstab and module-loading rules.
4. Run a non-flashing Android 15 baseline build only after source pairing is pinned.
5. Compare partition assumptions against the physical handset only when it is available.

## Required data when handset is available

Collect and archive:

```sh
adb shell getprop ro.product.device
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
adb shell getprop ro.build.fingerprint
adb shell getprop ro.product.cpu.abi
adb shell getprop ro.treble.enabled
adb shell uname -a
adb shell cat /proc/meminfo
adb shell cat /proc/partitions
adb shell ls -l /dev/block/by-name/
```

Also record exact ROM build, firmware/modem version, recovery version, dynamic-partition status, encryption state, and a verified backup/recovery path. Redact serial numbers, IMEI, Wi-Fi MAC addresses, and other unique identifiers before sharing logs.

## Safety

No flashing, repartitioning, bootloader relocking, or firmware downgrade is authorized by this plan. Do not publish proprietary Samsung files, signing keys, credentials, or device-identifying logs.
