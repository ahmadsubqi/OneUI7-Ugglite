# OneUI7-Ugglite

Experimental research project for investigating a Samsung One UI 7 (Android 15) port for Xiaomi Redmi Note 5A Lite (**ugglite**, Snapdragon 425/MSM8937, 2 GB RAM / 16 GB storage).

## Status

**Preparation / source audit only. No flashable ROM exists.**

The device is currently reported by its owner to run a custom LineageOS Android 16 build. The handset is not currently available for live ADB inspection, so partition layout, boot image format, vendor state, firmware level, and exact kernel branch remain unverified.

## Important technical constraints

- One UI 7 is based on Android 15 (API 35); the reported installed ROM is Android 16 (API 36). These are different platform generations and are not interchangeable.
- A full Samsung framework port is substantially harder than a launcher/theme port. Samsung framework, proprietary services, native libraries, HALs, SELinux policy, and device-specific blobs must be compatible.
- Do not assume an Android 15 GSI or Samsung system image will boot on this device.
- The 2 GB RAM / 16 GB storage configuration imposes severe runtime and system-image constraints.
- No partition resizing, bootloader flashing, or device modification should be attempted until a verified recovery and exact partition map are available.

## Initial workflow

GitHub Actions workflow `.github/workflows/source-audit.yml` performs a read-only remote source audit. It does not build Android, download proprietary firmware, or produce a flashable image.

## Source policy

Use public device/kernel sources only as research references. Verify repository ownership, target device, branch history, kernel version, license, and compatibility before adopting anything. Proprietary Samsung firmware and blobs must be obtained lawfully by the project owner; do not commit copyrighted firmware or private keys.

## Planned milestones

1. Identify exact device and audit candidate source repositories.
2. Verify ugglite device tree, common tree, kernel, vendor and recovery sources.
3. Establish Android 15 bring-up feasibility against the device's actual vendor/firmware baseline.
4. Prototype compatible Samsung UI/framework components.
5. Build and test incrementally on a physical device.

See [SOURCE-PLAN.md](docs/SOURCE-PLAN.md).


A separate free GitHub-hosted kernel/DTB workflow is available at `.github/workflows/kernel-build-ugglite.yml`. It is intended to test the kernel build independently; it does not build the Android system image or a flashable ROM. The full Android build still requires a larger Linux x86_64 runner.
