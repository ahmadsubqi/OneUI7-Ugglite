# Android 15 Baseline Build Plan

## Target

- Device: Xiaomi Redmi Note 5A Lite (`ugglite`)
- Baseline: LineageOS 22.2 / Android 15 (API 35)
- Product: `lineage_Mi8937_4_19-userdebug`
- Kernel: Mi-Thorium MSM8937 Linux 4.19.325
- Later objective: One UI 7 framework/UI research and porting. A successful LineageOS baseline is not a One UI 7 ROM.

## Source layout

Android source root: `$ANDROID_ROOT`

Kernel Repo client is synchronized OUTSIDE the Android Repo checkout, then moved to:

`$ANDROID_ROOT/kernel/xiaomi/mithorium-4.19`

The kernel source path expected by `BoardConfigCommon.mk` is:

`kernel/xiaomi/mithorium-4.19/kernel`

**Do not run `repo init` inside the Android source checkout to create a second Repo client.** The build script uses a sibling directory `../kernel-sync/mithorium-4.19`, initializes and syncs the kernel manifest there, writes its pinned manifest, and only then moves the complete Repo checkout to the expected `TARGET_KERNEL_SOURCE` path. On a later run, it moves the existing kernel Repo checkout back to the sibling sync directory before updating it. This preserves the Android source root's own `.repo` metadata.

The kernel manifest's project path `kernel` resolves to the source directory above. DTS and techpack linkfiles are relative to the separate kernel Repo client root and remain valid when the entire client directory is moved.

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

Full build workflow: `.github/workflows/build-android15.yml` (self-hosted runner only).

Lightweight validation workflow: `.github/workflows/validate-config.yml` (GitHub-hosted runner; checks Bash syntax, local manifest/configuration, and existence of Mi-Thorium Git branch refs. It does not sync the Android source tree or compile Android).

Validation scripts: `scripts/validate-config.py`, `scripts/validate-refs.py`, and `scripts/validate-upstream-files.py`

Build script: `scripts/build-android15.sh`

The script:
1. Checks Linux x86_64, Ubuntu, RAM and free disk.
2. Initializes LineageOS 22.2 and installs the project's Mi-Thorium local manifest.
3. Syncs the Android source, applies the checked-in Mi-Thorium audio HAL Clang compatibility patch, and emits `pinned-android-manifest.xml` using `repo manifest -r`.
4. Initializes a separate kernel Repo client in a sibling directory OUTSIDE the Android source checkout.
5. Syncs the kernel/DTS/techpack source, emits `pinned-kernel-manifest.xml`, and moves the complete kernel Repo checkout into the exact nested source path expected by BoardConfig.
6. Checks kernel version, MSM8937 defconfig, ugglite DTS, device product makefile, ugglite overlay, and the required Mi8937 / MiThorium 4.19 vendor makefiles.
7. Runs `lunch lineage_Mi8937_4_19-userdebug` and `mka bacon`.
8. Requires a newly produced flashable ZIP, then copies ZIP/images and pinned manifests into build artifacts.

The source branches are resolved to immutable revisions by Repo during sync. The two `repo manifest -r` lockfiles are the reproducibility record for the actual source checkout used in that build.

## Known Android 15 audio HAL compatibility patch

The selected Mi-Thorium audio HAL branch currently resolves to commit prefix `a3ff9d54`. Its `cirrus_playback.c` and `spkr_protection.c` thread definitions contain unnamed `void*` parameters. That is a C23 extension and can be rejected by Clang when compiling as GNU99 with `-Werror`.

A small compatibility patch is stored at:

`patches/0001-audio-extn-name-unused-pthread-parameters.patch`

After Android source sync, the build script checks and applies this patch to the audio HAL Repo checkout. It skips the patch if it is already applied and fails early if the patch no longer applies cleanly. The upstream preflight checks the affected source signatures so a future upstream change is visible.

This is a source-level compatibility fix based on the current upstream code. It has not yet been validated by a full Android compilation.

## Current gate

The workflow and scripts are prepared, but the build cannot start until an online self-hosted runner with the required resources is registered and labelled `android-build`. A public GitHub repository does not provide extra disk or RAM on standard hosted runners.

No build has been claimed successful. No ROM has been flashed.
