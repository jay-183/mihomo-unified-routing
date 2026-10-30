"""Build into a staging directory. A failed build never replaces dist."""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import urllib.request

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapters import mihomo, shadowrocket
from scripts.model import ROOT, check_url, load_model


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fetch_provider(item, cache, refresh):
    name, provider = item
    key = digest(provider["url"].encode())
    target = cache / (key + ".yaml")
    if refresh or not target.exists():
        for attempt in range(3):
            try:
                request = urllib.request.Request(provider["url"], headers={"User-Agent": "unified-routing-builder/1"})
                with urllib.request.urlopen(request, timeout=30) as response:
                    check_url(response.url)
                    data = response.read(20 * 1024 * 1024 + 1)
                if len(data) > 20 * 1024 * 1024:
                    raise ValueError(f"规则集 {name} 超过 20 MiB")
                # Reject HTML/error pages and invalid YAML before updating the cache.
                document = yaml.load(data.decode("utf-8-sig"), Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
                if not isinstance(document, dict) or not isinstance(document.get("payload"), list) or not document["payload"]:
                    raise ValueError(f"规则集 {name} 缺少非空 payload")
                cache.mkdir(parents=True, exist_ok=True)
                tmp = target.with_suffix(".tmp")
                tmp.write_bytes(data)
                os.replace(tmp, target)
                break
            except (OSError, ValueError) as error:
                if attempt == 2:
                    raise RuntimeError(f"下载规则集失败：{name} ({type(error).__name__})") from error
                time.sleep(attempt + 1)
    return name, target.read_bytes()


def generate(model, upstream, base_url, output):
    source_bytes = json.dumps(model, sort_keys=True, ensure_ascii=False).encode()
    source_hash = digest(source_bytes)
    upstream_hashes = {name: digest(data) for name, data in sorted(upstream.items())}
    generator_files = sorted((ROOT / "adapters").glob("*.*")) + [ROOT / "scripts" / n for n in ("build.py", "model.py", "validate.py")]
    generator_hash = digest(b"".join(p.name.encode() + p.read_bytes() for p in generator_files if p.suffix in {".py", ".js"}))
    version = digest(source_bytes + generator_hash.encode() + json.dumps(upstream_hashes, sort_keys=True).encode())[:16]
    converted, unsupported = {}, {}
    for name, provider in model["rule-providers"].items():
        document = yaml.load(upstream[name].decode("utf-8-sig"), Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
        converted[name], skipped = shadowrocket.convert_payload(name, provider, document["payload"])
        if skipped:
            unsupported[name] = skipped
    rules_id = digest(json.dumps([converted, {n: p['url'] for n, p in model['rule-providers'].items()}], ensure_ascii=False, sort_keys=True).encode())[:16]
    rules_path = "rules/" + rules_id
    rules_url = base_url + "/" + rules_path
    empty = {name for name, entries in converted.items() if not entries}
    output.mkdir(parents=True, exist_ok=True)

    def write(path, content):
        dest = output / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            dest.write_bytes(content)
        else:
            dest.write_text(content, encoding="utf-8", newline="\n")

    script = mihomo.render(model, version)
    for client in ("clash-verge", "flclash"):
        write(client + "/routing.js", script)
    write("shadowrocket/config.conf", shadowrocket.render(model, version, base_url, rules_url, empty))
    for name in upstream:
        write("upstream/" + name + ".yaml", upstream[name])
        body = f"# {name}; source: {model['rule-providers'][name]['url']}\n"
        body += "# Policy-free Shadowrocket rules; see THIRD_PARTY.md and compatibility.json.\n"
        if name in unsupported:
            body += f"# Unsupported iOS process rules: {len(unsupported[name])}; details in compatibility.json\n"
        write(f"{rules_path}/{name}.list", body + "\n".join(converted[name]) + "\n")
    report = {
        "build": version, "ios_runtime_tested": False,
        "shadowrocket_unsupported_public_rules": unsupported,
        "shadowrocket_empty_providers": sorted(empty),
        "shadowrocket_domain_regex_approximations": shadowrocket.DOMAIN_REGEX_APPROXIMATIONS,
        "differences": [
            "Shadowrocket 无可公开运行的内核校验器；仅做静态检查和规则转换对照。",
            "Shadowrocket 不支持进程匹配；公共源中的进程规则显式记录，后续域名/IP规则继续匹配。",
            "OpenAI 公共源的一个 DOMAIN-REGEX 改为 DOMAIN-WILDCARD：覆盖原匹配，但放宽数字段为任意字符；精确条目见 shadowrocket_domain_regex_approximations。",
            "MATCH 转为 FINAL；GEOIP LAN 按 Mihomo isLan 定义展开为 CIDR；IP-CIDR6 转为 IP-CIDR。",
            "Shadowrocket load-balance 保持同域名粘性，但不保证与 Mihomo consistent-hashing 选中同一节点。",
            "Shadowrocket timeout 使用秒；lazy 与 max-failed-times 无已核实的等价参数。",
            "Shadowrocket 编译可能优先处理域名类规则、后置 GEOIP；输出文本维持原顺序，运行顺序需 iOS 验证。",
            "Mihomo 公共源每 86400 秒更新；Shadowrocket 使用本次构建的转换快照，需更新并编译配置。",
            "Windows 原生全局脚本为本地文件；提供校验、备份的外部同步工具，写入后仍需客户端重载。",
            "FlClash v0.9.2 核实源码支持 URL 脚本自动更新：资源自动更新开关 geoAutoUpdate、间隔 geoUpdateInterval（小时），启动及定时检查；旧版本请手动更新脚本。",
            "节点正则忠实保留原式；例如 US 可能匹配含 us 的其他名称，须按机场命名自行调整。",
            "未写入 DNS 或顶层 IPv6；客户端自身仍可按本地设置修改最终运行配置。",
        ],
    }
    write("compatibility.json", json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    write("THIRD_PARTY.md", (ROOT / "THIRD_PARTY.md").read_text(encoding="utf-8"))
    for license_file in (ROOT / "licenses").glob("*.txt"):
        write("licenses/" + license_file.name, license_file.read_bytes())
    files = {str(p.relative_to(output)).replace("\\", "/"): digest(p.read_bytes())
             for p in sorted(output.rglob("*")) if p.is_file()}
    manifest = {"build": version, "source_sha256": source_hash, "generator_sha256": generator_hash, "base_url": base_url,
                "upstream_sha256": upstream_hashes, "rules_path": rules_path,
                "group_count": len(model["proxy-groups"]), "rule_count": len(model["rules"]),
                "user_rule_count": len(model["user-rules"]), "files": files}
    write("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def build(base_url, refresh=False):
    base_url = check_url(base_url)
    model = load_model()
    cache = ROOT / ".cache" / "providers"
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        upstream = dict(pool.map(lambda item: fetch_provider(item, cache, refresh), model["rule-providers"].items()))
    staging_root = ROOT / ".cache"
    staging_root.mkdir(exist_ok=True)
    # Keep rollback data outside TemporaryDirectory even if restoring it fails.
    backup = staging_root / "dist-previous"
    if backup.exists() or backup.is_symlink():
        raise RuntimeError(f"存在未清理的构建备份，请先检查：{backup}")
    with tempfile.TemporaryDirectory(prefix="build-", dir=staging_root) as temporary:
        staged = Path(temporary) / "dist"
        manifest = generate(model, upstream, base_url, staged)
        from scripts.validate import validate_dist
        validate_dist(staged)
        destination = ROOT / "dist"
        if destination.is_symlink():
            raise ValueError("dist 不得是符号链接")
        if destination.exists():
            destination.rename(backup)
        try:
            staged.rename(destination)
        except OSError:
            if backup.exists():
                try:
                    backup.rename(destination)
                except OSError as error:
                    raise RuntimeError(f"产物替换和恢复均失败；原配置完整保存在 {backup}") from error
            raise
        if backup.exists():
            if backup.resolve().parent != staging_root.resolve():
                raise ValueError("构建备份路径越界，拒绝清理")
            shutil.rmtree(backup)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="发布根 URL，默认取 GITHUB_REPOSITORY；本地未指定时使用明确占位 URL")
    parser.add_argument("--refresh", action="store_true", help="刷新全部公共规则；任一失败即中止构建")
    args = parser.parse_args()
    repo = os.environ.get("GITHUB_REPOSITORY", "OWNER/REPO")
    url = args.base_url or f"https://raw.githubusercontent.com/{repo}/release"
    try:
        result = build(url, args.refresh)
    except Exception as error:
        print(f"构建失败，保留上一份 dist：{error}", file=sys.stderr)
        return 1
    print(f"Build {result['build']}: {result['group_count']} groups, {result['rule_count']} rules")
    if "OWNER/REPO" in url:
        print("本地构建使用 OWNER/REPO 占位 URL；发布或在 iOS 导入前必须设置 --base-url。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
