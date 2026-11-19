#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANDROID_ROOT="${ANDROID_ROOT:-/srv/android15/OneUI7-Ugglite/android}"
KERNEL_ROOT="${ANDROID_ROOT}/kernel/xiaomi/mithorium-4.19"
# IMPORTANT: Repo does not support initializing a second client inside an
# existing Android Repo checkout. Sync the kernel as a sibling client, then
# move the complete checkout into TARGET_KERNEL_SOURCE.
KERNEL_SYNC_ROOT="${ANDROID_ROOT%/}/../kernel-sync/mithorium-4.19"
JOBS="${JOBS:-8}"
MIN_FREE_GB="${MIN_FREE_GB:-400}"
MIN_RAM_GB="${MIN_RAM_GB:-64}"
LOG_DIR="${PROJECT_ROOT}/build-logs"
mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG_DIR/build-$(date -u +%Y%m%dT%H%M%SZ).log") 2>&1

fail() { echo "ERROR: $*" >&2; exit 1; }

echo "=== OneUI7-Ugglite Android 15 baseline build ==="
echo "Android source: $ANDROID_ROOT"
echo "Kernel source:  $KERNEL_ROOT"
echo "Kernel sync:    $KERNEL_SYNC_ROOT"

[[ "$(uname -m)" == "x86_64" ]] || fail "Build host must be x86_64."
[[ -f /etc/os-release ]] || fail "Cannot identify Linux distribution."
. /etc/os-release
[[ "$ID" == "ubuntu" ]] || fail "Use Ubuntu 22.04/24.04 x86_64 build host; found $ID."
[[ "$EUID" -ne 0 ]] || fail "Do not run the build as root."

RAM_GB="$(awk '/MemTotal/ {printf "%d", $2/1024/1024}' /proc/meminfo)"
mkdir -p "$ANDROID_ROOT"
FREE_GB="$(df -BG "$ANDROID_ROOT" | awk 'NR==2 {gsub(/G/,"",$4); print $4}')"
echo "RAM: ${RAM_GB} GiB; free disk: ${FREE_GB} GiB; CPU threads: $(nproc)"
(( RAM_GB >= MIN_RAM_GB )) || fail "Need at least ${MIN_RAM_GB} GiB RAM for a practical full Android build."
(( FREE_GB >= MIN_FREE_GB )) || fail "Need at least ${MIN_FREE_GB} GiB free on the Android source filesystem."

command -v git >/dev/null || fail "git is missing."
command -v curl >/dev/null || fail "curl is missing."
command -v repo >/dev/null || fail "repo launcher is missing; install the Android repo tool first."
command -v git-lfs >/dev/null || fail "git-lfs is missing."

cd "$ANDROID_ROOT"
repo init -u https://github.com/LineageOS/android.git -b lineage-22.2 --git-lfs --no-clone-bundle

mkdir -p .repo/local_manifests
install -m 0644 "$PROJECT_ROOT/manifests/mi-thorium-lineage-22.2.xml" .repo/local_manifests/mi-thorium.xml

echo "=== Syncing LineageOS 22.2 + Mi-Thorium device/vendor/HAL sources ==="
repo sync -c --no-clone-bundle -j"$JOBS"

echo "=== Applying the known Mi-Thorium audio HAL Clang compatibility patch ==="
AUDIO_HAL_ROOT="$ANDROID_ROOT/hardware/mithorium/audio/LA.UM.9.6.4.r2-04300-89xx.QSSI13r2.0/hal"
AUDIO_PATCH="$PROJECT_ROOT/patches/0001-audio-extn-name-unused-pthread-parameters.patch"
[[ -d "$AUDIO_HAL_ROOT/.git" || -f "$AUDIO_HAL_ROOT/.git" ]] || fail "Mi-Thorium audio HAL Repo checkout missing: $AUDIO_HAL_ROOT"
[[ -f "$AUDIO_HAL_ROOT/hal/audio_extn/cirrus_playback.c" ]] || fail "Audio HAL Cirrus source missing."
if git -C "$AUDIO_HAL_ROOT" apply --reverse --check "$AUDIO_PATCH" >/dev/null 2>&1; then
    echo "Audio HAL compatibility patch is already applied."
else
    git -C "$AUDIO_HAL_ROOT" apply --check "$AUDIO_PATCH" || fail "Audio HAL compatibility patch does not apply cleanly; inspect upstream changes."
    git -C "$AUDIO_HAL_ROOT" apply "$AUDIO_PATCH"
    echo "Audio HAL compatibility patch applied."
fi
grep -q 'audio_extn_cirrus_calibration_thread(void *arg __unused)' "$AUDIO_HAL_ROOT/hal/audio_extn/cirrus_playback.c" || fail "Audio HAL calibration-thread fix not present."
grep -q 'spkr_calibration_thread(void *arg __unused)' "$AUDIO_HAL_ROOT/hal/audio_extn/spkr_protection.c" || fail "Audio HAL speaker-thread fix not present."

apply_local_patch() {
    local repo_root="$1"
    local patch_file="$2"
    local label="$3"
    [[ -d "$repo_root/.git" || -f "$repo_root/.git" ]] || fail "$label repository checkout missing: $repo_root"
    [[ -f "$patch_file" ]] || fail "$label patch missing: $patch_file"
    if git -C "$repo_root" apply --reverse --check "$patch_file" >/dev/null 2>&1; then
        echo "$label patch is already applied."
    else
        git -C "$repo_root" apply --check "$patch_file" || fail "$label patch does not apply cleanly; inspect upstream changes."
        git -C "$repo_root" apply "$patch_file"
        echo "$label patch applied."
    fi
}

apply_local_patch "$ANDROID_ROOT/device/xiaomi/Mi8937" "$PROJECT_ROOT/patches/0002-fix-mi8937-product-build-prop-override.patch" "Mi8937 product build-property"
apply_local_patch "$ANDROID_ROOT/device/xiaomi/mithorium-common" "$PROJECT_ROOT/patches/0003-fix-mithorium-msm8937-media-copy-entry.patch" "MiThorium MSM8937 media copy"

repo manifest -r -o "$ANDROID_ROOT/pinned-android-manifest.xml"

echo "=== Preparing separate kernel Repo client OUTSIDE Android source tree ==="
mkdir -p "$(dirname "$KERNEL_SYNC_ROOT")"
if [[ -d "$KERNEL_ROOT/.repo" && ! -e "$KERNEL_SYNC_ROOT" ]]; then
    echo "Moving any previous kernel Repo client out of the Android source tree."
    mkdir -p "$(dirname "$KERNEL_ROOT")"
    mv "$KERNEL_ROOT" "$KERNEL_SYNC_ROOT"
fi
[[ ! -e "$KERNEL_ROOT" ]] || fail "Kernel destination already exists without a movable Repo client: $KERNEL_ROOT"
mkdir -p "$KERNEL_SYNC_ROOT"
cd "$KERNEL_SYNC_ROOT"
repo init -u https://github.com/Mi-Thorium/kernel_manifest -b mithorium-4.19 --no-clone-bundle
repo sync -c --no-clone-bundle -j4
repo manifest -r -o "$ANDROID_ROOT/pinned-kernel-manifest.xml"

echo "=== Installing synced kernel tree at TARGET_KERNEL_SOURCE ==="
mkdir -p "$(dirname "$KERNEL_ROOT")"
mv "$KERNEL_SYNC_ROOT" "$KERNEL_ROOT"

KERNEL_SOURCE="$KERNEL_ROOT/kernel"
[[ -f "$KERNEL_SOURCE/Makefile" ]] || fail "Kernel Makefile missing at expected TARGET_KERNEL_SOURCE: $KERNEL_SOURCE"
grep -q '^VERSION = 4$' "$KERNEL_SOURCE/Makefile" || fail "Unexpected kernel major version."
grep -q '^PATCHLEVEL = 19$' "$KERNEL_SOURCE/Makefile" || fail "Unexpected kernel minor version."
grep -q '^SUBLEVEL = 325$' "$KERNEL_SOURCE/Makefile" || fail "Expected kernel 4.19.325 source not found."
CONFIG_ROOT="$KERNEL_SOURCE/arch/arm64/configs"
for config in \
    vendor/msm8937-perf_defconfig \
    vendor/common.config \
    vendor/debugfs.config \
    vendor/msm8937-legacy.config \
    vendor/feature/android-12.config \
    vendor/feature/compat-vdso.config \
    vendor/feature/erofs.config \
    vendor/feature/exfat.config \
    vendor/feature/kprobes.config \
    vendor/feature/lmkd.config \
    vendor/feature/wireguard.config \
    vendor/feature/ntfs.config \
    vendor/feature/no-camera-stack.config \
    vendor/feature/no-wlan-driver.config \
    vendor/xiaomi/msm8937/common.config \
    vendor/xiaomi/msm8937/mi8937.config; do
    [[ -f "$CONFIG_ROOT/$config" ]] || fail "Required kernel config fragment missing: $config"
done
[[ -f "$KERNEL_SOURCE/arch/arm64/boot/dts/xiaomi-msm8937/ugglite.dts" ]] || fail "ugglite DTS missing after kernel manifest sync."
[[ -f "$KERNEL_SOURCE/arch/arm64/boot/dts/xiaomi-msm8937/ulysse/ugglite/ugglite.dtsi" ]] || fail "ugglite device DTS include missing."
[[ -f "$KERNEL_SOURCE/arch/arm64/boot/dts/vendor-legacy/qcom/msm8917.dtsi" ]] || fail "MSM8917 vendor DTS include missing."

cd "$ANDROID_ROOT"
[[ -f device/xiaomi/Mi8937/lineage_Mi8937_4_19.mk ]] || fail "Mi8937 4.19 product makefile missing."
[[ -f vendor/xiaomi/Mi8937/Mi8937-vendor.mk ]] || fail "Mi8937 proprietary vendor makefile missing."
[[ -f vendor/xiaomi/mithorium-common-4.19/BoardConfigVendor.mk ]] || fail "MiThorium 4.19 common vendor makefile missing."
grep -q 'xiaomi_ugglite_overlay' device/xiaomi/Mi8937/device.mk || fail "ugglite overlay package not found."
grep -q 'ugglite' device/xiaomi/Mi8937/BoardConfig.mk || fail "ugglite OTA assert not found."

echo "=== Source lockfiles generated ==="
ls -lh "$ANDROID_ROOT/pinned-android-manifest.xml" "$ANDROID_ROOT/pinned-kernel-manifest.xml"

echo "=== Starting Android 15 baseline build ==="
mkdir -p "$PROJECT_ROOT/build-output"
rm -f "$PROJECT_ROOT/build-output"/*.zip
source build/envsetup.sh
lunch lineage_Mi8937_4_19-userdebug
mka bacon -j"$JOBS"

OUT_DIR="$ANDROID_ROOT/out/target/product/Mi8937_4_19"
[[ -d "$OUT_DIR" ]] || fail "Product output directory does not exist: $OUT_DIR"
mkdir -p "$PROJECT_ROOT/build-output"
find "$OUT_DIR" -maxdepth 1 -type f \( -name '*.zip' -o -name '*.img' -o -name '*.tar' \) -exec cp -v {} "$PROJECT_ROOT/build-output/" \;
compgen -G "$PROJECT_ROOT/build-output/*.zip" >/dev/null || fail "Build ended without producing a flashable ZIP."
cp -f "$ANDROID_ROOT/pinned-android-manifest.xml" "$PROJECT_ROOT/build-output/"
cp -f "$ANDROID_ROOT/pinned-kernel-manifest.xml" "$PROJECT_ROOT/build-output/"
find "$PROJECT_ROOT/build-output" -maxdepth 1 -type f -printf '%f %s bytes\n'
echo "BUILD_COMPLETE"
