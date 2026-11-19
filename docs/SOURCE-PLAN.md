# Source verification plan

## Device identity (owner-reported / source-confirmed)

- Device: Xiaomi Redmi Note 5A Lite / Redmi Y1 Lite
- Codename: `ugglite`
- SoC: Qualcomm MSM8937 / Snapdragon 425
- GPU: Adreno 308
- Memory/storage: 2 GB RAM / 16 GB storage
- Current software reported by owner: custom LineageOS, Android 16
- Bootloader reported unlocked; handset is temporarily unavailable for ADB inspection

The Mi-Thorium Mi8937 unified device tree explicitly includes `ugglite` in its OTA assert list and includes an overlay for `ugglite`. The product is unified as `Mi8937`, not a standalone `ugglite` lunch product.

## Best current Android 15 source lead

The Mi-Thorium `local_manifests/lineage-22.2.xml` manifest selects the `a15_qpr2/master` source family. Its Mi8937 project is:

- Device tree: `Mi-Thorium/android_device_xiaomi_Mi8937`
- Branch: `a15_qpr2/master`
- Android product file: `lineage_Mi8937_4_19.mk`
- Product name: `lineage_Mi8937_4_19`
- Kernel selection: `TARGET_KERNEL_VERSION := 4.19`

The corresponding device tree `BoardConfig.mk` configures the unified Mi8937 family, including `ugglite`. Its device makefile enables retrofit dynamic partitions. The source's declared super layout is not proof of the physical handset's actual partition map; never flash or repartition based only on this build configuration.

Kernel repository lead:

- `Mi-Thorium/kernel_msm-4.19`
- A publicly visible branch family includes `mithorium/a13/master`
- The inspected Makefile reports Linux kernel 4.19.325.
- This does **not** prove that the Android 15 manifest's kernel project resolves to this exact branch or commit. Verify the kernel manifest and commit pin before syncing/building.

Vendor/common repositories referenced by the Android 15 manifest:

- `Mi-Thorium/proprietary_vendor_xiaomi_Mi8937`
- `Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common`
- `Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-4.19`
- `Mi-Thorium/android_device_xiaomi_mithorium-common`

These are build inputs to audit, not proof that every proprietary component is compatible or redistributable.

## Verified technical observations

- The unified device tree's Android 15 branch declares `core_64_bit.mk`.
- It declares a `lineage_Mi8937_4_19` product using kernel version 4.19.
- It enables retrofit dynamic partitions in `device.mk`.
- The device tree lists `ugglite` as a supported OTA assert device and packages a ugglite overlay.
- The Android 15 manifest is a LineageOS 22.2 / Android 15-based community source baseline, **not Samsung One UI 7**.

## Current feasibility assessment

There is a plausible Android 15 AOSP/LineageOS device baseline to investigate. That is a useful starting point for a custom ROM, but it does not establish that a full Samsung One UI 7 framework port is feasible. Samsung framework services, proprietary libraries, SELinux rules, camera/audio/radio HALs, graphics, and vendor interfaces remain major compatibility work. A full One UI 7 port is high risk on a 2 GB / 16 GB Snapdragon 425 device.

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

Also record exact ROM build, firmware/modem version, recovery version, dynamic-partition status, encryption state, and a verified backup/recovery path. Redact serial numbers, IMEI, Wi-Fi MAC addresses, and other unique identifiers before sharing logs.

## Next source-audit gates

1. Run the GitHub Actions source audit and save its artifact.
2. Verify the exact Android 15 kernel manifest entry and commit pin.
3. Inspect the Mi8937 4.19 device tree, common tree, vendor tree and fstab.
4. Confirm the Android 15 branch can build before adding Samsung framework components.
5. Compare source partition assumptions against the physical phone only when it is available.

## Safety

No flashing, repartitioning, bootloader relocking, or firmware downgrade is authorized by this plan. Do not publish proprietary Samsung files, signing keys, credentials, or device-identifying logs.
