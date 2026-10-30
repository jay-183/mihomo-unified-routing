"""Validate source, generated script execution, file hashes and SR structure."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.model import ROOT, BUILTINS, load_model, split_fields


def apply_script(script, config):
    result = subprocess.run(["node", str(ROOT / "tests/run-script.cjs"), str(script)],
                            input=json.dumps(config, ensure_ascii=False), text=True,
                            encoding="utf-8", capture_output=True, timeout=10)
    if result.returncode:
        raise ValueError(f"脚本执行失败：{result.stderr}")
    return json.loads(result.stdout)


def read_conf(path):
    sections, current = {}, None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            if current in sections:
                raise ValueError(f"重复节：{current}")
            sections[current] = []
        elif current is None:
            raise ValueError(f"节外配置：第 {number} 行")
        else:
            sections[current].append(line)
    return sections


def validate_dist(directory=ROOT / "dist"):
    model = load_model()
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    actual_files = {str(p.relative_to(directory)).replace("\\", "/") for p in directory.rglob("*") if p.is_file()}
    if actual_files != set(manifest["files"]) | {"manifest.json"}:
        raise ValueError("dist 含未登记文件或缺少文件；拒绝发布")
    for name, expected in manifest["files"].items():
        path = (directory / name).resolve()
        if directory.resolve() not in path.parents:
            raise ValueError("manifest 路径越界")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"生成文件哈希不一致：{name}")
    outputs = []
    fixture = {"proxies": [{"name": "香港-test", "type": "ss", "server": "127.0.0.1",
                            "port": 9, "cipher": "aes-128-gcm", "password": "test"}],
               "dns": {"enable": True, "nameserver": ["local-default-marker"]}, "ipv6": True}
    for client in ("clash-verge", "flclash"):
        script = directory / client / "routing.js"
        subprocess.run(["node", "--check", str(script)], check=True, capture_output=True, timeout=10)
        output = apply_script(script, fixture)
        for key in ("proxy-groups", "rule-providers", "rules"):
            if output[key] != model[key]:
                raise ValueError(f"生成脚本与统一源不同：{client} / {key}")
        if output["dns"] != fixture["dns"] or output["ipv6"] != fixture["ipv6"]:
            raise ValueError("脚本改变了本地 DNS/IPv6")
        clean = apply_script(script, {"proxies": fixture["proxies"]})
        if "dns" in clean or "ipv6" in clean:
            raise ValueError("脚本注入了 DNS/IPv6")
        outputs.append(output)
    if outputs[0] != outputs[1]:
        raise ValueError("两客户端的 Mihomo 分流结果不一致")
    sections = read_conf(directory / "shadowrocket/config.conf")
    if set(sections) != {"General", "Proxy Group", "Rule"}:
        raise ValueError("Shadowrocket 节不合法")
    if sections["General"] != [f"update-url = {manifest['base_url']}/shadowrocket/config.conf"]:
        raise ValueError("Shadowrocket General 含额外覆写")
    names = {g["name"] for g in model["proxy-groups"]}
    seen = set()
    for line in sections["Proxy Group"]:
        name, separator, value = line.partition(" = ")
        if not separator or name not in names or name in seen:
            raise ValueError(f"Shadowrocket 策略组无效：{name}")
        seen.add(name)
        fields = split_fields(value)
        if fields[0] not in {"select", "url-test", "fallback", "load-balance"}:
            raise ValueError(f"Shadowrocket 策略类型无效：{fields[0]}")
        for field in fields[1:]:
            if field.startswith("policy-regex-filter="):
                re.compile(field.partition("=")[2])
            elif "=" not in field and field not in names | BUILTINS:
                raise ValueError(f"Shadowrocket 引用不存在的策略：{field}")
    if seen != names:
        raise ValueError("Shadowrocket 缺少策略组")
    user_count = len(model["user-rules"])
    if sections["Rule"][:user_count] != model["user-rules"]:
        # IPv6 and logical rules can have an intentional syntax translation.
        from adapters.shadowrocket import translate_rule
        expected = [line for rule in model["user-rules"] for line in
                    translate_rule(rule, model, manifest["base_url"] + "/" + manifest["rules_path"], set())]
        if sections["Rule"][:len(expected)] != expected:
            raise ValueError("Shadowrocket 个人规则目标或顺序改变")
    for line in sections["Rule"]:
        fields = split_fields(line)
        target = fields[1] if fields[0] == "FINAL" else fields[2]
        if target not in names | BUILTINS:
            raise ValueError(f"Shadowrocket 规则引用不存在的策略：{target}")
        if fields[0] == "RULE-SET":
            prefix = manifest["base_url"] + "/"
            if not fields[1].startswith(prefix):
                raise ValueError("远程规则集来源不属于本次发布")
            path = directory / fields[1][len(prefix):]
            if not path.is_file():
                raise ValueError(f"转换规则集缺失：{path}")
    if sections["Rule"][-1] != "FINAL," + model["rules"][-1].split(",")[1]:
        raise ValueError("Shadowrocket 兜底错误")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    result = validate_dist(args.dist)
    print(f"Validation passed: {result['build']} (Shadowrocket: static only)")


if __name__ == "__main__":
    main()
