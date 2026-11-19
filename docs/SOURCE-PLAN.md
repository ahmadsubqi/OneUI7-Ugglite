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

The Mi8937 tree on `a15_qpr2/master` declares `lineage_Mi8937_4_19`, with `TARGET_KERNEL_VERSION := 4.19`. Its BoardConfig includes `ugglite` in `TARGET_OTA_ASSERT_DEVICE`. This establishes a credible Android 15 device-tree lead, not a successful build or boot.

## Kernel validation — blocker

Inspected `Mi-Thorium/local_manifests/lineage-22.2.xml`:

- It does **not** declare a kernel project for `kernel/xiaomi/mithorium-4.19/kernel`.
- The Android 15 common BoardConfig expects the kernel source at that exact path when `TARGET_KERNEL_VERSION=4.19`.
- The manifest separately declares `device/xiaomi/Mi8937_4_19` at revision `a11/master`; this is a device-tree project, not the kernel repository.

Inspected `Mi-Thorium/kernel_msm-4.19`:

- The available branch search returned `mithorium/a13/master`, older A13 branches, and a `mithorium/lineage-21` family.
- Searching the same repository for `a15` returned no branch.
- `mithorium/a13/master` reports kernel version 4.19.325 in its Makefile.
- Its `arch/arm64/configs/vendor/msm8937-perf_defconfig` exists and enables `CONFIG_ARCH_MSM8937=y`.
- The kernel source contains MSM8937-specific clock, board, pinctrl and platform code.

Assessment: this kernel tree has relevant MSM8937 hardware support, but its visible branch lineage is A13/Lineage 21 rather than Android 15. No manifest pin links it to the Android 15 device tree. **Do not add it to the Android 15 manifest or claim compatibility yet.** A kernel version match (4.19) and SoC config match are not sufficient to prove Android 15 vendor ABI, required config fragments, DTB/DTBO, modules, or boot compatibility.

## Additional configuration concern

The Android 15 common BoardConfig appends kernel fragments under `arch/arm64/configs/vendor/`, including `vendor/msm8937-legacy.config`. The inspected kernel branch contains that file, but its contents mainly enable legacy MSM8917/MSM8920/MSM8940 options; it does not by itself establish complete ugglite support. The base `msm8937-perf_defconfig` does enable MSM8937. A full fragment merge and kernel build test is still required.

## Vendor and partition cautions

The vendor/common projects are referenced by the Android 15 manifest, but proprietary blob compatibility and redistribution rights remain to be assessed. The device tree enables retrofit dynamic partitions and declares a super layout; this is not proof of the handset's actual partition map. Do not flash or repartition based on build files alone.

## Current feasibility assessment

There is a plausible Android 15 LineageOS/AOSP device baseline to investigate. It is not Samsung One UI 7. Samsung framework services, proprietary libraries, SELinux rules, camera/audio/radio HALs, graphics, and vendor interfaces remain major compatibility work. A full One UI 7 port is high risk on a 2 GB / 16 GB Snapdragon 425 device.

## Next source-audit gates

1. Find a kernel branch/commit explicitly used with the Mi8937 4.19 device tree, or obtain maintainer confirmation for the Android 15 combination.
2. Compare the complete kernel config fragments and device-specific DTS/DTB/DTBO setup.
3. Inspect the Mi8937 4.19 device tree, common tree, vendor tree, fstab and module-loading rules.
4. Run a non-flashing Android 15 baseline build only after source pairing is resolved.
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
