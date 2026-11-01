"""Run Mihomo -t and inspect real group membership through a loopback controller."""
import argparse
import json
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from urllib.parse import quote

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.model import ROOT, load_model
from scripts.validate import apply_script


def node(name):
    return {"name": name, "type": "ss", "server": "127.0.0.1", "port": 9,
            "cipher": "aes-128-gcm", "password": "test-fixture-only"}


def verify(core):
    core = str(core.resolve())
    version = subprocess.run([core, "-v"], text=True, encoding="utf-8", capture_output=True, check=True).stdout.strip()
    model = load_model()
    cases = {
        "inline": {"proxies": [node(n) for n in ["HK One", "TW One", "Tokyo", "Singapore", "美国03", "Paris", "加拿大", "HK 剩余流量"]]},
        "provider": {"proxy-providers": {"fixture": {"type": "inline", "payload": [node("Japan Two"), node("US Expiry")], "health-check": {"enable": False}}}},
        "mixed": {"proxies": [node("SG Three")], "proxy-providers": {"fixture": {"type": "inline", "payload": [node("香港 Four"), node("reset HK")], "health-check": {"enable": False}}}},
    }
    results = []
    work = ROOT / ".cache"
    work.mkdir(exist_ok=True)
    database = work / "Country.mmdb"
    if not database.exists():
        url = "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/release/country.mmdb"
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read(20 * 1024 * 1024)
        if b"\xab\xcd\xefMaxMind.com" not in content[-131072:]:
            raise ValueError("下载内容不是 MaxMind 数据库")
        database.write_bytes(content)
    for label, fixture in cases.items():
        with tempfile.TemporaryDirectory(prefix="core-check-", dir=work) as temporary:
            home = Path(temporary)
            (home / "Country.mmdb").write_bytes(database.read_bytes())
            config = apply_script(ROOT / "dist/clash-verge/routing.js", fixture)
            for name, provider in config["rule-providers"].items():
                target = home / provider["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / "dist/upstream" / (name + ".yaml")).read_bytes())
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            config["external-controller"] = f"127.0.0.1:{port}"
            path = home / "config.yaml"
            path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")
            checked = subprocess.run([core, "-t", "-d", str(home), "-f", str(path)],
                                     capture_output=True, text=True, encoding="utf-8", timeout=60)
            if checked.returncode:
                raise ValueError(f"Mihomo {label} 配置验证失败：{checked.stdout}\n{checked.stderr}")
            all_nodes = [p["name"] for p in fixture.get("proxies", [])]
            for provider in fixture.get("proxy-providers", {}).values():
                all_nodes.extend(p["name"] for p in provider["payload"])
            with (home / "core.log").open("w", encoding="utf-8") as log:
                process = subprocess.Popen([core, "-d", str(home), "-f", str(path)], stdout=log, stderr=subprocess.STDOUT,
                                           creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
                try:
                    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
                    deadline = time.monotonic() + 25
                    observed = None
                    while time.monotonic() < deadline:
                        if process.poll() is not None:
                            break
                        try:
                            with opener.open(f"http://127.0.0.1:{port}/proxies", timeout=1) as response:
                                observed = json.load(response)["proxies"]
                            if all(g["name"] in observed for g in model["proxy-groups"]):
                                break
                        except (OSError, ValueError):
                            pass
                        time.sleep(0.2)
                    if observed is None:
                        raise ValueError(f"Mihomo {label} 未启动：{(home / 'core.log').read_text(encoding='utf-8')}")
                    for group in model["proxy-groups"]:
                        if not group.get("include-all"):
                            continue
                        expected = {name for name in all_nodes if not re.search(group["exclude-filter"], name)
                                    and ("filter" not in group or re.search(group["filter"], name))}
                        actual = set(observed[group["name"]]["all"])
                        expected.update(group.get("proxies", []))
                        if actual != (expected or {"COMPATIBLE"}):
                            raise ValueError(f"{label} / {group['name']}: 节点成员不符 {actual} != {expected}")
                    result = {"case": label, "config_test": "passed", "runtime_group_membership": "passed"}
                    if label == "inline":
                        endpoint = f"http://127.0.0.1:{port}/proxies"

                        def choose(group, target):
                            request = urllib.request.Request(endpoint + "/" + quote(group, safe=""),
                                data=json.dumps({"name": target}).encode(), method="PUT",
                                headers={"Content-Type": "application/json"})
                            with opener.open(request, timeout=3):
                                pass

                        def expect_chain(expected):
                            with opener.open(endpoint, timeout=3) as response:
                                current = json.load(response)["proxies"]
                            chain = [expected[0]]
                            while "now" in current.get(chain[-1], {}):
                                chain.append(current[chain[-1]]["now"])
                                if len(chain) > len(current):
                                    raise ValueError("运行中的策略组循环引用")
                            if chain != expected:
                                raise ValueError(f"实际策略链不符：{chain} != {expected}")

                        choose("模式选择", "美国")
                        # One eligible US node makes the url-test choice deterministic.
                        expect_chain(["YouTube", "国外媒体", "模式选择", "美国", "美国03"])
                        choose("国外媒体", "美国")
                        expect_chain(["YouTube", "国外媒体", "美国", "美国03"])
                        choose("YouTube", "日本")
                        expect_chain(["YouTube", "日本", "Tokyo"])
                        expect_chain(["Netflix", "国外媒体", "美国", "美国03"])
                        choose("AI 服务", "美国")
                        choose("Gemini", "日本")
                        expect_chain(["OpenAI", "AI 服务", "美国", "美国03"])
                        expect_chain(["Gemini", "日本", "Tokyo"])
                        choose("YouTube", "国外媒体")
                        expect_chain(["YouTube", "国外媒体", "美国", "美国03"])
                        result["hierarchy_selection"] = "passed"
                    results.append(result)
                finally:
                    process.terminate()
                    process.wait(timeout=10)
    manifest = json.loads((ROOT / "dist/manifest.json").read_text(encoding="utf-8"))
    report = {"build": manifest["build"], "core": version, "cases": results,
              "scope": "配置解析与真实节点分组；未连接真实机场或测试出口流量"}
    (work / "mihomo-validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", required=True, type=Path)
    print(json.dumps(verify(parser.parse_args().core), ensure_ascii=False, indent=2))
