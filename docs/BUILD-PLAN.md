# Android 15 Baseline Build Plan

## Target

- Device: Xiaomi Redmi Note 5A Lite (`ugglite`)
- Baseline: LineageOS 22.2 / Android 15 (API 35)
- Product: `lineage_Mi8937_4_19-userdebug`
- Kernel: Mi-Thorium MSM8937 Linux 4.19.325
- Later objective: One UI 7 framework/UI research and porting. A successful LineageOS baseline is not a One UI 7 ROM.

## Source layout

Android source root: `$ANDROID_ROOT`

Kernel Repo client root: `$ANDROID_ROOT/kernel/xiaomi/mithorium-4.19`

Kernel source path expected by `BoardConfigCommon.mk`:

`kernel/xiaomi/mithorium-4.19/kernel`

The kernel is intentionally managed by a **separate nested Repo client**. Run the kernel manifest initialization from `kernel/xiaomi/mithorium-4.19`, not from the Android root. The kernel manifest's project path `kernel` then resolves exactly to the source path expected by `TARGET_KERNEL_SOURCE`. Its DTS and techpack linkfiles are also relative to this nested Repo client root.

## Device-tree observations

- The Mi8937 unified device tree includes `ugglite` in its OTA assert list.
- `device.mk` packages `xiaomi_ugglite_overlay`.
- The product makefile selects `TARGET_KERNEL_VERSION := 4.19`.
- Kernel 4.19 configuration disables legacy Camera HAL1 support. Camera support is a known risk and must be tested; do not promise it works.
- Partition and fstab declarations in source are assumptions until compared with the physical handset. No flashing or repartitioning is part of this build workflow.

## Build-host requirements

Google's current AOSP build guidance recommends a 64-bit x86 host, at least 400 GB free disk, and at least 64 GB RAM. The workflow therefore targets a Linux x86_64 self-hosted GitHub Actions runner labelled `android-build`.

Standard GitHub-hosted runners are not suitable: their standard Linux runner has 16 GB RAM and 14 GB SSD. GitHub larger runners with 64 GB RAM / 600 GB SSD require an organization on GitHub Team or Enterprise Cloud. This project must not start a full sync/build on a standard runner because it will fail for disk and memory limits.

## Build automation

Workflow: `.github/workflows/build-android15.yml`

Script: `scripts/build-android15.sh`

The script:
1. Checks Linux x86_64, Ubuntu, RAM and free disk.
2. Initializes LineageOS 22.2 and installs the project's Mi-Thorium local manifest.
3. Syncs the Android source and emits `pinned-android-manifest.xml` using `repo manifest -r`.
4. Initializes a separate kernel Repo client in the exact nested path expected by BoardConfig.
5. Syncs the kernel/DTS/techpack source and emits `pinned-kernel-manifest.xml`.
6. Checks kernel version, MSM8937 defconfig, ugglite DTS, device product makefile and overlay.
7. Runs `lunch lineage_Mi8937_4_19-userdebug` and `mka bacon`.
8. Copies produced ZIP/images and pinned manifests into build artifacts.

The source branches are resolved to immutable revisions by Repo during sync. The two `repo manifest -r` lockfiles are the reproducibility record for the actual source checkout used in that build.

## Current gate

The workflow and scripts are prepared, but the build cannot start until an online self-hosted runner with the required resources is registered and labelled `android-build`. A public GitHub repository does not provide extra disk or RAM on standard hosted runners.

No build has been claimed successful. No ROM has been flashed.
