#!/usr/bin/env python3
"""Validate the ugglite kernel artifacts before publishing or integrating them."""
from pathlib import Path
import gzip
import struct
import sys
import zlib

root = Path(sys.argv[1] if len(sys.argv) > 1 else "kernel-artifacts")
image = root / "Image.gz-dtb"
dtb = root / "ugglite.dtb"
config = root / "kernel.config"

def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")

for path in (image, dtb, config):
    require(path.is_file() and path.stat().st_size > 0, f"{path.name} exists and is non-empty")

image_bytes = image.read_bytes()
require(image_bytes[:2] == b"\x1f\x8b", "Image.gz-dtb begins with a gzip stream")
decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
try:
    kernel_payload = decoder.decompress(image_bytes)
    kernel_payload += decoder.flush()
except zlib.error as exc:
    raise SystemExit(f"FAIL: kernel gzip stream is corrupt: {exc}")
require(decoder.eof, "kernel gzip stream reaches a valid end")
appended_dtb = decoder.unused_data
require(len(kernel_payload) > 1024 * 1024, "decompressed kernel payload is plausibly sized")
require(appended_dtb[:4] == b"\xd0\x0d\xfe\xed", "Image.gz-dtb contains an appended flattened device tree")

dtb_bytes = dtb.read_bytes()
require(dtb_bytes[:4] == b"\xd0\x0d\xfe\xed", "standalone DTB has the FDT magic")
totalsize = struct.unpack(">I", dtb_bytes[4:8])[0]
require(40 <= totalsize <= len(dtb_bytes), "standalone DTB header reports a valid total size")
require(b"xiaomi,ugglite" in dtb_bytes, "standalone DTB contains the xiaomi,ugglite compatible string")
require(b"xiaomi,ugglite" in appended_dtb, "appended DTB in Image.gz-dtb targets xiaomi,ugglite")

config_text = config.read_text(encoding="utf-8", errors="replace")
required = [
    "CONFIG_ARCH_MSM8937=y",
    "CONFIG_MACH_XIAOMI_MSM8937=y",
    "CONFIG_MACH_XIAOMI_UGGLITE=y",
    "CONFIG_PRONTO_WLAN=y",
    "CONFIG_WCNSS_CORE=y",
    "CONFIG_WCNSS_CORE_PRONTO=y",
    "CONFIG_CFG80211=y",
    "CONFIG_SND=y",
    "CONFIG_SND_SOC=y",
    "CONFIG_MSMB_CAMERA=y",
    "CONFIG_MSMB_CAMERA_LEGACY=y",
    "CONFIG_MSMB_CAMERA_LEGACY_M=y",
    "CONFIG_MSMB_JPEG=y",
    "CONFIG_MSM_FD=y",
]
for symbol in required:
    require(symbol in config_text, f"kernel config enables {symbol}")

print("PASS: kernel image, embedded DTB, standalone ugglite DTB, and required config are consistent.")
