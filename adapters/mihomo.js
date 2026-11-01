// Unified routing build: __VERSION__
// Generated file. Edit src/*.yaml and rebuild.
const ROUTING = __DATA__;

function main(config) {
  if (!config || typeof config !== "object" || Array.isArray(config)) {
    throw new Error("订阅必须是配置对象。");
  }
  const proxies = Array.isArray(config.proxies) ? config.proxies : [];
  const providers = config["proxy-providers"] == null ? {} : config["proxy-providers"];
  if (typeof providers !== "object" || Array.isArray(providers)) {
    throw new Error("proxy-providers 必须是对象。");
  }
  const valid = proxies.filter(p => p && typeof p === "object" &&
    typeof p.name === "string" && p.name.trim());
  if (!valid.length && !Object.keys(providers).length) {
    throw new Error("当前订阅中未找到任何代理节点或 proxy-provider。");
  }
  const groupNames = ROUTING["proxy-groups"].map(g => g.name);
  const names = new Set(["DIRECT", "REJECT", "COMPATIBLE", "GLOBAL", ...groupNames]);
  for (const proxy of valid) {
    if (names.has(proxy.name)) throw new Error("节点名称重复或与策略冲突：" + proxy.name);
    names.add(proxy.name);
  }
  const routing = JSON.parse(JSON.stringify(ROUTING));
  config["proxy-groups"] = routing["proxy-groups"];
  config["rule-providers"] = routing["rule-providers"];
  config.rules = routing.rules;
  config["proxy-providers"] = providers;
  config.proxies = valid.map(p => ({...p, udp: __UDP__}));
  config.profile = {...config.profile, "store-selected": true};
  return config;
}

