#!/usr/bin/env bash
set -Eeuo pipefail

ANDROID_ROOT="${ANDROID_ROOT:-$(pwd)}"
KERNEL_SOURCE="${KERNEL_SOURCE:-$ANDROID_ROOT/kernel/xiaomi/mithorium-4.19/kernel}"
JOBS="${JOBS:-$(nproc)}"
OUT="${KERNEL_OUT:-$ANDROID_ROOT/out/kernel-ugglite}"
ARTIFACT_DIR="${KERNEL_ARTIFACT_DIR:-$ANDROID_ROOT/build-output/kernel}"

fail() { echo "ERROR: $*" >&2; exit 1; }
pass() { echo "PASS: $*"; }

[[ -d "$KERNEL_SOURCE" && -f "$KERNEL_SOURCE/Makefile" ]] || fail "Kernel source not found: $KERNEL_SOURCE"
[[ "$(uname -m)" == "x86_64" ]] || fail "Kernel build host must be Linux x86_64."
command -v make >/dev/null || fail "make is missing."
command -v python3 >/dev/null || fail "python3 is missing."

grep -q '^VERSION = 4$' "$KERNEL_SOURCE/Makefile" || fail "Kernel major version is not 4."
grep -q '^PATCHLEVEL = 19$' "$KERNEL_SOURCE/Makefile" || fail "Kernel minor version is not 19."
grep -q '^SUBLEVEL = 325$' "$KERNEL_SOURCE/Makefile" || fail "Expected kernel 4.19.325."

if [[ -z "${CLANG_BIN:-}" ]]; then
  if [[ -d "$ANDROID_ROOT/prebuilts/clang/host/linux-x86" ]]; then
    CLANG_BIN="$(find "$ANDROID_ROOT/prebuilts/clang/host/linux-x86" -name clang -executable 2>/dev/null | sort -V | tail -n 1)"
  else
    CLANG_BIN="$(command -v clang || true)"
  fi
fi
[[ -n "$CLANG_BIN" && -x "$CLANG_BIN" ]] || fail "Clang not found. Set CLANG_BIN or install clang on PATH."
export PATH="$(dirname "$CLANG_BIN"):$PATH"
command -v clang >/dev/null || fail "clang is not executable after PATH setup."
command -v ld.lld >/dev/null || fail "ld.lld is missing from the selected Clang toolchain."

CONFIG_ROOT="$KERNEL_SOURCE/arch/arm64/configs"
FRAGMENTS=(
  vendor/common.config
  vendor/feature/android-12.config
  vendor/feature/compat-vdso.config
  vendor/feature/erofs.config
  vendor/feature/exfat.config
  vendor/feature/kprobes.config
  vendor/feature/lmkd.config
  vendor/feature/wireguard.config
  vendor/msm8937-legacy.config
  vendor/xiaomi/msm8937/common.config
  vendor/xiaomi/msm8937/mi8937.config
)
for fragment in "${FRAGMENTS[@]}"; do
  [[ -f "$CONFIG_ROOT/$fragment" ]] || fail "Missing required kernel config fragment: $fragment"
done
[[ -x "$KERNEL_SOURCE/scripts/kconfig/merge_config.sh" ]] || fail "Kernel merge_config.sh is missing."
[[ -f "$KERNEL_SOURCE/techpack/audio-legacy/config/sdm450auto.conf" ]] || fail "MSM8937 audio auto-config is missing."
[[ -f "$KERNEL_SOURCE/techpack/audio-legacy/config/sdm450autoconf.h" ]] || fail "MSM8937 audio auto-config header is missing."
[[ -f "$KERNEL_SOURCE/drivers/staging/prima/Kconfig" ]] || fail "Prima WLAN Kconfig linkfile is missing."
[[ -f "$KERNEL_SOURCE/drivers/staging/prima/Kbuild" ]] || fail "Prima WLAN Kbuild linkfile is missing."
[[ -f "$KERNEL_SOURCE/arch/arm64/boot/dts/xiaomi-msm8937/ugglite.dts" ]] || fail "ugglite DTS linkfile is missing."

mkdir -p "$OUT" "$ARTIFACT_DIR"
echo "=== Configure MSM8937 ugglite kernel ==="
echo "Kernel: $KERNEL_SOURCE"
echo "Clang:  $CLANG_BIN"
echo "Output: $OUT"
make -C "$KERNEL_SOURCE" O="$OUT" ARCH=arm64 LLVM=1 CROSS_COMPILE=aarch64-linux-gnu- vendor/msm8937-perf_defconfig
"$KERNEL_SOURCE/scripts/kconfig/merge_config.sh" -m -O "$OUT" "$OUT/.config" "${FRAGMENTS[@]/#/$CONFIG_ROOT/}"
make -C "$KERNEL_SOURCE" O="$OUT" ARCH=arm64 LLVM=1 CROSS_COMPILE=aarch64-linux-gnu- olddefconfig

require_config() {
  local symbol="$1"
  grep -qx "$symbol=y" "$OUT/.config" || fail "Required kernel option is not enabled after merge: $symbol"
}
require_config CONFIG_ARCH_MSM8937
require_config CONFIG_MACH_XIAOMI_MSM8937
require_config CONFIG_MACH_XIAOMI_UGGLITE
require_config CONFIG_PRONTO_WLAN
require_config CONFIG_WCNSS_CORE
require_config CONFIG_WCNSS_CORE_PRONTO
require_config CONFIG_CFG80211
require_config CONFIG_SND
require_config CONFIG_SND_SOC
grep -q "^CONFIG_SND_SOC_SDM450=y$" "$KERNEL_SOURCE/techpack/audio-legacy/config/sdm450auto.conf" || fail "MSM8937 sdm450 audio auto-config is not enabled."
grep -q "^CONFIG_SND_SOC_EXT_CODEC_SDM450=y$" "$KERNEL_SOURCE/techpack/audio-legacy/config/sdm450auto.conf" || fail "MSM8937 external codec audio config is not enabled."
require_config CONFIG_MSMB_CAMERA
require_config CONFIG_MSMB_CAMERA_LEGACY
require_config CONFIG_MSMB_CAMERA_LEGACY_M
require_config CONFIG_MSMB_JPEG
require_config CONFIG_MSM_FD
pass "audio, WLAN/Pronto, camera, and ugglite device config symbols are enabled."

echo "=== Build kernel Image.gz-dtb and device-tree blobs ==="
make -C "$KERNEL_SOURCE" O="$OUT" ARCH=arm64 LLVM=1 CROSS_COMPILE=aarch64-linux-gnu- -j"$JOBS" Image.gz-dtb dtbs

IMAGE="$OUT/arch/arm64/boot/Image.gz-dtb"
DTB="$OUT/arch/arm64/boot/dts/xiaomi-msm8937/ugglite.dtb"
[[ -s "$IMAGE" ]] || fail "Kernel build did not produce Image.gz-dtb."
[[ -s "$DTB" ]] || fail "Kernel build did not produce ugglite.dtb."
cp -f "$IMAGE" "$ARTIFACT_DIR/Image.gz-dtb"
cp -f "$DTB" "$ARTIFACT_DIR/ugglite.dtb"
cp -f "$OUT/.config" "$ARTIFACT_DIR/kernel.config"
pass "Kernel image and ugglite DTB built and copied to $ARTIFACT_DIR."
