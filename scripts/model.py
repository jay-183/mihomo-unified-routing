"""Read the shared source and validate it before rendering either platform."""
import copy
import ipaddress
import re
from pathlib import Path
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
BUILTINS = {"DIRECT", "REJECT"}
RULE_TYPES = {
    "DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-WILDCARD",
    "IP-CIDR", "IP-CIDR6", "GEOIP", "IP-ASN", "DST-PORT", "RULE-SET",
    "AND", "OR", "NOT", "MATCH",
}
LAN_CIDRS = (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "0.0.0.0/32",
    "127.0.0.0/8", "224.0.0.0/4", "169.254.0.0/16", "fc00::/7",
    "::/128", "::1/128", "ff00::/8", "fe80::/10",
)


def load_yaml(path):
    # Duplicate mapping keys must not silently change a provider or policy.
    class UniqueLoader(getattr(yaml, "CSafeLoader", yaml.SafeLoader)):
        pass

    def mapping(loader, node):
        result = {}
        for key, value in node.value:
            name = loader.construct_object(key)
            if name in result:
                raise ValueError(f"{path}: 重复字段 {name}")
            result[name] = loader.construct_object(value)
        return result

    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    return yaml.load(Path(path).read_text(encoding="utf-8-sig"), Loader=UniqueLoader)


def split_fields(text):
    """Split rule commas while leaving logical expressions intact."""
    if not isinstance(text, str) or any(c in text for c in "\r\n#"):
        raise ValueError(f"规则必须是单行字符串：{text!r}")
    fields, depth, start = [], 0, 0
    for i, char in enumerate(text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            fields.append(text[start:i].strip())
            start = i + 1
        if depth < 0:
            raise ValueError(f"括号不匹配：{text}")
    if depth:
        raise ValueError(f"括号不匹配：{text}")
    fields.append(text[start:].strip())
    if not all(fields):
        raise ValueError(f"规则有空字段：{text}")
    return fields


def validate_match(kind, value, providers):
    if kind not in RULE_TYPES - {"MATCH"}:
        raise ValueError(f"三平台适配尚未支持规则类型 {kind}；请扩展适配器后使用")
    if kind in {"AND", "OR", "NOT"}:
        if not value.startswith("(") or not value.endswith(")"):
            raise ValueError(f"逻辑规则缺少括号：{value}")
        children = split_fields(value[1:-1])
        if (kind == "NOT" and len(children) != 1) or (kind != "NOT" and len(children) < 2):
            raise ValueError(f"{kind} 子条件数量错误")
        for child in children:
            if not child.startswith("(") or not child.endswith(")"):
                raise ValueError(f"子条件缺少括号：{child}")
            parts = split_fields(child[1:-1])
            if len(parts) != 2:
                raise ValueError(f"子条件格式错误：{child}")
            validate_match(*parts, providers)
    elif kind == "RULE-SET" and value not in providers:
        raise ValueError(f"引用不存在的规则集：{value}")
    elif kind in {"IP-CIDR", "IP-CIDR6"}:
        network = ipaddress.ip_network(value, strict=False)
        if kind == "IP-CIDR6" and network.version != 6:
            raise ValueError(f"IP-CIDR6 需要 IPv6：{value}")
    elif kind == "GEOIP" and not re.fullmatch(r"[A-Za-z]{2}|LAN", value):
        raise ValueError(f"不支持的 GEOIP 值：{value}")
    elif kind == "IP-ASN" and not value.isdecimal():
        raise ValueError(f"ASN 必须是数字：{value}")
    elif kind == "DST-PORT":
        if not value.isdecimal() or not 1 <= int(value) <= 65535:
            raise ValueError(f"当前三平台仅核实单端口；多个端口请使用 OR 条件：{value}")
    elif kind.startswith("DOMAIN") and not re.fullmatch(r"[\w.*?+-]+", value):
        raise ValueError(f"域名字段无效：{value}")


def parse_rule(rule, targets, providers):
    fields = split_fields(rule)
    index = 1 if fields[0] == "MATCH" else 2
    if len(fields) not in {index + 1, index + 2}:
        raise ValueError(f"规则字段数错误：{rule}")
    if fields[index] not in targets:
        raise ValueError(f"引用不存在的策略：{fields[index]}")
    if len(fields) == index + 2 and fields[-1] != "no-resolve":
        raise ValueError(f"不支持的附加参数：{rule}")
    if fields[0] == "MATCH":
        if len(fields) != 2:
            raise ValueError(f"MATCH 不支持附加参数：{rule}")
    else:
        validate_match(fields[0], fields[1], providers)
        if fields[-1] == "no-resolve" and fields[0] not in {"RULE-SET", "GEOIP", "IP-CIDR", "IP-CIDR6", "IP-ASN"}:
            raise ValueError(f"此规则不能使用 no-resolve：{rule}")
    return fields


def check_url(url):
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("公共 URL 必须为不含凭证、查询串和片段的 HTTPS 地址")
    return url.rstrip("/")


def load_model(root=ROOT / "src"):
    settings = load_yaml(root / "settings.yaml")
    region_source = load_yaml(root / "regions.yaml")
    groups_source = load_yaml(root / "proxy-groups.yaml")
    providers = load_yaml(root / "rule-providers.yaml")["providers"]
    user = load_yaml(root / "user-rules.yaml")["rules"]
    rules = load_yaml(root / "rules.yaml")["rules"]
    if set(settings) != {"test", "node-exclude-filter", "udp", "region-tolerance"}:
        raise ValueError("settings 字段无效；此项目不接受 DNS 等额外配置")
    if set(settings["test"]) != {"url", "interval", "timeout", "lazy", "max-failed-times", "hidden"}:
        raise ValueError("测速配置字段无效")
    for key in ("interval", "timeout", "max-failed-times"):
        if type(settings["test"][key]) is not int or settings["test"][key] <= 0:
            raise ValueError(f"测速 {key} 必须是正整数")
    check_url(settings["test"]["url"])
    if type(settings["udp"]) is not bool or type(settings["region-tolerance"]) is not int or settings["region-tolerance"] < 0:
        raise ValueError("udp 或 region-tolerance 无效")
    regions = region_source["regions"]
    if not regions or len({r["id"] for r in regions}) != len(regions):
        raise ValueError("地区不能为空且 id 不能重复")
    patterns = [settings["node-exclude-filter"]] + [r["filter"] for r in regions]
    for pattern in patterns:
        re.compile(pattern)
        # The shared regex subset is RE2-compatible; SR exclusion is adapter-generated.
        if re.search(r"\(\?[=!<]|\\[1-9]|[,\r\n#]", pattern):
            raise ValueError(f"地区正则超出已验证的 RE2/ICU 交集：{pattern}")
    exclude = settings["node-exclude-filter"]
    known = "|".join(r["filter"].removeprefix("(?i)") for r in regions)
    other_exclude = "(?i)" + exclude.removeprefix("(?i)") + "|" + known
    region_groups = []
    for region in regions + [{"name": region_source["other"]}]:
        group = {**settings["test"], "name": region["name"], "type": "url-test",
                 "tolerance": settings["region-tolerance"], "include-all": True,
                 "exclude-filter": exclude if "filter" in region else other_exclude}
        if "filter" in region:
            group["filter"] = region["filter"]
        region_groups.append(group)
    region_names = [g["name"] for g in region_groups]

    def expand(items, services=None):
        result = []
        for item in items:
            if item == "$regions":
                result.extend(region_names)
            elif item == "$services":
                if services is None:
                    raise ValueError("service-options 不能递归引用自己")
                result.extend(services)
            else:
                result.append(item)
        return result

    services = expand(groups_source["service-options"])
    groups = []
    for item in groups_source["groups"]:
        if item == "$regions":
            groups.extend(region_groups)
            continue
        if not isinstance(item, dict) or set(item) - {"name", "type", "proxies", "node-pool", "tolerance", "strategy"}:
            raise ValueError(f"未知策略组字段：{item}")
        group = copy.deepcopy(item)
        pool = group.pop("node-pool", False)
        if pool or group["name"] == "🔰 模式选择":
            group = {**settings["test"], **group}
        if pool:
            group.update({"include-all": True, "exclude-filter": exclude})
        if "proxies" in group:
            group["proxies"] = expand(group["proxies"], services)
        groups.append(group)
    names = [g["name"] for g in groups]
    if len(set(names)) != len(names) or set(names) & (BUILTINS | {"GLOBAL", "COMPATIBLE"}):
        raise ValueError("策略组名称重复或使用保留名称")
    targets = set(names) | BUILTINS
    for group in groups:
        if any(c in group["name"] for c in ",=#\r\n"):
            raise ValueError("策略名称包含配置分隔符")
        if group["type"] not in {"select", "url-test", "fallback", "load-balance"}:
            raise ValueError(f"未知策略组类型：{group['type']}")
        for target in group.get("proxies", []):
            if target not in targets:
                raise ValueError(f"{group['name']} 引用不存在的策略 {target}")
        if not group.get("include-all") and not group.get("proxies"):
            raise ValueError(f"策略组为空：{group['name']}")
    graph = {g["name"]: g.get("proxies", []) for g in groups}

    def visit(name, stack):
        if name in stack:
            raise ValueError(f"策略组循环引用：{' -> '.join(stack + [name])}")
        for child in graph.get(name, []):
            visit(child, stack + [name])

    for name in names:
        visit(name, [])
    for name, provider in providers.items():
        if not re.fullmatch(r"[a-z0-9-]+", name):
            raise ValueError(f"规则集名称无效：{name}")
        if set(provider) != {"type", "behavior", "format", "interval", "url", "path"}:
            raise ValueError(f"规则集字段无效：{name}")
        if provider["type"] != "http" or provider["format"] != "yaml" or provider["behavior"] not in {"domain", "classical", "ipcidr"}:
            raise ValueError(f"不支持的规则集格式：{name}")
        check_url(provider["url"])
        path = Path(provider["path"])
        if path.is_absolute() or ".." in path.parts or ":" in provider["path"]:
            raise ValueError(f"规则集缓存路径必须在工作目录内：{name}")
        if type(provider["interval"]) is not int or provider["interval"] <= 0:
            raise ValueError(f"规则集更新周期无效：{name}")
    if not isinstance(user, list) or not isinstance(rules, list):
        raise ValueError("rules 必须为有序列表")
    all_rules = user + rules
    for rule in all_rules:
        parse_rule(rule, targets, providers)
    if not all_rules or not all_rules[-1].startswith("MATCH,") or any(r.startswith("MATCH,") for r in all_rules[:-1]):
        raise ValueError("仅允许在最后一条使用 MATCH")
    return {"settings": settings, "regions": region_source, "user-rules": user,
            "proxy-groups": groups, "rule-providers": providers, "rules": all_rules}
