# 原始脚本分析与统一架构

分析对象为本目录的两份原文件，均以 UTF-8 读取并在无网络能力的 Node VM 中提取常量。
它们继续作为测试输入；生成器只读取 `src/`，不执行原始脚本。

## 相同点和差异

| 项目 | Clash Verge 原始版 | FlClash 安卓版 | 统一实现 |
|---|---|---|---|
| 15 条有效个人规则及顺序 | 相同 | 相同 | 全部保留，`src/user-rules.yaml` |
| 26 条后续规则及顺序 | 相同 | 相同 | 全部保留，`src/rules.yaml` |
| 24 个策略组及引用 | 相同 | 相同 | 统一展开，逐字段回归比较 |
| 六个地区正则、其他地区补集 | 相同 | 相同 | 原式保留 |
| 19 个公共 Provider | 相同 | 相同 | 原 URL/behavior/path/interval 保留 |
| DNS 定义 | 存在并无条件注入 | 同一组配置，默认开关 false | 从生成路径完全移除 |
| DNS 监听 | `0.0.0.0:1053` | `127.0.0.1:1053` | 不生成监听配置 |
| 顶层 IPv6 | 强制 false | 强制 false | 沿用输入配置，不再强制 |
| 静态节点 UDP | true | true | 保留 |
| 原订阅 Provider | 保留 | 保留 | 原样保留，兼容 Provider-only |

安卓文件没有额外的地区分组或业务补丁；其实际可运行经验说明 `main(config)` 与原组结构可用于安卓，
不能据此推定任意版本都有远程脚本自动更新。更新能力另行按源码核实。

移除的变量包括 `domesticNameservers`、`foreignNameservers`、`dnsConfig`、`APPLY_CUSTOM_DNS`，
以及监听、缓存、Fake-IP、DNS Policy、DNS IPv6 等注入逻辑。
原文件保留为历史输入不代表继续启用其中 DNS。

## 完整功能清单

基础选择：🔰 模式选择、🖐 手动选择、♻️ 自动选择、🚑 故障转移、⚖️ 负载均衡。
地区：🇭🇰 香港、🇹🇼 台湾、🇯🇵 日本、🇸🇬 新加坡、🇺🇸 美国、🌍 欧洲、🌐 其他地区。
业务：🤖 OpenAI、✨ Gemini、🧠 其他 AI、📲 Telegram、📢 谷歌服务、🍎 苹果服务、Ⓜ️ 微软服务。
其他：🥰 广告过滤、🔗 全局直连、🐬 自定义直连、🐳 自定义代理、🐟 漏网之鱼。

手动/自动/地区/故障转移/负载均衡动态引用全部节点源并过滤假节点。业务组只引用上层组。
苹果、微软默认引用全局直连；广告默认 REJECT；模式默认手动；这些原始选项顺序保持不变。
测速地址为 `https://www.gstatic.com/generate_204`，间隔 300 秒，超时 5000 毫秒，
测速容差 50，lazy=true，max-failed-times=3，负载均衡采用 consistent-hashing。

Provider 清单：reject、icloud、apple、google、proxy、direct、private、gfw、tld-not-cn、
applications、telegramcidr、cncidr、lancidr、openai、anthropic、google-gemini、xai、perplexity、microsoft。
前 13 个来自 Loyalsoldier，后 6 个来自 MetaCubeX。所有周期为 86400 秒。

## 原始优先级及覆盖点

精确顺序为：15 条个人规则 → 4 条显式域名规则 → 5 个 AI 集 → applications/private/reject →
microsoft/icloud/apple/google → proxy/gfw/tld-not-cn → direct/lancidr/cncidr → telegramcidr →
GEOIP LAN → GEOIP CN → MATCH。没有按需求说明中的概括顺序重排。

- `DOMAIN-KEYWORD,github` 在前，`DOMAIN-SUFFIX,github.io` 在后，所以 github.io 实际命中个人自定义代理。
- applications 在广告之前；Mihomo 中匹配到这些进程时，会先进入全局直连。这是原始行为，iOS 无此进程匹配。
- 通用代理规则位于国内直连之前，重叠时首先命中的代理规则获胜。
- Microsoft、iCloud、Google 等专用服务先于通用代理，因此公共列表之间的重叠不会抹去业务组目标。
- Telegram IP 列表在国内 CIDR 之后；IP 交集如出现，先采用国内直连。这一顺序继续保留。
- `GEOIP LAN` 位于 lancidr 之后并非完全冗余：它有 Mihomo 自身对私有、回环、多播、链路本地地址的判断。
- 原地区正则是宽松的子串匹配，例如 `US` 可命中名称里的 `us`。节点可能同时匹配多个地区，
  仅“其他地区”是已知地区的补集；不擅自把六个正则改成互斥分类。

本次公共快照包含 348899 条条目。对完全相同的匹配条件做交集检查，发现 1334 次不同策略目标的重叠，
主要包括 microsoft→proxy 545、reject→direct 262、reject→proxy 118、proxy→direct 109、
microsoft→direct 89、icloud→proxy 44。箭头左边的规则集优先。
这只是相同条件的检查，不是对所有域名父子关系、通配符、正则、进程和 IP 交集的完备证明；
每日上游更新后交集数量可能变化。所有发现均保留原先的先匹配行为。

## 架构取舍

Windows/Android 输出同步的 JS，直接变换客户端选中的订阅，避免在 GitHub 公开配置内绑定机场 URL。
内联节点和 Provider 均由 Mihomo 的 include-all 动态引入；Mihomo RE2 的“其他地区”用 exclude-filter，
不加入 RE2 不支持的负向前瞻。
[Mihomo 官方组字段说明](https://wiki.metacubex.one/config/proxy-groups/)

iOS 输出原生 `.conf`，正则过滤首页节点；排除条件使用该客户端示例支持的前瞻表达式。
其公共规则由同一份 Mihomo 上游原文转换为 policy-free `.list`，每个 RULE-SET 仍保留原来的目标及原位置。
个人规则直接写入完整 `[Rule]`，没有误用一个目标固定的 Rule Provider 来承载不同目标的个人规则。

没有采用公开的“完整 Mihomo 配置＋固定机场 Provider URL”：它无法自动拿到客户端另一个订阅中的私有节点。
也没有引入在线订阅转换服务。原生脚本正好满足机场独立这一最高优先目标。

## 技术核实记录

核实发生于 2026-10-30 至 2026-10-31，北京时间。

| 组件 | 核实对象 | 结论与证据 |
|---|---|---|
| Mihomo | v1.19.33 官方内核、官方文档 | include-all 与 exclude-filter；真实内核检查通过 |
| Clash Verge Rev | v2.5.8 发布、dev 提交 `c236f5094e0608b7be82f62350a4ef397dc062ae` | 全局本地 main 脚本；远程订阅更新不能当作本地脚本更新 |
| FlClash | v0.9.2；提交 `7fd417fb9a9a277c6a9339a8ac87f907df7c25f7` | URL 脚本、资源自动更新、当前脚本更新后的重新应用 |
| Shadowrocket | App Store 2.2.93、社区手册/示例 | 原生组类型、正则、规则集、FINAL；无公开内核执行认证 |

FlClash 关键代码：[资源自动更新](https://github.com/chen08209/FlClash/blob/7fd417fb9a9a277c6a9339a8ac87f907df7c25f7/lib/providers/actions/resources.dart)、
[启动及约 20 分钟检查](https://github.com/chen08209/FlClash/blob/7fd417fb9a9a277c6a9339a8ac87f907df7c25f7/lib/application.dart)、
[脚本更新后重载](https://github.com/chen08209/FlClash/blob/7fd417fb9a9a277c6a9339a8ac87f907df7c25f7/lib/providers/actions/scripts.dart)。

Clash Verge Rev 关键代码：[配置类型及本地 JS 文件](https://github.com/clash-verge-rev/clash-verge-rev/blob/c236f5094e0608b7be82f62350a4ef397dc062ae/src-tauri/src/config/prfitem.rs)、
[官方扩展说明](https://www.clashverge.dev/guide/extend.html)。

Shadowrocket：[开发者 App Store 页面](https://apps.apple.com/us/app/shadowrocket/id932747118)、
[手册作者的配置示例](https://github.com/LOWERTOP/Shadowrocket/blob/main/lazy_group.conf)。
后者是社区参考资料，不冒充软件官方解析器或实机证明。
