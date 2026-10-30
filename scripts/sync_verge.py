"""Safely sync a published script to an explicitly selected local Verge script file."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.model import check_url
from scripts.validate import apply_script


def install_script(target, content, expected):
    target = Path(target)
    if target.is_symlink() or not target.is_file() or target.suffix.lower() != ".js":
        raise ValueError("--target 必须是已存在的本地 .js 普通文件；请从客户端打开全局扩展脚本定位")
    if not re.fullmatch(r"[0-9a-f]{64}", expected) or hashlib.sha256(content).hexdigest() != expected:
        raise ValueError("脚本与 manifest 的 SHA-256 不一致；保留原文件")
    if target.read_bytes() == content:
        return False
    with tempfile.NamedTemporaryFile(suffix=".js", dir=target.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
    try:
        subprocess.run(["node", "--check", str(temporary)], check=True, capture_output=True, timeout=10)
        result = apply_script(temporary, {"proxies": [{"name": "HK sync-test"}]})
        if "dns" in result or "ipv6" in result or not result.get("rules") or not result.get("proxy-groups"):
            raise ValueError("下载的脚本未通过基本配置检查")
        shutil.copy2(target, target.with_suffix(".js.bak"))
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return True


def download(url, limit):
    with urllib.request.urlopen(url, timeout=30) as response:
        check_url(response.url)
        content = response.read(limit + 1)
    if len(content) > limit:
        raise ValueError("远程文件超过大小限制")
    return content


def sync(base_url, target):
    base_url = check_url(base_url)
    manifest = json.loads(download(base_url + "/manifest.json", 1024 * 1024))
    path = "clash-verge/routing.js"
    content = download(base_url + "/" + path, 2 * 1024 * 1024)
    changed = install_script(target, content, manifest["files"][path])
    return manifest["build"], changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--target", type=Path, required=True)
    args = parser.parse_args()
    version, changed = sync(args.base_url, args.target)
    print(f"Build {version}: " + ("脚本已更新并备份；请在 Clash Verge Rev 重新应用当前配置。" if changed else "本地脚本已是此版本。"))

