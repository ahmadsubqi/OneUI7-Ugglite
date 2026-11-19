# Source verification plan

## Device identity

- Device: Xiaomi Redmi Note 5A Lite / Redmi Y1 Lite
- Codename: `ugglite`
- SoC: Qualcomm MSM8937 / Snapdragon 425
- GPU: Adreno 308
- Memory/storage: 2 GB RAM / 16 GB storage
- Current software reported by owner: custom LineageOS, Android 16
- Bootloader reported unlocked; handset is temporarily unavailable for ADB inspection

The Mi-Thorium unified Mi8937 device tree explicitly lists `ugglite` in `TARGET_OTA_ASSERT_DEVICE` and packages `xiaomi_ugglite_overlay`. This is a unified product family, not a dedicated `ugglite` lunch target.

## Android 15 source lead

The Mi-Thorium `local_manifests/lineage-22.2.xml` manifest selects the `a15_qpr2/master` source family. It references the Mi8937 device tree, Mithorium common tree, and matching vendor repositories.

The Android 15 device tree declares:
- Product makefile: `lineage_Mi8937_4_19.mk`
- Lunch target: `lineage_Mi8937_4_19-userdebug`
- `TARGET_KERNEL_VERSION := 4.19`
- `ugglite` in the unified OTA assert list
- `xiaomi_ugglite_overlay` in the installed overlay packages

This is a credible Android 15 device-tree lead, not proof of a successful build or boot on this physical handset.

## Kernel validation — source pairing found

The Android source manifest does not directly declare the kernel project. The separate repository `Mi-Thorium/kernel_manifest`, branch `mithorium-4.19`, has an inspected `default.xml` that maps the 4.19 kernel stack:

- Kernel: `Mi-Thorium/kernel_msm-4.19`, branch `mithorium/a13/master`
- Common DTS: `Mi-Thorium/kernel_devicetree_msm-4.19`, branch `dts/master`
- Xiaomi MSM8937 DTS: `Mi-Thorium/kernel_devicetree_xiaomi-msm8937`, branch `dts/mi8937/4.19/master`
- Xiaomi MSM8937 techpack: `Mi-Thorium/kernel_techpack_xiaomi-msm8937`, branch `techpack/mi8937/4.19/master`
- Additional audio, camera and WLAN techpack/module projects are declared by the same manifest.

The kernel Makefile reports Linux 4.19.325. Its ARM64 `vendor/msm8937-perf_defconfig` exists and enables `CONFIG_ARCH_MSM8937=y`. Relevant MSM8937 platform code and the matching 4.19 DTS/techpack branches are present.

The common BoardConfig constructs `TARGET_KERNEL_SOURCE` as `kernel/xiaomi/mithorium-$(TARGET_KERNEL_VERSION)/kernel`. The kernel manifest itself checks out the main kernel project at path `kernel`. The correct layout is a separate, nested Repo client rooted at `kernel/xiaomi/mithorium-4.19`; its `path="kernel"` project then lands exactly at the expected `TARGET_KERNEL_SOURCE` path `kernel/xiaomi/mithorium-4.19/kernel`. Initialize the kernel manifest from that nested client root, not from the Android source root. The manifest's DTS and techpack linkfile destinations are also relative to that nested root and must be checked after sync.

Community evidence exists for a Mi8937 LineageOS 22.2 / Android 15 build dated 4 November 2026, reporting kernel 4.19.325. This supports the kernel family pairing but does not prove that the current floating Android device/vendor branches and kernel subprojects resolve to the exact same source set.

## Device-tree and vendor audit

Inspected `BoardConfig.mk`, `AndroidProducts.mk`, `device.mk`, `lineage_Mi8937_4_19.mk`, `rootdir/etc/fstab_4_19.qcom`, `manifest_k4.19.xml`, and vendor makefiles.

Findings:
- `AndroidProducts.mk` offers `lineage_Mi8937_4_19-userdebug`; there is no separate `lineage_ugglite` target.
- The 4.19 product inherits the common Mi8937 device configuration and includes the ugglite overlay.
- `manifest_k4.19.xml` declares device target-level 5 and kernel target-level 6.
- The 4.19 BoardConfig sets `TARGET_SUPPORT_HAL1 := false`; the legacy Camera HAL1 path is intentionally disabled for this kernel family. Camera behavior must be tested; do not promise full legacy camera compatibility.
- The device fstab assumes logical system/system_ext/product/vendor/odm partitions, an `oem` block device mounted at `/metadata`, and particular boot/recovery/cache/userdata/by-name paths.
- The build config declares retrofit dynamic partitions, a super layout using `cust` and `system`, and a userdata image size around 10.3 GB. These are source assumptions only, not verified facts about the user's handset.
- The vendor file list includes legacy Xiaomi blob sources, including an entry comment identifying the `ugg` package as Android 7.1.2. Compatibility shims and HAL integration therefore remain a significant risk for Android 15.
- The common tree includes a 512 MB Dalvik heap configuration, relevant to a device with only 2 GB RAM, but runtime performance still needs real-device testing.

## Revision pinning status

The kernel branch search and commit history identify kernel commit candidate `b22b61aa0b3cce1df017905750e5399890234c10` (4.19.325, merged into `mithorium/a13/master`). Recent commit candidates observed for the Android device/common trees include `27f9bcfe3d4d2c4ffb45f719af51dfaf62c5f26e` and `d3292cac56e76648e567dd2e93518c1b54983dd9`.

These are audit observations, not yet a complete reproducible lockfile: exact branch-to-SHA resolution is still required for every kernel, DTS, module, device, common and vendor project. Mi-Thorium also notes that its repositories may be force-pushed, so floating branch names should not be treated as immutable.

## Current assessment

Status: `PROMISING AND SOURCE-PAIRED AT THE FAMILY LEVEL; NOT YET BUILD-READY`.

There is a plausible Android 15 LineageOS/AOSP baseline for the unified Mi8937 family, including ugglite overlay support and a 4.19 kernel source stack. No baseline build has yet been run in this project. This is not Samsung One UI 7. A full One UI 7 port still faces major framework, proprietary library, SELinux, camera/audio/radio HAL, graphics, and vendor-interface work. It is especially high risk on a 2 GB RAM / 16 GB storage Snapdragon 425 device.

## Next source-audit gates

1. Resolve exact immutable commit SHAs for every manifest project and every kernel-manifest subproject.
2. Verify the intended kernel-manifest checkout layout and required symlink setup.
3. Inspect all ugglite-specific overlay, fstab, init, DTS, and module-loading dependencies.
4. Verify vendor blob extraction provenance and Android 15 compatibility.
5. Run a non-flashing Android 15 baseline build only after all revisions and source paths are pinned.
6. Compare partition assumptions against the physical handset only when it is available.

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
