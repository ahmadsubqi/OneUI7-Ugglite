# Kernel 4.19 integration notes

## Verified manifest layout

Source manifest: `Mi-Thorium/kernel_manifest`, branch `mithorium-4.19`, file `default.xml`.

The manifest declares the main kernel project at checkout path `kernel`, not at the final Android tree path. Its linkfiles place additional repositories into the kernel source tree:

- `dts/vendor-legacy` -> `kernel/arch/arm64/boot/dts/vendor-legacy`
- `dts/xiaomi-msm8937` -> `kernel/arch/arm64/boot/dts/xiaomi-msm8937`
- `module/xiaomi-msm8937` -> `kernel/techpack/xiaomi-msm8937`
- `module/audio-legacy` -> `kernel/techpack/audio-legacy`
- `module/camera-legacy` -> `kernel/techpack/camera-legacy`
- `module/camera-legacy-m` -> `kernel/techpack/camera-legacy-m`
- `module/prima` -> `kernel/drivers/staging/prima`

The two camera-legacy projects use the same repository name but different branch revisions and checkout paths. Preserve both entries exactly as the manifest declares.

## Safe sync procedure

Do not run `repo init` inside the Android ROM checkout. Sync the kernel manifest in a separate directory, then move the completed checkout to the exact directory expected by the device tree:

```sh
mkdir -p ~/mithorium-4.19
cd ~/mithorium-4.19
repo init -u https://github.com/Mi-Thorium/kernel_manifest -b mithorium-4.19 --no-clone-bundle
repo sync -c -j"$(nproc --all)" --no-clone-bundle --no-tags

# After sync succeeds, place it in the Android source tree:
mkdir -p ~/android/lineage-22.2/kernel/xiaomi
mv -T ~/mithorium-4.19 ~/android/lineage-22.2/kernel/xiaomi/mithorium-4.19
```

Expected kernel source path from the common BoardConfig is:

`kernel/xiaomi/mithorium-4.19/kernel`

The destination path above is consistent with that expectation. Confirm the exact Android source root and branch name before executing; these commands are a layout recipe, not an instruction to start a build now.

## Device-tree checks

- `lineage_Mi8937_4_19.mk` exists on the Android 15 `a15_qpr2/master` branch.
- `AndroidProducts.mk` on that branch offers `lineage_Mi8937_4_19-userdebug`.
- The product makefile inherits `device/xiaomi/Mi8937/device.mk`.
- `device.mk` adds `xiaomi_ugglite_overlay`, so the ugglite overlay is inherited even though the product-specific `overlay-lineage` package list does not name it.
- `BoardConfig.mk` includes `ugglite` in `TARGET_OTA_ASSERT_DEVICE`.
- The 4.19 configuration disables Camera HAL1 (`TARGET_SUPPORT_HAL1 := false`).

The Android 15 product makefile and product list were also checked on `a15_qpr2/master`; do not confuse this with the older `a11/master` revision that appears in some older manifests/guides.

## Revision observations (not a lockfile)

- Kernel branch `mithorium/a13/master` currently resolves in the observed audit to commit `b22b61aa0b3cce1df017905750e5399890234c10`.
- The MSM8937 DTS branch `dts/mi8937/4.19/master` exists. A recent-commit search returned `dedb5f8091aae81058865d385241d2eedb72e4fe`, but this search result is not a reliable proof that it is the branch tip.
- All manifest projects still need exact branch-tip SHA resolution and a complete immutable lockfile before a reproducible build.

## References

- Kernel manifest: https://github.com/Mi-Thorium/kernel_manifest/blob/mithorium-4.19/default.xml
- Android 15 device product: https://github.com/Mi-Thorium/android_device_xiaomi_Mi8937/blob/a15_qpr2/master/lineage_Mi8937_4_19.mk
- Product list: https://github.com/Mi-Thorium/android_device_xiaomi_Mi8937/blob/a15_qpr2/master/AndroidProducts.mk
- Device package list: https://github.com/Mi-Thorium/android_device_xiaomi_Mi8937/blob/a15_qpr2/master/device.mk
- Board configuration: https://github.com/Mi-Thorium/android_device_xiaomi_Mi8937/blob/a15_qpr2/master/BoardConfig.mk
- Community integration guide (secondary source): https://github.com/rigaz29/riva-lineageos-guide

## Safety gate

No flashing, repartitioning, recovery installation, firmware downgrade, or device write operation is part of this stage. Build only after all Android, vendor, kernel, DTS, and module revisions have been pinned and audited.