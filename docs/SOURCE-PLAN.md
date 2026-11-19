# Source verification plan

## Device identity

- Commercial name: Xiaomi Redmi Note 5A Lite (reported by owner)
- Codename supplied by owner: `ugglite`
- SoC family: Qualcomm Snapdragon 425 / MSM8937 (to verify against authoritative device sources)
- Memory: 2 GB RAM / 16 GB storage
- Current software reported by owner: custom LineageOS, Android 16
- Bootloader: unlocked (reported by owner)
- Physical device: temporarily unavailable for ADB inspection

## Candidate repositories (unverified)

| Role | Candidate | Required verification |
|---|---|---|
| Device tree | `ancient-devices/device_xiaomi_ulysse` | Confirm ugglite target, branches, Android version, dependencies |
| Kernel | `xiaomi-ulysse/android_kernel_xiaomi_msm8937` | Confirm device support, kernel version, defconfig, toolchain and license |
| Recovery | `xiaomi-ulysse/twrp_device_xiaomi_ugglite` | Confirm partition map, fstab, boot/recovery format |

These are discovery leads, not approved build inputs. The audit workflow checks remote branch visibility only; it does not establish compatibility.

## Required data when handset is available

Collect and archive output from:

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

Also record the exact installed ROM build, firmware/modem version, recovery version, dynamic-partition status, encryption state, and a verified backup/recovery path. Redact serial numbers, IMEI, Wi-Fi MAC addresses, and other unique identifiers before sharing logs.

## Android 15 / One UI 7 feasibility gates

1. Confirm a viable Android 15 device/vendor baseline for ugglite.
2. Determine whether the existing Android 16 vendor and kernel can support the required Android 15 interfaces; do not assume downgrade compatibility.
3. Verify graphics, camera, audio, radio, Wi-Fi, Bluetooth, sensors, power and SELinux integration.
4. Assess Samsung framework dependencies and proprietary components. A complete One UI 7 port may prove infeasible; a hybrid AOSP base with selected compatible Samsung UI components may be the practical fallback.
5. Establish image sizes and partition capacity before any packaging or flashing.

## Safety

No flashing, repartitioning, bootloader relocking, or firmware downgrade is authorized by this plan. Do not publish proprietary Samsung files, signing keys, credentials, or device-identifying logs.
