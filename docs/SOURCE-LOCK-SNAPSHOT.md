# Source revision audit — initial lock snapshot

Audit date: 2026-11-19

This file records branch-tip commit SHAs resolved through GitHub's compare endpoint with identical base/head refs. These are immutable commit identifiers for this snapshot; branch names may move later. Re-resolve and review every entry before syncing or building.

## Android 15 device/vendor source

| Repository | Manifest revision | Resolved commit |
|---|---|---|
| Mi-Thorium/android_device_xiaomi_Mi8937 | a15_qpr2/master | 9534c81fb72a3b5ed901c43c90030ca53954d05e |
| Mi-Thorium/android_device_xiaomi_mithorium-common | a15_qpr2/master | 4f4668f7014587452098875509ffa4a18721ed14 |
| Mi-Thorium/proprietary_vendor_xiaomi_Mi8937 | a15_qpr2/master | dda37856a1e538fd28fe0cb73a0f6c2ae1a29faf |
| Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common | a15_qpr2/master | 538c178c9829e208ae0d078d6e411e648dcb5f2a |
| Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-4.19 | a15_qpr2/master | 7dcd4a3aa6020e0ee4c98aca78e8b67d87df9144 |
| Mi-Thorium/android_device_xiaomi_Mi8937_4_19 | a11/master | 3ea49da1d4dc1228d746f5e14263aa9edcf73a4d |

## Kernel 4.19 manifest projects

| Repository | Manifest revision | Resolved commit |
|---|---|---|
| Mi-Thorium/kernel_msm-4.19 | mithorium/a13/master | b22b61aa0b3cce1df017905750e5399890234c10 |
| Mi-Thorium/kernel_devicetree_msm-4.19 | dts/master | 918f25d5eb8dcd965b7c68b9ac287c4168b33df6 |
| Mi-Thorium/kernel_devicetree_xiaomi-msm8937 | dts/mi8937/4.19/master | eca0b0dadbac0713824c3b42a1238c4e983982ae |
| Mi-Thorium/kernel_devicetree_xiaomi-sdm439 | dts/mi439/4.19/master | 8b2ae4cf628f1453d0dc8fd00dd070ae9fde0316 |
| Mi-Thorium/kernel_techpack_xiaomi-msm8937 | techpack/mi8937/4.19/master | 8bb3e9ba33bec89411a0309ee1c309cc06e55fb5 |
| Mi-Thorium/kernel_techpack_xiaomi-sdm439 | techpack/mi439/4.19/master | cfab702b180b3284483125c0bae8bcc1e5ec6e08 |
| Mi-Thorium/kernel_techpack_audio-legacy | audio/4.19/mithorium/master | 625b3e5d26721f927b68cd6eb8a00c8a242bb418 |
| Mi-Thorium/kernel_techpack_camera-legacy | camera/LA.UM.8.6.r1-05300-89xx.0/4.19/mithorium | a72413660fdb2dd1ae97dac7723af31bb33633f3 |
| Mi-Thorium/kernel_techpack_camera-legacy | camera/LA.UM.5.3-10610-89xx.0/4.19/mithorium | 1f56a74ef7e3bc215637e7bde627152f8ae41bc1 |
| Mi-Thorium/vendor_qcom_opensource_wlan_prima | wlan/LA.UM.9.6.4/mithorium/master | 7fbe512f0ea8cbaef681e2a54445c56e91fd80dd |

Note: the kernel manifest includes SDM439 projects in addition to MSM8937 projects. They are recorded here because they are declared by the manifest; do not assume they are needed by ugglite. The two camera-legacy entries intentionally use the same repository with different branches and checkout destinations.

## Android manifest projects still requiring resolution

The Android local manifest also declares additional projects (common graphics vendor, MiThorium hardware wrappers, LineageOS Qualcomm display interface projects, and legacy camera helper trees). These must be resolved before claiming a complete source lock. In particular:
- Resolve the exact branch tips for every remaining Mi-Thorium project.
- Resolve the upstream LineageOS projects using their actual remote and revision, not the Mi-Thorium remote.
- Inspect whether the separate `device/xiaomi/Mi8937_4_19` checkout is required by the selected product; the product makefile inspected so far inherits `device/xiaomi/Mi8937/device.mk`, so do not silently substitute one tree for the other.
- Verify whether the MiThoriumSSI project is required for this product. The attempted `a15_qpr2/master` ref did not resolve and is not pinned here.

## Status

This is a partial audit lock snapshot, not a complete repo manifest lockfile. Do not feed this partial list into a build workflow as if it were complete. The next step is to resolve the remaining manifest entries, check the separate Mi8937_4_19 tree relationship, and then generate a complete pinned manifest/lock artifact. No build or device operation is authorized by this document.

## Additional Android manifest revisions resolved in follow-up audit

| Repository | Manifest revision | Resolved commit |
|---|---|---|
| Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-graphics | a15_qpr2/master | 84fc1d44483139d6355347a4bc98b172bac6f69b |
| Mi-Thorium/android_device_xiaomi_land-camera | sairam/a11/master | 6d9a98c2ab3b7e8e87956f79997029e1d4b69bb8 |
| Mi-Thorium/android_device_xiaomi_mi8937-camera | a11/master | 54d8909022b1244b90189cccd8d792993cb2c643 |
| Mi-Thorium/android_device_xiaomi_prada-camera | a11/master | bb003d61929ffb7a33a3acd2f0dfbea411fe8c4b |
| LineageOS/android_hardware_qcom_media | lineage-21.0-caf-msm8953 | 90a808309f461f139161f504e44e341f4f6f2fb6 |
| LineageOS/android_hardware_qcom_display | lineage-21.0-caf-msm8953 | d0107598e13d1b7df25e97214c195a501b3ec348 |

The LineageOS display-commonsys-intf project did not resolve under the repository name as written in the local manifest; its upstream repository identity/remote mapping needs verification before pinning.
