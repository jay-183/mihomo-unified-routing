"""Download the pinned official Mihomo binary and verify its release digest."""
import argparse
import gzip
import hashlib
import io
import os
from pathlib import Path
import platform
import urllib.request
import zipfile

VERSION = "v1.19.33"
ASSETS = {
    "Windows": (f"mihomo-windows-amd64-compatible-{VERSION}.zip",
                "7aaf636a4f2172dcd8ec34ac4f52797b059195e5afd6409508c963e545f8864d"),
    "Linux": (f"mihomo-linux-amd64-compatible-{VERSION}.gz",
              "386508bfb1c72c43b6a0eda73708ecdce82546581b0ebcb16366c53757c622b6"),
}


def download(destination):
    system = platform.system()
    if system not in ASSETS or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise ValueError("自动下载仅支持 Windows/Linux x64；其他平台请用 --core 指定官方内核")
    asset, expected = ASSETS[system]
    url = f"https://github.com/MetaCubeX/mihomo/releases/download/{VERSION}/{asset}"
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read(64 * 1024 * 1024 + 1)
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("Mihomo 下载文件 SHA-256 不匹配，拒绝使用")
    if system == "Windows":
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            binary = archive.read("mihomo-windows-amd64-compatible.exe")
    else:
        binary = gzip.decompress(data)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".download")
    temporary.write_bytes(binary)
    temporary.chmod(0o755)
    os.replace(temporary, destination)
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".cache/mihomo.exe" if platform.system() == "Windows" else ".cache/mihomo"))
    print(download(parser.parse_args().output))
