"""Translate shared groups and rules; never emit DNS settings."""
import ipaddress

from scripts.model import BUILTINS, LAN_CIDRS, parse_rule, split_fields, validate_match

# SR has no verified DOMAIN-REGEX equivalent. Keep this one upstream exception explicit.
DOMAIN_REGEX_APPROXIMATIONS = {
    r"DOMAIN-REGEX,^chatgpt-async-webps-prod-\S+-\d+\.webpubsub\.azure\.com$":
        "DOMAIN-WILDCARD,chatgpt-async-webps-prod-*-*.webpubsub.azure.com",
}


def node_filter(group):
    excluded = group["exclude-filter"].removeprefix("(?i)")
    included = group.get("filter", ".*").removeprefix("(?i)")
    return f"(?i)^(?!.*(?:{excluded}))(?=.*(?:{included})).*$"


def convert_payload(name, provider, payload):
    """Return policy-free rules for SR RULE-SET and explicit unsupported entries."""
    if not isinstance(payload, list) or not payload:
        raise ValueError(f"规则集 {name} 的 payload 不能为空")
    converted, unsupported = [], []
    for entry in payload:
        if not isinstance(entry, str) or not entry.strip() or any(c in entry for c in "\r\n#"):
            raise ValueError(f"{name}: 无效规则集条目 {entry!r}")
        if provider["behavior"] == "domain":
            if entry.startswith("+."):
                kind, value = "DOMAIN-SUFFIX", entry[2:]
            elif "*" in entry or "?" in entry:
                kind, value = "DOMAIN-WILDCARD", entry
            elif entry.startswith("."):
                kind, value = "DOMAIN-WILDCARD", "*" + entry
            else:
                kind, value = "DOMAIN", entry
            validate_match(kind, value, {})
            converted.append(f"{kind},{value}")
        elif provider["behavior"] == "ipcidr":
            network = ipaddress.ip_network(entry, strict=False)
            converted.append(f"IP-CIDR,{network}")
        else:
            if entry in DOMAIN_REGEX_APPROXIMATIONS:
                converted.append(DOMAIN_REGEX_APPROXIMATIONS[entry])
                continue
            parts = split_fields(entry)
            if parts[0] in {"PROCESS-NAME", "PROCESS-PATH", "PROCESS-NAME-REGEX", "PROCESS-PATH-REGEX"}:
                unsupported.append(entry)
                continue
            if len(parts) not in {2, 3} or (len(parts) == 3 and parts[-1] != "no-resolve"):
                raise ValueError(f"{name}: 不支持的 classical 条目 {entry}")
            validate_match(parts[0], parts[1], {})
            if parts[0] in {"AND", "OR", "NOT", "RULE-SET"}:
                raise ValueError(f"{name}: 此远程 classical 类型需显式适配：{entry}")
            parts[0] = "IP-CIDR" if parts[0] == "IP-CIDR6" else parts[0]
            converted.append(",".join(parts))
    return converted, unsupported


def translate_rule(rule, model, rules_url, empty_providers):
    targets = {g["name"] for g in model["proxy-groups"]} | BUILTINS
    parts = parse_rule(rule, targets, model["rule-providers"])
    if parts[0] == "MATCH":
        return [f"FINAL,{parts[1]}"]
    if parts[0] == "RULE-SET":
        if parts[1] in empty_providers:
            return [f"# {rule} — 此公共规则集仅含 iOS 不支持的进程规则，详见 compatibility.json"]
    if parts[0] == "GEOIP" and parts[1].upper() == "LAN":
        return [",".join(["IP-CIDR", cidr, *parts[2:]]) for cidr in LAN_CIDRS]

    def condition(kind, value):
        if kind in {"AND", "OR", "NOT"}:
            children = []
            for child in split_fields(value[1:-1]):
                children.append("(" + ",".join(condition(*split_fields(child[1:-1]))) + ")")
            return kind, "(" + ",".join(children) + ")"
        if kind == "RULE-SET":
            if value in empty_providers:
                raise ValueError(f"iOS 无法在逻辑条件中应用纯进程规则集 {value}")
            return kind, f"{rules_url}/{value}.list"
        if kind == "GEOIP" and value.upper() == "LAN":
            return "OR", "(" + ",".join(f"(IP-CIDR,{cidr})" for cidr in LAN_CIDRS) + ")"
        return ("IP-CIDR" if kind == "IP-CIDR6" else kind), value

    parts[:2] = condition(*parts[:2])
    return [",".join(parts)]


def render(model, version, base_url, rules_url, empty_providers):
    lines = [f"# Unified routing build: {version}",
             "# Generated file. Edit src/*.yaml and rebuild.",
             "# 本文件使用首页已导入的节点；生成器未配置 DNS。",
             "[General]", f"update-url = {base_url}/shadowrocket/config.conf", "", "[Proxy Group]"]
    for group in model["proxy-groups"]:
        fields = [group["type"], *group.get("proxies", [])]
        if group.get("include-all"):
            fields.append("policy-regex-filter=" + node_filter(group))
        if "interval" in group:
            fields.extend([f"url={group['url']}", f"interval={group['interval']}",
                           f"timeout={group['timeout'] / 1000:g}"])
        if "tolerance" in group:
            fields.append(f"tolerance={group['tolerance']}")
        if group["type"] == "select" and group.get("proxies"):
            fields.append("policy-select-name=" + group["proxies"][0])
        lines.append(group["name"] + " = " + ",".join(fields))
    lines.extend(["", "[Rule]"])
    for rule in model["rules"]:
        lines.extend(translate_rule(rule, model, rules_url, empty_providers))
    return "\n".join(lines) + "\n"
