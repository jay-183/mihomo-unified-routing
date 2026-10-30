/**
 * FlClash Android - 单订阅统一规则脚本覆写（从 Clash Verge Rev 适配）
 * 版本：区域自动选择精简版
 *
 * 设计目标：
 * 1. 平时只启用一个订阅，当前订阅只提供节点。
 * 2. OpenAI / Gemini / 其他 AI / Google / Telegram / Microsoft 等业务分组中，不直接展示所有节点。
 * 3. 业务分组只展示：模式选择、手动选择、自动选择、各地区节点组。
 * 4. 各地区节点组内部自动测速，自动选择该地区最快节点。
 * 5. 只有进入“🖐 手动选择”时才直接看到具体节点。
 * 6. 自动过滤“剩余流量 / 套餐到期 / 重置”等订阅信息节点。
 */


/* ============================================================
 * 【用户通常只需要修改这里】
 * ============================================================ */

// 自定义规则：需要时取消注释或自行增加。
const USER_RULES = [
  // "DOMAIN-SUFFIX,example.com,🐳 自定义代理",
  // "DOMAIN-SUFFIX,example.cn,🐬 自定义直连",
  "DOMAIN-KEYWORD,dnscheck.tools,🐳 自定义代理",
  "DOMAIN-KEYWORD,ip.net.coffee,🐳 自定义代理",
  "DOMAIN-KEYWORD,github,🐳 自定义代理",
  "DOMAIN-KEYWORD,9kqz23b19z,🐳 自定义代理",
  "DOMAIN-KEYWORD,ippure,🖐 手动选择",
  "DOMAIN-KEYWORD,todetect,🐳 自定义代理",
  "DOMAIN-KEYWORD,biu.moe,🐬 自定义直连",
  "DOMAIN-KEYWORD,joox,🇭🇰 香港",
  "DOMAIN-KEYWORD,music-api.gdstudio.xyz,🐬 自定义直连",
  "DOMAIN-KEYWORD,dglab.xiaoyudi,🐬 自定义直连",
  "DOMAIN-KEYWORD,blinkroom,🐬 自定义直连",
  "DOMAIN-KEYWORD,dglabplay,🐬 自定义直连",
  "IP-CIDR,18.162.180.119/32,🐬 自定义直连,no-resolve",
  "DOMAIN-KEYWORD,clerk,🐬 自定义直连",
  "DOMAIN-KEYWORD,dghub.top,🐬 自定义直连",
  //"DOMAIN-KEYWORD,1panel,🔰 模式选择",

];

// 测速地址，一般不需要修改。
const TEST_URL = "https://www.gstatic.com/generate_204";

// 安卓适配：默认沿用 FlClash/当前订阅的 DNS 设置。
// 如确实需要与电脑版完全一致的自定义 DNS，可改为 true。
const APPLY_CUSTOM_DNS = false;

// 统一过滤订阅信息类“假节点”。
// 只要节点名称包含以下关键词，就不会进入手动/自动/地区/故障转移等节点组。
const NODE_EXCLUDE_FILTER =
  "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset";

// 各地区节点名称匹配。
// 如果你的机场节点命名比较特殊，只需要改这里对应地区的正则。
const REGION_FILTERS = {
  HK: "(?i)香港|港|HK|Hong Kong|HongKong",
  TW: "(?i)台湾|台北|新北|TW|Taiwan",
  JP: "(?i)日本|东京|大阪|JP|Japan|Tokyo|Osaka",
  SG: "(?i)新加坡|狮城|SG|Singapore",
  US: "(?i)美国|洛杉矶|圣何塞|西雅图|纽约|达拉斯|芝加哥|US|USA|United States|Los Angeles|San Jose|Seattle|New York|Dallas|Chicago",
  EU: "(?i)欧洲|EU|Europe|英国|伦敦|UK|United Kingdom|London|法国|France|巴黎|Paris|德国|Germany|法兰克福|Frankfurt|荷兰|Netherlands|阿姆斯特丹|Amsterdam|瑞士|Switzerland|西班牙|Spain|意大利|Italy|波兰|Poland|芬兰|Finland|瑞典|Sweden|挪威|Norway",
};


/* ========================= DNS ========================= */

const domesticNameservers = [
  "https://223.5.5.5/dns-query",
  "https://doh.pub/dns-query",
];

const foreignNameservers = [
  "https://cloudflare-dns.com/dns-query",
  "https://9.9.9.9/dns-query",
  "https://77.88.8.8/dns-query",
];

const dnsConfig = {
  enable: true,
  ipv6: false,
  listen: "127.0.0.1:1053",
  "prefer-h3": false,
  "respect-rules": true,
  "use-system-hosts": false,
  "cache-algorithm": "arc",
  "enhanced-mode": "fake-ip",
  "fake-ip-range": "198.18.0.1/16",

  "fake-ip-filter": [
    "+.lan",
    "+.local",
    "+.ts.net",
    "+.msftconnecttest.com",
    "+.msftncsi.com",
    "localhost.ptlogin2.qq.com",
    "localhost.sec.qq.com",
    "localhost.work.weixin.qq.com",
  ],

  "default-nameserver": [
    "223.5.5.5",
    "1.2.4.8",
  ],

  nameserver: foreignNameservers,
  "proxy-server-nameserver": domesticNameservers,
  "direct-nameserver": domesticNameservers,
  "direct-nameserver-follow-policy": false,

  "nameserver-policy": {
    "geosite:cn": domesticNameservers,
    "+.ts.net": "100.100.100.100",
  },
};


/* ========================= Rule Providers ========================= */

const commonDomainProvider = {
  type: "http",
  behavior: "domain",
  format: "yaml",
  interval: 86400,
};

const commonClassicalProvider = {
  type: "http",
  behavior: "classical",
  format: "yaml",
  interval: 86400,
};

const commonIPProvider = {
  type: "http",
  behavior: "ipcidr",
  format: "yaml",
  interval: 86400,
};

const ruleProviders = {
  reject: {
    ...commonDomainProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt",
    path: "./ruleset/loyalsoldier/reject.yaml",
  },

  icloud: {
    ...commonDomainProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/icloud.txt",
    path: "./ruleset/loyalsoldier/icloud.yaml",
  },

  apple: {
    ...commonDomainProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/apple.txt",
    path: "./ruleset/loyalsoldier/apple.yaml",
  },

  google: {
    ...commonDomainProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/google.txt",
    path: "./ruleset/loyalsoldier/google.yaml",
  },

  proxy: {
    ...commonDomainProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/proxy.txt",
    path: "./ruleset/loyalsoldier/proxy.yaml",
  },

  direct: {
    ...commonDomainProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt",
    path: "./ruleset/loyalsoldier/direct.yaml",
  },

  private: {
    ...commonDomainProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt",
    path: "./ruleset/loyalsoldier/private.yaml",
  },

  gfw: {
    ...commonDomainProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/gfw.txt",
    path: "./ruleset/loyalsoldier/gfw.yaml",
  },

  "tld-not-cn": {
    ...commonDomainProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/tld-not-cn.txt",
    path: "./ruleset/loyalsoldier/tld-not-cn.yaml",
  },

  applications: {
    ...commonClassicalProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/applications.txt",
    path: "./ruleset/loyalsoldier/applications.yaml",
  },

  telegramcidr: {
    ...commonIPProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt",
    path: "./ruleset/loyalsoldier/telegramcidr.yaml",
  },

  cncidr: {
    ...commonIPProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/cncidr.txt",
    path: "./ruleset/loyalsoldier/cncidr.yaml",
  },

  lancidr: {
    ...commonIPProvider,
    url: "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/lancidr.txt",
    path: "./ruleset/loyalsoldier/lancidr.yaml",
  },

  openai: {
    ...commonClassicalProvider,
    url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/openai.yaml",
    path: "./ruleset/MetaCubeX/openai.yaml",
  },

  anthropic: {
    ...commonClassicalProvider,
    url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/anthropic.yaml",
    path: "./ruleset/MetaCubeX/anthropic.yaml",
  },

  "google-gemini": {
    ...commonClassicalProvider,
    url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/google-gemini.yaml",
    path: "./ruleset/MetaCubeX/google-gemini.yaml",
  },

  xai: {
    ...commonClassicalProvider,
    url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/xai.yaml",
    path: "./ruleset/MetaCubeX/xai.yaml",
  },

  perplexity: {
    ...commonClassicalProvider,
    url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/perplexity.yaml",
    path: "./ruleset/MetaCubeX/perplexity.yaml",
  },

  microsoft: {
    ...commonClassicalProvider,
    url: "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/microsoft.yaml",
    path: "./ruleset/MetaCubeX/microsoft.yaml",
  },
};


/* ========================= Rules ========================= */

const rules = [
  ...USER_RULES,

  "DOMAIN-SUFFIX,googleapis.cn,📢 谷歌服务",
  "DOMAIN-SUFFIX,gstatic.com,📢 谷歌服务",
  "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,📢 谷歌服务",
  "DOMAIN-SUFFIX,github.io,🔰 模式选择",

  // AI
  "RULE-SET,openai,🤖 OpenAI",
  "RULE-SET,google-gemini,✨ Gemini",
  "RULE-SET,anthropic,🧠 其他 AI",
  "RULE-SET,xai,🧠 其他 AI",
  "RULE-SET,perplexity,🧠 其他 AI",

  // 本机 / 私有网络 / 广告
  "RULE-SET,applications,🔗 全局直连",
  "RULE-SET,private,🔗 全局直连",
  "RULE-SET,reject,🥰 广告过滤",

  // 常用服务
  "RULE-SET,microsoft,Ⓜ️ 微软服务",
  "RULE-SET,icloud,🍎 苹果服务",
  "RULE-SET,apple,🍎 苹果服务",
  "RULE-SET,google,📢 谷歌服务",

  // 常见代理规则
  "RULE-SET,proxy,🔰 模式选择",
  "RULE-SET,gfw,🔰 模式选择",
  "RULE-SET,tld-not-cn,🔰 模式选择",

  // 国内直连
  "RULE-SET,direct,🔗 全局直连",
  "RULE-SET,lancidr,🔗 全局直连,no-resolve",
  "RULE-SET,cncidr,🔗 全局直连,no-resolve",

  // Telegram
  "RULE-SET,telegramcidr,📲 Telegram,no-resolve",

  // 兜底
  "GEOIP,LAN,🔗 全局直连,no-resolve",
  "GEOIP,CN,🔗 全局直连,no-resolve",
  "MATCH,🐟 漏网之鱼",
];


/* ========================= Proxy Groups ========================= */

const groupBase = {
  interval: 300,
  timeout: 5000,
  url: TEST_URL,
  lazy: true,
  "max-failed-times": 3,
  hidden: false,
};

// 业务分组统一只展示这些策略组，不直接把所有节点塞进去。
const SERVICE_GROUP_OPTIONS = [
  "🔰 模式选择",
  "🖐 手动选择",
  "♻️ 自动选择",
  "🇭🇰 香港",
  "🇹🇼 台湾",
  "🇯🇵 日本",
  "🇸🇬 新加坡",
  "🇺🇸 美国",
  "🌍 欧洲",
  "🌐 其他地区",
];

// 创建“地区内自动选择”组。
function regionGroup(name, filter) {
  return {
    ...groupBase,
    name,
    type: "url-test",
    tolerance: 50,
    "include-all": true,
    filter,
    "exclude-filter": NODE_EXCLUDE_FILTER,
  };
}

// “其他地区” = 排除订阅信息节点 + 排除已识别的地区节点。
// Mihomo 使用 RE2，不适合写负向前瞻，所以用 exclude-filter 实现。
const KNOWN_REGION_FILTER = [
  REGION_FILTERS.HK,
  REGION_FILTERS.TW,
  REGION_FILTERS.JP,
  REGION_FILTERS.SG,
  REGION_FILTERS.US,
  REGION_FILTERS.EU,
]
  .map((item) => item.replace(/^\(\?i\)/, ""))
  .join("|");

const OTHER_REGION_EXCLUDE_FILTER =
  `(?i)${NODE_EXCLUDE_FILTER.replace(/^\(\?i\)/, "")}|${KNOWN_REGION_FILTER}`;

function otherRegionGroup() {
  return {
    ...groupBase,
    name: "🌐 其他地区",
    type: "url-test",
    tolerance: 50,
    "include-all": true,
    "exclude-filter": OTHER_REGION_EXCLUDE_FILTER,
  };
}

const proxyGroups = [
  /* ========================================================
   * 1. 基础选择：永远放最前面
   * ======================================================== */

  {
    ...groupBase,
    name: "🔰 模式选择",
    type: "select",
    proxies: [
      "🖐 手动选择",
      "♻️ 自动选择",
      "🇭🇰 香港",
      "🇹🇼 台湾",
      "🇯🇵 日本",
      "🇸🇬 新加坡",
      "🇺🇸 美国",
      "🌍 欧洲",
      "🌐 其他地区",
      "🚑 故障转移",
      "⚖️ 负载均衡",
      "DIRECT",
    ],
  },

  // 原“节点选择”改名为“手动选择”。
  // 只有进入这个组时才直接看到具体节点。
  {
    ...groupBase,
    name: "🖐 手动选择",
    type: "select",
    "include-all": true,
    "exclude-filter": NODE_EXCLUDE_FILTER,
  },

  // 所有有效节点自动测速选择。
  {
    ...groupBase,
    name: "♻️ 自动选择",
    type: "url-test",
    tolerance: 50,
    "include-all": true,
    "exclude-filter": NODE_EXCLUDE_FILTER,
  },


  /* ========================================================
   * 2. 服务分流
   * 业务组内部只显示：模式 / 手动 / 自动 / 地区
   * 不直接显示具体节点。
   * ======================================================== */

  {
    name: "🤖 OpenAI",
    type: "select",
    proxies: SERVICE_GROUP_OPTIONS,
  },

  {
    name: "✨ Gemini",
    type: "select",
    proxies: SERVICE_GROUP_OPTIONS,
  },

  {
    name: "🧠 其他 AI",
    type: "select",
    proxies: SERVICE_GROUP_OPTIONS,
  },

  {
    name: "📲 Telegram",
    type: "select",
    proxies: SERVICE_GROUP_OPTIONS,
  },

  {
    name: "📢 谷歌服务",
    type: "select",
    proxies: SERVICE_GROUP_OPTIONS,
  },

  {
    name: "🍎 苹果服务",
    type: "select",
    proxies: [
      "🔗 全局直连",
      ...SERVICE_GROUP_OPTIONS,
    ],
  },

  {
    name: "Ⓜ️ 微软服务",
    type: "select",
    proxies: [
      "🔗 全局直连",
      ...SERVICE_GROUP_OPTIONS,
    ],
  },


  /* ========================================================
   * 3. 地区组
   * 每个地区内部自动测速，自动选最快节点。
   * ======================================================== */

  regionGroup("🇭🇰 香港", REGION_FILTERS.HK),
  regionGroup("🇹🇼 台湾", REGION_FILTERS.TW),
  regionGroup("🇯🇵 日本", REGION_FILTERS.JP),
  regionGroup("🇸🇬 新加坡", REGION_FILTERS.SG),
  regionGroup("🇺🇸 美国", REGION_FILTERS.US),
  regionGroup("🌍 欧洲", REGION_FILTERS.EU),

  // 没有匹配到以上地区的有效节点自动进入这里。
  otherRegionGroup(),


  /* ========================================================
   * 4. 其他功能：统一放最后
   * ======================================================== */

  {
    ...groupBase,
    name: "🚑 故障转移",
    type: "fallback",
    "include-all": true,
    "exclude-filter": NODE_EXCLUDE_FILTER,
  },

  {
    ...groupBase,
    name: "⚖️ 负载均衡",
    type: "load-balance",
    strategy: "consistent-hashing",
    "include-all": true,
    "exclude-filter": NODE_EXCLUDE_FILTER,
  },

  {
    name: "🥰 广告过滤",
    type: "select",
    proxies: ["REJECT", "DIRECT"],
  },

  {
    name: "🔗 全局直连",
    type: "select",
    proxies: [
      "DIRECT",
      "🔰 模式选择",
    ],
  },

  {
    name: "🐬 自定义直连",
    type: "select",
    proxies: [
      "🔗 全局直连",
      "🔰 模式选择",
    ],
  },

  {
    name: "🐳 自定义代理",
    type: "select",
    proxies: SERVICE_GROUP_OPTIONS,
  },

  {
    name: "🐟 漏网之鱼",
    type: "select",
    proxies: [
      ...SERVICE_GROUP_OPTIONS,
      "DIRECT",
    ],
  },
];


/* ========================= Main ========================= */

function main(config) {
  const originalProxies = Array.isArray(config?.proxies)
    ? config.proxies
    : [];

  const originalProviders =
    config?.["proxy-providers"] &&
    typeof config["proxy-providers"] === "object"
      ? config["proxy-providers"]
      : {};

  if (
    originalProxies.length === 0 &&
    Object.keys(originalProviders).length === 0
  ) {
    throw new Error("当前订阅中未找到任何代理节点或 proxy-provider。");
  }

  config.ipv6 = false;

  // 统一接管 DNS、规则集、规则和代理组。
  if (APPLY_CUSTOM_DNS) config.dns = dnsConfig;
  config["rule-providers"] = ruleProviders;
  config.rules = rules;
  config["proxy-groups"] = proxyGroups;

  // 保留当前订阅自己的 provider，不额外添加其他订阅。
  config["proxy-providers"] = originalProviders;

  // 保留当前订阅的静态节点，并开启 UDP。
  config.proxies = originalProxies
    .filter((proxy) => proxy && typeof proxy === "object" && proxy.name)
    .map((proxy) => ({
      ...proxy,
      udp: true,
    }));

  return config;
}
