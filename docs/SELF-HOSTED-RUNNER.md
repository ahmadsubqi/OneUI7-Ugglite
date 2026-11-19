# GitHub Actions Android Build Runner Setup

## Why a separate runner is required

The Android 15 full source checkout and build is too large for the standard GitHub-hosted runner. Current standard public Linux runners provide 16 GB RAM and 14 GB SSD. The AOSP build guide recommends at least 64 GB RAM and 400 GB free disk.

Use a dedicated Ubuntu x86_64 machine with:

- 64 GB RAM minimum (96 GB preferred)
- 600 GB SSD free space recommended
- 8 or more CPU cores
- Ubuntu 22.04 or 24.04
- Stable broadband and enough bandwidth for a multi-repository Android source sync

Do not use the Redmi Note 5A Lite itself as the build host.

## Install build dependencies

On the Ubuntu build host:

```bash
sudo apt-get update
sudo apt-get install -y bc bison build-essential ccache curl erofs-utils flex \
  g++-multilib gcc-multilib git git-lfs gnupg gperf imagemagick kmod \
  protobuf-compiler python3-protobuf lib32readline-dev lib32z1-dev \
  libdw-dev libelf-dev libgnutls28-dev lz4 libsdl1.2-dev libssl-dev \
  libxml2 libxml2-utils lzop pngcrush rsync schedtool squashfs-tools \
  xsltproc xxd zip zlib1g-dev
```

Install the Repo launcher:

```bash
mkdir -p "$HOME/bin"
curl -o "$HOME/bin/repo" https://storage.googleapis.com/git-repo-downloads/repo
chmod a+rx "$HOME/bin/repo"
echo 'export PATH="$HOME/bin:$PATH"' >> "$HOME/.profile"
source "$HOME/.profile"
repo version
git lfs install
```

## Register the runner

1. Open the repository: https://github.com/ahmadsubqi/OneUI7-Ugglite
2. Open **Settings → Actions → Runners**.
3. Choose **New self-hosted runner**.
4. Select **Linux** and **x64**.
5. Follow GitHub's displayed download and configuration commands on the build host.
6. During runner configuration, add the custom label: `android-build`.
7. Start the runner or install it as a service.

Do not paste the one-time runner registration token into this repository, source files, workflow logs, or this chat. Obtain it directly from the repository Settings page when configuring the runner.

## Start the build

Once the runner is online and shows the `android-build` label:

1. Open the repository's **Actions** tab.
2. Select **Android 15 Baseline Build**.
3. Select **Run workflow**.
4. Keep the default parallel job count at 8 initially.
5. Open the run and monitor the sync/build logs.

The workflow uses a persistent source directory under the runner workspace so a later run can reuse the synced source tree. The first source sync and full build may take many hours.

The kernel manifest is synchronized in a separate sibling directory, outside the Android source Repo checkout, and then moved into `kernel/xiaomi/mithorium-4.19`. Do not initialize the kernel Repo client from inside the Android source root: that would conflict with the Android Repo metadata.

## Expected artifacts

A successful run uploads:

- LineageOS baseline ZIP (if produced by the selected target)
- Other generated images found in the product output directory
- `pinned-android-manifest.xml`
- `pinned-kernel-manifest.xml`

The pinned manifests record the exact project revisions used for that run.

## Safety

The workflow only syncs and builds source. It does not connect to the phone, flash partitions, unlock/relock the bootloader, or repartition storage. Do not upload proprietary firmware, signing keys, passwords, runner tokens, IMEI, or serial-number logs to the repository.
