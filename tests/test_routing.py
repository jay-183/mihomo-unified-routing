import copy
import fnmatch
import ipaddress
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

import yaml

from adapters import mihomo, shadowrocket
from scripts.model import ROOT, BUILTINS, LAN_CIDRS, check_url, load_model, load_yaml, parse_rule, split_fields
from scripts.validate import apply_script, read_conf, validate_dist


def snapshot(path):
    result = subprocess.run(["node", str(ROOT / "tests/run-script.cjs"), str(path), "snapshot"],
                            input="", text=True, encoding="utf-8", capture_output=True, check=True)
    return json.loads(result.stdout)


def proxy(name):
    return {"name": name, "type": "ss", "server": "127.0.0.1", "port": 9,
            "cipher": "aes-128-gcm", "password": "fixture-only"}


def match(rule, domain="", ip="", country=""):
    kind, value = split_fields(rule)[:2]
    if kind == "DOMAIN":
        return domain == value
    if kind == "DOMAIN-SUFFIX":
        return domain == value or domain.endswith("." + value)
    if kind == "DOMAIN-KEYWORD":
        return value in domain
    if kind == "DOMAIN-REGEX":
        return bool(re.search(value, domain))
    if kind == "DOMAIN-WILDCARD":
        return fnmatch.fnmatchcase(domain, value)
    if kind in {"IP-CIDR", "IP-CIDR6"}:
        return bool(ip) and ipaddress.ip_address(ip) in ipaddress.ip_network(value, strict=False)
    if kind == "GEOIP":
        if value == "LAN":
            return bool(ip) and any(ipaddress.ip_address(ip) in ipaddress.ip_network(n) for n in LAN_CIDRS)
        return bool(ip) and value == country
    if kind in {"PROCESS-NAME", "PROCESS-PATH"}:
        return False
    if kind in {"DST-PORT", "IP-ASN"}:
        return False  # These domain/IP fixtures supply no port or ASN metadata.
    raise AssertionError("Fixture evaluator does not support " + kind)


class OriginalRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = snapshot(ROOT / "docs/clash verge原始分流脚本.txt")
        cls.android = snapshot(ROOT / "docs/FlClash_安卓适配分流脚本.js")
        cls.baseline = json.loads((ROOT / "tests/fixtures/baseline.json").read_text(encoding="utf-8"))

    def test_both_original_scripts_have_identical_routing_data(self):
        self.assertEqual(self.original, self.android)

    def test_initial_extraction_preserved_every_rule_group_and_provider(self):
        for key, old in [("user-rules", "USER_RULES"), ("rules", "rules"),
                         ("proxy-groups", "proxyGroups"), ("rule-providers", "ruleProviders")]:
            self.assertEqual(self.baseline[key], self.original[old], key)
        self.assertEqual(len(self.baseline["user-rules"]), 15)
        self.assertEqual(len(self.baseline["proxy-groups"]), 24)
        self.assertEqual(len(self.baseline["rule-providers"]), 19)

    def test_adapter_preserves_original_behavior_except_dns_and_ipv6(self):
        config = {"proxies": [proxy("HK One")], "dns": {"enable": False}, "ipv6": True}
        before = apply_script(ROOT / "docs/clash verge原始分流脚本.txt", config)
        with tempfile.TemporaryDirectory() as temporary:
            script = Path(temporary) / "routing.js"
            script.write_text(mihomo.render(self.baseline, "baseline"), encoding="utf-8")
            after = apply_script(script, config)
        for field in ("rules", "rule-providers", "proxy-groups", "proxies", "proxy-providers"):
            self.assertEqual(before[field], after[field])
        self.assertEqual(after["dns"], config["dns"])
        self.assertTrue(after["ipv6"])


class SourceValidation(unittest.TestCase):
    def setUp(self):
        self.model = load_model()
        self.targets = {g["name"] for g in self.model["proxy-groups"]} | BUILTINS

    def parse(self, rule):
        return parse_rule(rule, self.targets, self.model["rule-providers"])

    def test_any_existing_target_and_no_resolve(self):
        for target in self.targets:
            self.parse("DOMAIN-SUFFIX,example.com," + target)
        self.assertEqual(self.parse("IP-CIDR,18.162.180.119/32,DIRECT,no-resolve")[-1], "no-resolve")

    def test_nested_logical_rules(self):
        rule = "AND,((DOMAIN-SUFFIX,example.com),(OR,((DST-PORT,443),(DST-PORT,8443)))),DIRECT"
        self.parse(rule)
        self.assertEqual(split_fields(rule)[-1], "DIRECT")

    def test_bad_rule_types_targets_options_and_syntax_fail(self):
        for rule in ["DOMAIN,x,missing", "PROCESS-NAME,x,DIRECT", "DOMAIN,x,DIRECT,typo",
                     "IP-CIDR,999.0.0.1/32,DIRECT", "DST-PORT,65536,DIRECT",
                     "DST-PORT,90-80,DIRECT", "RULE-SET,missing,DIRECT", "MATCH,DIRECT,no-resolve",
                     "DOMAIN,x,DIRECT,no-resolve", "DOMAIN,,DIRECT", "AND,((DOMAIN,x),DIRECT"]:
            with self.subTest(rule=rule), self.assertRaises(ValueError):
                self.parse(rule)

    def test_duplicate_yaml_keys_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.yaml"
            path.write_text("rules: []\nrules: [x]\n")
            with self.assertRaises(ValueError):
                load_yaml(path)

    def test_public_urls_do_not_accept_secrets_or_local_files(self):
        for url in ["http://example.com", "file:///secret", "https://u:p@example.com",
                    "https://example.com/?token=x", "https://example.com/#secret"]:
            with self.assertRaises(ValueError):
                check_url(url)

    def test_adding_a_region_reaches_mode_and_all_services(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in (ROOT / "src").glob("*.yaml"):
                (root / path.name).write_bytes(path.read_bytes())
            regions = load_yaml(root / "regions.yaml")
            regions["regions"].append({"id": "TEST_REGION", "name": "🧪 测试地区", "filter": "(?i)FixtureRegion"})
            (root / "regions.yaml").write_text(yaml.safe_dump(regions, allow_unicode=True), encoding="utf-8")
            result = load_model(root)
        groups = {g["name"]: g for g in result["proxy-groups"]}
        self.assertEqual(groups["🧪 测试地区"]["type"], "url-test")
        self.assertNotIn("🧪 测试地区自动", groups)
        self.assertIn("🧪 测试地区", groups["默认线路"]["proxies"])
        self.assertIn("🧪 测试地区", groups["OpenAI"]["proxies"])
        self.assertIn("FixtureRegion", groups["其他地区节点"]["exclude-filter"])

    def test_apps_follow_categories_and_allow_independent_region_selection(self):
        groups = {g["name"]: g for g in self.model["proxy-groups"]}
        families = {
            "国外媒体": ["YouTube", "Netflix", "Disney+", "TikTok"],
            "AI 服务": ["OpenAI", "Gemini", "Claude", "Grok"],
            "通讯社交": ["Telegram", "Discord", "X", "Facebook", "Instagram", "Reddit"],
        }
        for parent, apps in families.items():
            self.assertEqual(groups[parent]["proxies"][0], "默认线路")
            for app in apps:
                self.assertEqual(groups[app]["proxies"][0], parent)
                self.assertIn("日本节点", groups[app]["proxies"])
                self.assertIn("DIRECT", groups[app]["proxies"])
                self.assertNotIn("include-all", groups[app])
        self.assertIn("DOMAIN-KEYWORD,github,自定义代理", self.model["user-rules"])
        self.assertEqual(groups["Google"]["proxies"][0], "默认线路")
        for company in ["Apple", "Microsoft"]:
            self.assertEqual(groups[company]["proxies"][0], "直连模式")
        self.assertEqual(groups["默认线路"]["proxies"][0], "美国节点")
        self.assertEqual(len(groups["默认线路"]["proxies"]), len(set(groups["默认线路"]["proxies"])))
        for group in groups.values():
            if group["type"] == "select" and group["name"] not in {"手动选择", "广告过滤", "直连模式"}:
                self.assertIn("美国故障转移", group["proxies"])
                self.assertIn("美国负载均衡", group["proxies"])
        self.assertEqual(len(groups), 38)
        self.assertTrue(all(re.fullmatch(r"[\w +]+", name) for name in groups))
        self.assertEqual(groups["直连模式"]["proxies"][0], "DIRECT")
        used = {split_fields(r)[1] for r in self.model["rules"] if r.startswith("RULE-SET,")}
        self.assertEqual(used, set(self.model["rule-providers"]))

    def test_us_policies_share_region_filter_and_reject_unknown_region(self):
        groups = {g["name"]: g for g in self.model["proxy-groups"]}
        for name, kind in [("美国故障转移", "fallback"), ("美国负载均衡", "load-balance")]:
            group = groups[name]
            self.assertEqual(group["type"], kind)
            self.assertEqual(group["filter"], groups["美国节点"]["filter"])
            self.assertEqual(group["exclude-filter"], groups["美国节点"]["exclude-filter"])
            nodes = ["US One", "美国02", "Tokyo", "HK One", "美国 到期"]
            actual = [n for n in nodes if re.search(group["filter"], n) and not re.search(group["exclude-filter"], n)]
            self.assertEqual(actual, ["US One", "美国02"])
            self.assertEqual(group["interval"], self.model["settings"]["test"]["interval"])
        self.assertEqual(groups["美国负载均衡"]["strategy"], "consistent-hashing")
        for region_id, pool in [("MISSING", True), ("US", False)]:
            with self.subTest(region_id=region_id, pool=pool), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                for path in (ROOT / "src").glob("*.yaml"):
                    (root / path.name).write_bytes(path.read_bytes())
                data = load_yaml(root / "proxy-groups.yaml")
                group = next(g for g in data["groups"] if isinstance(g, dict) and g["name"] == "美国故障转移")
                group.update({"region": region_id, "node-pool": pool})
                (root / "proxy-groups.yaml").write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "地区节点池引用无效"):
                    load_model(root)

    def test_cycle_and_dns_fields_fail(self):
        for filename, mutate in [
            ("proxy-groups.yaml", lambda d: d["groups"][0]["proxies"].append("默认线路")),
            ("settings.yaml", lambda d: d.update({"dns": {"enable": False}})),
        ]:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                for path in (ROOT / "src").glob("*.yaml"):
                    (root / path.name).write_bytes(path.read_bytes())
                data = load_yaml(root / filename)
                mutate(data)
                (root / filename).write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_model(root)

    def test_editing_only_the_user_source_can_retarget_github(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in (ROOT / "src").glob("*.yaml"):
                (root / path.name).write_bytes(path.read_bytes())
            data = {"rules": ["DOMAIN-KEYWORD,github,自定义代理"]}
            (root / "user-rules.yaml").write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
            before = load_model(root)
            data["rules"][0] = "DOMAIN-KEYWORD,github,日本节点"
            (root / "user-rules.yaml").write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
            result = load_model(root)
            script = root / "routing.js"
            script.write_text(mihomo.render(result, "fixture"), encoding="utf-8")
            output = apply_script(script, {"proxies": [proxy("Japan")]})
        self.assertEqual(output["rules"][0], "DOMAIN-KEYWORD,github,日本节点")
        self.assertEqual(output["rules"][1:], before["rules"][1:])
        conf = shadowrocket.render(result, "fixture", "https://example.com", "https://example.com/rules", {"applications"})
        self.assertIn("DOMAIN-KEYWORD,github,日本节点", conf)


class AdapterRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_model()
        cls.dist = ROOT / "dist"
        cls.manifest = json.loads((cls.dist / "manifest.json").read_text(encoding="utf-8"))
        cls.conf = read_conf(cls.dist / "shadowrocket/config.conf")

    def test_outputs_pass_full_validation(self):
        validate_dist(self.dist)

    def test_empty_provider_only_mixed_and_invalid_node_sources(self):
        for client in ["clash-verge", "flclash"]:
            script = self.dist / client / "routing.js"
            provider = {"airport": {"type": "inline", "payload": [proxy("Tokyo")], "health-check": {"enable": False}}}
            for config in [{"proxy-providers": provider},
                           {"proxies": [None, {}, proxy("HK")], "proxy-providers": provider},
                           {"proxies": [proxy("SG")]}]:
                with self.subTest(client=client, config=config):
                    result = apply_script(script, config)
                    self.assertNotIn("dns", result)
                    if "proxy-providers" in config:
                        self.assertEqual(result["proxy-providers"], provider)
                    self.assertTrue(all(p["udp"] for p in result["proxies"]))
            for config in [{}, {"proxies": [None, {}]}, {"proxy-providers": []},
                           {"proxies": [proxy("DIRECT")]}, {"proxies": [proxy("HK"), proxy("HK")]}]:
                with self.subTest(config=config), self.assertRaises(ValueError):
                    apply_script(script, config)

    def test_local_dns_is_preserved_by_value_and_object_identity(self):
        code = (self.dist / "clash-verge/routing.js").read_text(encoding="utf-8")
        extra = '\nconst d={enable:false};const c={proxies:[{name:"HK"}],dns:d,ipv6:true};if(main(c).dns!==d||!c.ipv6)throw Error("DNS mutated");'
        subprocess.run(["node", "-"], input=code + extra, text=True, encoding="utf-8",
                       check=True, capture_output=True)

    def test_local_selection_cache_is_enabled_without_changing_other_profile_settings(self):
        for client in ["clash-verge", "flclash"]:
            for profile in [None, {"store-selected": False, "store-fake-ip": False}]:
                config = {"proxies": [proxy("US One")]}
                if profile is not None:
                    config["profile"] = profile
                result = apply_script(self.dist / client / "routing.js", config)
                self.assertEqual(result["profile"], {**(profile or {}), "store-selected": True})

    def test_all_regions_and_fake_nodes_have_equivalent_regex_membership(self):
        nodes = ["香港 01", "HK Two", "Hong Kong 3", "台北 01", "TW 01", "Tokyo 2", "大阪", "SG 1",
                 "Singapore 2", "Los Angeles", "Seattle", "France Paris", "德国 Frankfurt", "加拿大 01",
                 "Australia", "HK 剩余流量", "Japan 套餐到期", "Expiry USA", "reset SG"]
        sr = {}
        for line in self.conf["Proxy Group"]:
            name, _, value = line.partition(" = ")
            for item in split_fields(value):
                if item.startswith("policy-regex-filter="):
                    sr[name] = re.compile(item.partition("=")[2])
        for group in self.model["proxy-groups"]:
            if not group.get("include-all"):
                continue
            for node in nodes:
                expected = not re.search(group["exclude-filter"], node) and (
                    "filter" not in group or bool(re.search(group["filter"], node)))
                self.assertEqual(bool(sr[group["name"]].search(node)), bool(expected), (group["name"], node))
        self.assertTrue(sr["其他地区节点"].search("加拿大 01"))
        self.assertFalse(any(p.search("HK 剩余流量") for p in sr.values()))

    def test_business_groups_do_not_expand_concrete_nodes(self):
        for group in self.model["proxy-groups"]:
            if group["name"] in {"OpenAI", "Gemini", "Claude", "Telegram", "Google", "Apple", "Microsoft", "YouTube", "Netflix"}:
                self.assertNotIn("include-all", group)
                self.assertIn("日本节点", group["proxies"])

    def test_public_conversion_preserves_semantics_and_reports_process_rules(self):
        report = json.loads((self.dist / "compatibility.json").read_text(encoding="utf-8"))
        for name, provider in self.model["rule-providers"].items():
            original = load_yaml(self.dist / "upstream" / (name + ".yaml"))["payload"]
            converted, unsupported = shadowrocket.convert_payload(name, provider, original)
            actual = [line for line in (self.dist / self.manifest["rules_path"] / (name + ".list")).read_text(encoding="utf-8").splitlines()
                      if line and not line.startswith("#")]
            self.assertEqual(actual, converted)
            expansions = sum(len(shadowrocket.DOMAIN_REGEX_EXPANSIONS.get(entry, [entry])) - 1
                             for entry in original)
            self.assertEqual(len(actual) + len(unsupported), len(original) + expansions)
            if unsupported:
                self.assertEqual(report["shadowrocket_unsupported_public_rules"][name], unsupported)

    def test_unknown_public_types_fail_instead_of_disappearing(self):
        with self.assertRaises(ValueError):
            shadowrocket.convert_payload("new", {"behavior": "classical"}, ["UNSUPPORTED,value"])

    def test_netflix_regex_expansions_preserve_root_subdomain_and_label_boundaries(self):
        for original, converted in shadowrocket.DOMAIN_REGEX_EXPANSIONS.items():
            if "amazonaws" not in original:
                continue
            stem = converted[0].split(",", 1)[1].split("?*", 1)[0]
            for domain in [stem + tail for tail in ["a.amazonaws.com", "us-east-1.amazonaws.com", ".amazonaws.com"]] + [
                "edge." + stem + "abc.amazonaws.com", "evil" + stem + "abc.amazonaws.com",
                stem + "abc.amazonaws.com.evil.test", "example.com",
            ]:
                self.assertEqual(any(match(rule, domain) for rule in converted), match(original, domain), domain)

    def test_disney_regex_expansion_matches_only_the_eight_original_domains(self):
        original = r"DOMAIN-REGEX,^hses[1-7]?\.akamaized\.net$"
        converted = shadowrocket.DOMAIN_REGEX_EXPANSIONS[original]
        self.assertEqual(len(converted), 8)
        for suffix in ["", *range(0, 12), "a", "01"]:
            for prefix in ["", "edge.", "evil"]:
                domain = f"{prefix}hses{suffix}.akamaized.net"
                self.assertEqual(any(match(rule, domain) for rule in converted), match(original, domain), domain)

    def test_google_regex_reduction_requires_the_covering_suffix(self):
        for regex, suffix in shadowrocket.GOOGLE_REDUNDANT_REGEX.items():
            result, _ = shadowrocket.convert_payload("google", {"behavior": "classical"}, [regex, suffix])
            self.assertEqual(result, [suffix, suffix])
            with self.assertRaises(ValueError):
                shadowrocket.convert_payload("google", {"behavior": "classical"}, [regex])

    def test_shadowrocket_selectors_default_to_their_parent_and_regions_are_automatic(self):
        lines = dict(line.split(" = ", 1) for line in self.conf["Proxy Group"])
        for name, parent in [("YouTube", "国外媒体"), ("Netflix", "国外媒体"),
                             ("OpenAI", "AI 服务"), ("Gemini", "AI 服务"),
                             ("国外媒体", "默认线路"), ("Google", "默认线路"),
                             ("默认线路", "美国节点"), ("Apple", "直连模式"), ("Microsoft", "直连模式"),
                             ("直连模式", "DIRECT")]:
            self.assertIn("policy-select-name=" + parent, split_fields(lines[name]))
        self.assertEqual(split_fields(lines["美国节点"])[0], "url-test")
        self.assertNotIn("美国自动", lines)

    def test_openai_regex_approximation_is_explicit_and_includes_original(self):
        original, converted = next(iter(shadowrocket.DOMAIN_REGEX_APPROXIMATIONS.items()))
        for domain in ["chatgpt-async-webps-prod-a-12.webpubsub.azure.com", "chatgpt-async-webps-prod-west-us-7.webpubsub.azure.com"]:
            self.assertTrue(match(original, domain))
            self.assertTrue(match(converted, domain))
        widened = "chatgpt-async-webps-prod-a-other.webpubsub.azure.com"
        self.assertFalse(match(original, widened))
        self.assertTrue(match(converted, widened))

    def test_match_lan_ipv6_and_logical_conversion(self):
        translate = lambda rule: shadowrocket.translate_rule(rule, self.model, "https://example.com/rules", set())
        self.assertEqual(translate("MATCH,DIRECT"), ["FINAL,DIRECT"])
        self.assertEqual(translate("IP-CIDR6,fc00::/7,DIRECT,no-resolve"), ["IP-CIDR,fc00::/7,DIRECT,no-resolve"])
        self.assertEqual(len(translate("GEOIP,LAN,DIRECT,no-resolve")), len(LAN_CIDRS))
        self.assertTrue(all(line.endswith(",DIRECT,no-resolve") for line in translate("GEOIP,LAN,DIRECT,no-resolve")))
        logical = translate("AND,((IP-CIDR6,fc00::/7),(RULE-SET,private)),DIRECT")[0]
        self.assertEqual(logical, "AND,((IP-CIDR,fc00::/7),(RULE-SET,https://example.com/rules/private.list)),DIRECT")

    def test_custom_japan_target_does_not_change_other_rules(self):
        model = copy.deepcopy(self.model)
        model["rules"].insert(0, "DOMAIN-SUFFIX,example.com,日本节点")
        model["user-rules"].insert(0, model["rules"][0])
        result = shadowrocket.render(model, "test", "https://example.com", "https://example.com/rules", {"applications"})
        self.assertIn("DOMAIN-SUFFIX,example.com,日本节点", result)
        self.assertEqual(model["rules"][1:], self.model["rules"])

    def test_generated_rules_have_equivalent_expected_routes(self):
        providers, raw_providers = {}, {}
        for name, definition in self.model["rule-providers"].items():
            raw_providers[name] = load_yaml(self.dist / "upstream" / (name + ".yaml"))["payload"]
            providers[name], _ = shadowrocket.convert_payload(name, definition, raw_providers[name])

        def original_matches(name, domain, ip, country):
            behavior = self.model["rule-providers"][name]["behavior"]
            for entry in raw_providers[name]:
                if behavior == "domain":
                    if entry.startswith("+."):
                        value = entry[2:]
                        if domain == value or domain.endswith("." + value):
                            return True
                    elif "*" in entry or "?" in entry:
                        if fnmatch.fnmatchcase(domain, entry):
                            return True
                    elif domain == entry:
                        return True
                elif behavior == "ipcidr":
                    if ip and ipaddress.ip_address(ip) in ipaddress.ip_network(entry, strict=False):
                        return True
                elif match(entry, domain, ip, country):
                    return True
            return False

        def route(rules, domain, ip, country, sr=False):
            def condition(fields):
                kind, value = fields[:2]
                if kind == "RULE-SET":
                    name = value.rsplit("/", 1)[-1].removesuffix(".list") if sr else value
                    return any(match(r, domain, ip, country) for r in providers[name]) if sr else original_matches(name, domain, ip, country)
                if kind in {"AND", "OR", "NOT"}:
                    children = [condition(split_fields(c[1:-1])) for c in split_fields(value[1:-1])]
                    return all(children) if kind == "AND" else any(children) if kind == "OR" else not children[0]
                return match(",".join(fields), domain, ip, country)

            for line in rules:
                fields = split_fields(line)
                if fields[0] in {"MATCH", "FINAL"}:
                    return fields[1]
                if condition(fields[:2]):
                    return fields[2]
            self.fail("No final rule")

        cases = [("github.com", "", "", "自定义代理"),
                 ("github.io", "", "", "自定义代理"),
                 ("blinkroom.test", "", "", "直连模式"),
                 ("joox.com", "", "", "香港节点"),
                 ("dnscheck.tools", "", "", "自定义代理"),
                 ("ippure.com", "", "", "手动选择"),
                 ("api.openai.com", "", "", "OpenAI"),
                 ("gemini.google.com", "", "", "Gemini"),
                 ("claude.ai", "", "", "Claude"),
                 ("www.youtube.com", "", "", "YouTube"),
                 ("www.netflix.com", "", "", "Netflix"),
                 ("apiproxy-device-prod-nlb-test.amazonaws.com", "", "", "Netflix"),
                 ("edge.dualstack.apiproxy-test.amazonaws.com", "", "", "Netflix"),
                 ("www.disneyplus.com", "", "", "Disney+"),
                 ("www.tiktok.com", "", "", "TikTok"),
                 ("www.facebook.com", "", "", "Facebook"),
                 ("www.instagram.com", "", "", "Instagram"),
                 ("www.reddit.com", "", "", "Reddit"),
                 ("discord.com", "", "", "Discord"),
                 ("x.com", "", "", "X"),
                 ("grok.com", "", "", "Grok"),
                 ("telegram.org", "", "", "Telegram"),
                 ("", "149.154.167.50", "US", "Telegram"),
                 ("gitlab.com", "", "", "默认线路"),
                 ("www.apple.com", "", "", "Apple"),
                 ("www.microsoft.com", "", "", "Microsoft"),
                 ("www.google.com", "", "", "Google"),
                 ("www.baidu.com", "", "", "直连模式"),
                 ("", "18.162.180.119", "HK", "直连模式"),
                 ("", "192.168.10.2", "LAN", "直连模式"),
                 ("unmatched-fixture.routing-test", "", "", "漏网之鱼")]
        for domain, ip, country, expected in cases:
            with self.subTest(domain=domain, ip=ip):
                source_target = route(self.model["rules"], domain, ip, country)
                self.assertEqual(source_target, expected)
                self.assertEqual(route(self.conf["Rule"], domain, ip, country, True), source_target)


if __name__ == "__main__":
    unittest.main()
