# Adreno 308 / Qualcomm graphics audit — ugglite

Audit date: 2026-11-19
Target: Xiaomi Redmi Note 5A Lite / Redmi Y1 Lite (`ugglite`), MSM8937, Adreno 308
Android source baseline: Mi-Thorium `a15_qpr2/master`, kernel 4.19 branch `mithorium/a13/master`.

## Executive result

The kernel source does include the Qualcomm KGSL driver and an MSM8937 GPU device-tree node. The selected proprietary graphics package contains Adreno EGL/GLES libraries for both 32-bit and 64-bit userspace, plus Qualcomm graphics support libraries and a Vulkan driver binary.

This is useful source evidence, but it does not prove that the complete graphics stack is ABI-compatible with the Android 15 framework or with the exact ugglite board configuration. GPU/display remains a high-risk integration gate.

## 1. Kernel-side evidence

Kernel repository: `Mi-Thorium/kernel_msm-4.19`
Kernel branch: `mithorium/a13/master`
Kernel commit previously pinned in the source lock snapshot: `b22b61aa0b3cce1df017905750e5399890234c10`

Verified files:

- `arch/arm64/configs/vendor/msm8937_defconfig` enables `CONFIG_QCOM_KGSL=y`.
- `arch/arm64/configs/vendor/msm8937-perf_defconfig` also enables `CONFIG_QCOM_KGSL=y`.
- `drivers/gpu/msm/Kconfig` defines the Qualcomm KGSL driver and selects the Adreno devfreq governors.
- `drivers/gpu/msm/Makefile` builds `msm_kgsl_core` and `msm_adreno` when `CONFIG_QCOM_KGSL` is enabled.
- `arch/arm64/boot/dts/vendor/qcom/msm8937-gpu.dtsi` declares `qcom,kgsl-3d0` / `qcom,kgsl-3d`, the GPU register region, interrupt, clocks, bus scaling, IOMMU and power levels.
- The DTS GPU power table contains a highest listed frequency of 450 MHz.

The device-specific kernel config adds Xiaomi MSM8937 board support and the ugglite machine option. More importantly, the actual ugglite board DTS is `ugglite.dts`, which includes `qcom/msm8917.dtsi`; that SoC DTSI includes `msm8917-gpu.dtsi`. Thus the MSM8917 GPU node is in the include chain for the ugglite board DTS. The final compiled DTB/DTBO selected by the ROM build still needs confirmation.

## 2. Proprietary graphics userspace

Graphics repository: `Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-graphics`
Branch: `a15_qpr2/master`
Pinned repository commit: `84fc1d44483139d6355347a4bc98b172bac6f69b`

Selected package family:

`LA.UM.9.6.3.r1-06200-89xx.0`

Its generated `Android.bp` declares 32-bit and 64-bit prebuilt variants for:

- `eglSubDriverAndroid`
- `libEGL_adreno`
- `libGLESv1_CM_adreno`
- `libGLESv2_adreno`
- `libq3dtools_adreno`
- `libadreno_utils`
- `libC2D2`
- `libc2d30-a3xx`
- `libc2d30_bltlib`
- `libgsl`
- `libllvm-glnext`
- `libllvm-qcom`
- `vulkan.adreno`

The same package family also contains 64-bit display color/post-processing libraries and a display color service. This is evidence of a fairly complete legacy Qualcomm graphics userspace payload, but it does not identify the precise GPU revision or prove all blobs are suitable for Adreno 308.

Important build-system caveat: the generated prebuilt modules set `check_elf_files: false`. That suppresses Soong's normal ELF dependency checking for these prebuilt libraries; it is not evidence that their dependencies or ABI are correct.

## 3. Display / gralloc / composer configuration

The Android 15 common BoardConfig sets:

- `TARGET_USES_GRALLOC1 := true`
- `TARGET_USES_HWC2 := true`
- `TARGET_USES_ION := true`
- Unless the alternate Q Display Stack is selected, `TARGET_USES_GRALLOC4`, QTI mapper 2.0 and mapper extensions 1.1 are enabled.

The common product makefile for the non-Q-Display path includes QTI display allocator, mapper 2.0/3.0/4.0, mapper extensions, QTI gralloc, composer 2.1 service, platform HWC, memtrack, display config libraries, and 32-/64-bit Adreno symlink packages.

The device manifest also has a separate optional `q-display-stack.xml` declaring allocator 2.0 and mapper 2.1. Do not enable that alternate stack without checking the matching product variables and manifest combination; mixing the two display paths can create duplicate or inconsistent HAL declarations.

## 4. Compatibility risks

1. **Legacy userspace on Android 15:** the graphics blobs are proprietary and from a Qualcomm 89xx software release family. Their linker namespaces, dependencies, binder/HIDL assumptions, and memory allocator behavior need runtime validation against the selected Android 15 framework.
2. **KGSL ABI pairing:** kernel KGSL and userspace `libgsl` / Adreno libraries must agree on ioctl, memory, sync and IOMMU behavior. A successful kernel compile does not validate this pairing.
3. **Gralloc/mapper/HWC combination:** the product mixes legacy gralloc1/HWC2 board flags with a QTI mapper 2/3/4 compatibility package set. Confirm the actual installed service binaries, manifest declarations, init rc files and symlinks in the final target-files package.
4. **32-bit compatibility:** the generated package includes both ARM and ARM64 EGL/GLES variants. Confirm that the device product's 32-bit linker configuration and all symlink modules are actually included.
5. **Vulkan declaration:** the common tree copies Vulkan feature XML declarations and the graphics package declares `vulkan.adreno`. Neither is sufficient proof that Adreno 308 exposes a usable Vulkan implementation. Do not advertise Vulkan until runtime enumeration and CTS/VTS or equivalent tests pass.
6. **Thermal and frequency behavior:** the DTS power levels and KGSL governor must be checked against the exact board, thermal policy and battery behavior.
7. **Memory pressure:** ugglite has only 2 GB RAM. GPU buffers, gralloc allocations, SurfaceFlinger composition and camera preview may compete heavily with Android 15 memory use.

## 5. Required validation before build/flash progression

- Confirm the compiled ugglite DTB/DTBO retains the MSM8917 GPU node and the correct clocks, regulator, bus and IOMMU links for this board.
- Confirm the kernel config used by the actual product has `CONFIG_QCOM_KGSL=y` after all config fragments are merged.
- Record hashes and ELF metadata for all selected Adreno/graphics blobs from the exact extraction source.
- Inspect every shared-library dependency and 32-/64-bit variant; resolve missing libraries rather than relying on `check_elf_files: false`.
- Verify final product inclusion and init/manifest wiring for gralloc, mapper, composer, memtrack, EGL/GLES and Vulkan.
- On real hardware, inspect KGSL probe, `/dev/kgsl-3d0`, EGL initialization, GLES renderer string, SurfaceFlinger composition, video playback, camera preview, suspend/resume, thermal throttling and memory pressure.
- Run applicable graphics CTS/VTS tests before claiming hardware acceleration is stable.

## Status

- Kernel KGSL source/config: **present in source**.
- MSM8937 GPU DTSI node: **present in source**.
- Proprietary Adreno EGL/GLES payload: **present in source manifest/build declarations**.
- Gralloc/HWC/mapper product wiring: **declared; final installed image not verified**.
- Adreno 308 runtime acceleration on ugglite: **not tested**.
- Vulkan on ugglite: **not verified; do not claim support**.
- Flashable One UI 7 image: **does not exist yet**.

No flashing, repartitioning, firmware writing, or device-side operations were performed during this audit. The physical handset is unavailable for runtime testing.


## Correction / board-specific Device Tree confirmation (2026-11-19)

The first pass inspected `msm8937-gpu.dtsi`, but that is not the correct GPU include for the ugglite board. The board DTS in the pinned Xiaomi MSM8937 DTS repository is `ugglite.dts`, which includes `qcom/msm8917.dtsi`; the latter explicitly includes `msm8917-gpu.dtsi`. The ugglite DTS also identifies the board with `xiaomi,ugglite` and a Qualcomm MSM8917 MTP compatible string. The audit therefore corrects the GPU include path to MSM8917. The final compiled DTB/DTBO still must be checked from the build output before flashing.

Relevant source refs:
- Device tree repo commit: `eca0b0dadbac0713824c3b42a1238c4e983982ae`
- `ugglite.dts` blob: `fabcb53a14df7ae50ecf088a4e203b076756f04e`
- `msm8917.dtsi` blob: `037033b80009a3114426670c11d0ae2378e3df95`
- `msm8917-gpu.dtsi` blob: `aa7d410429abf4306624cb916c9b6f02d9a555d7`


## 6. HIDL manifest cross-check

The Android 15 common device `manifest.xml` declares:

- `android.hardware.graphics.composer@2.1::IComposer/default`
- `android.hardware.memtrack@1.0::IMemtrack/default`
- `vendor.display.color@1.0::IDisplayColor/default`
- `vendor.display.config@2.0::IDisplayConfig/default`
- `vendor.display.postproc@1.0::IDisplayPostproc/default`

The same base manifest does not declare graphics allocator or mapper. A separate optional `configs/manifest/q-display-stack.xml` declares allocator 2.0 and mapper 2.1 passthrough. This is a distinct configuration path and must not be combined casually with the default QTI mapper 2.0/3.0/4.0 product package path. The final product variables and generated manifest must be checked together to ensure only the intended HAL combination is installed and declared.

The proprietary graphics package supplies `vendor.display.color@1.0-service` and an init rc that starts it as a HAL service. The presence of the init rc and manifest declaration still does not prove the service can load all dependencies or communicate with the display stack on the target device.

## 7. Board-specific GPU Device Tree correction

The correct ugglite board chain is:

`ugglite.dts` → `qcom/msm8917.dtsi` → `msm8917-gpu.dtsi`.

The ugglite board DTS has compatible strings `qcom,msm8917-mtp`, `qcom,msm8917`, `qcom,mtp`, and `xiaomi,ugglite`, and board ID `<8 0>`. The parent MSM8917 DTSI overrides the base GPU power table with speed-bin-specific tables, so the final maximum clock must be taken from the effective compiled DTB for the actual board, not copied from the unrelated MSM8937 GPU DTSI or from the generic MSM8917 base table.
