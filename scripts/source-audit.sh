#!/usr/bin/env bash
set -u

sources=(
  "https://github.com/Mi-Thorium/android_device_xiaomi_Mi8937"
  "https://github.com/Mi-Thorium/kernel_msm-4.19"
  "https://github.com/Mi-Thorium/android_device_xiaomi_mithorium-common"
  "https://github.com/Mi-Thorium/proprietary_vendor_xiaomi_Mi8937"
  "https://github.com/Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common"
  "https://github.com/Mi-Thorium/proprietary_vendor_xiaomi_mithorium-common-4.19"
  "https://github.com/Mi-Thorium/local_manifests"
)

for url in "${sources[@]}"; do
  printf '\n===== %s =====\n' "$url"
  if ! git ls-remote --heads "$url"; then
    printf 'Unable to inspect remote; verify URL and access.\n' >&2
  fi
done
