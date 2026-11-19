#!/usr/bin/env bash
set -u

sources=(
  "https://github.com/ancient-devices/device_xiaomi_ulysse.git"
  "https://github.com/xiaomi-ulysse/android_kernel_xiaomi_msm8937.git"
  "https://github.com/xiaomi-ulysse/twrp_device_xiaomi_ugglite.git"
)

for url in "${sources[@]}"; do
  printf '\n===== %s =====\n' "$url"
  if ! git ls-remote --heads "$url"; then
    printf 'Unable to inspect remote; verify URL and access.\n' >&2
  fi
done
