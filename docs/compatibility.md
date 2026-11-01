# 三平台兼容性

“保留”指生成器的数据和格式；只有 Mihomo 标记的项目经过本地真实内核执行。
客户端 UI、后台任务、真实网络出口均需实机确认。

| 功能 | Clash Verge Rev | FlClash v0.9.2 | Shadowrocket 2.2.93 对应格式 |
|---|---|---|---|
| 独立机场管理 | 当前订阅提供节点；全局脚本 | 当前订阅提供节点；每个新订阅关联脚本 | 首页订阅与分流配置独立；正则组取已导入节点，需实机确认作用范围 |
| 内联/Provider | 两者及混合均通过内核测试 | 相同 JS/内核数据 | 不使用 Mihomo Proxy Provider；使用原生节点库 |
| 手动/自动/故障转移 | 原类型保留 | 原类型保留 | select/url-test/fallback；行为需 iOS 验证 |
| 负载均衡 | consistent-hashing | consistent-hashing | load-balance 同域名粘性；不保证同一哈希算法、相同节点或故障时序 |
| 七个地区自动测速组 | url-test；include-all/filter/exclude-filter | 相同 | url-test，policy-regex-filter 正向与负向前瞻 |
| 美国专用策略 | fallback 与 consistent-hashing 负载均衡，共用美国地区过滤条件 | 相同，实际成员已验证 | fallback/load-balance，沿用同一美国节点正则，需实机确认 |
| 自动测速 | 300 秒、5000 毫秒超时、容差 50 | 相同 | 300 秒、5 秒超时、容差 50；计时实现可能不同 |
| lazy/max-failed-times | true/3 | true/3 | 无已核实的直接对应参数，未输出猜测参数 |
| 业务嵌套 | 14 个软件跟随 3 个大类，Google 跟随默认线路，Apple/Microsoft 跟随直连模式；支持独立覆盖 | 相同，已通过 Mihomo API 选择验证 | select 嵌套组引用及 policy-select-name 默认值；自动组只包含节点，需实机确认 |
| 15 条个人规则 | 保持源文件顺序和目标，GitHub 指向自定义代理 | 相同 | 当前规则原文和顺序保留；新增 IPv6 类型按原生语法转换 |
| no-resolve | 保留 | 保留 | 保留；是否已有解析结果取决于客户端 |
| 公共 domain/ipcidr/classical | 上游 URL 与 86400 秒周期 | 相同 | 同一次快照转换，28 份来源均有记录 |
| applications 进程规则 | 保留 | 保留；进程识别取决于设备权限/内核 | 98 条不适用，逐条列在 compatibility.json，后续规则继续匹配 |
| OpenAI DOMAIN-REGEX | 原正则保留 | 原正则保留 | 一条已知规则用通配符近似，下面说明扩大范围 |
| 最终兜底 | MATCH | MATCH | FINAL |
| GEOIP LAN | 原生判断 | 原生判断 | 按 Mihomo isLan 定义展开 12 段；不依赖猜测的 SR LAN 数据库 |
| GEOIP CN | 使用客户端本地库 | 使用客户端本地库 | 使用客户端本地库，库版本不同可造成边界差异 |
| DNS | 传入对象原样保留，无输入时不新增 | 相同 | 无 dns-server/Host/IPv6 覆写；替换整配置的继承见 README |
| 完整配置更新 | 本地全局脚本；同步工具＋重新应用 | URL 脚本，资源自动更新开关＋到期间隔 | update-url；系统后台限制；使用/编译确认 |

## 明确的 iOS 差异

OpenAI 上游的一条规则为：

```text
DOMAIN-REGEX,^chatgpt-async-webps-prod-\S+-\d+\.webpubsub\.azure\.com$
```

iOS 未核实支持 DOMAIN-REGEX；URL-REGEX 匹配对象不同，不拿它冒充域名正则。已知这条改为：

```text
DOMAIN-WILDCARD,chatgpt-async-webps-prod-*-*.webpubsub.azure.com
```

该式包含原来的正常主机名，但数字字段也允许非数字字符。因此可能让少量额外的同前缀 Azure 主机进入 OpenAI 组。
对应关系及限制在 `dist/compatibility.json` 中公开，测试同时覆盖原式命中和扩大范围。

Netflix 的四条 `(^|\.)前缀.+\.amazonaws\.com$` 正则各展开为根域名、子域名两条通配符，
其中 `?*` 保留至少一个字符的条件。Google 两条视频域名正则已被同一列表现有的 DOMAIN-SUFFIX 覆盖，
仅在该后缀仍存在时才允许替换为对应后缀规则；后缀移除后构建会停止。完整映射随兼容报告发布。
Disney 的 `^hses[1-7]?\.akamaized\.net$` 正则精确展开为 hses、hses1 至 hses7 共八个域名。
以上转换已做样例对照，Shadowrocket 的通配符运行行为仍需实机验收。
任何新出现的 DOMAIN-REGEX 或其他未适配类型都会停止构建，不做自动近似。

个人进程规则不允许添加后悄悄丢弃：例如加入 `PROCESS-NAME` 会明确构建失败。
公共 applications 则作为已知平台差异逐条报告，Windows/Android 的进程规则保持完整。

生成 `[Rule]` 按原始顺序排列。Shadowrocket 的配置编译可能把显式域名类规则优先、GEOIP 后置；
不能保证其运行顺序与 Mihomo 逐条判定完全一样，尤其是靠前的个人 IP 规则与靠后的域名规则发生交叉时。
本项目没有为了掩盖差异重排源文件；必须在实机的“测试规则”和连接日志里核实。
[手册作者关于编译优先级的说明](https://github.com/LOWERTOP/Shadowrocket#规则优先级)

Mihomo 的空地区组在本次实核中回退为 COMPATIBLE，可能直连，这是原脚本的默认行为。
缺少所需地区节点时先在手动组确认，不应把空组当成可用的地区出口。
Shadowrocket 的空组行为未实测，不承诺与之相同。

域名是否能还原、no-resolve 是否跳过、Fake-IP 映射是否可用，取决于客户端当前的 DNS 与流量入口设置。
生成器不通过增加 DNS 覆写消除这些差异。需要比较运行行为时，请检查客户端自己的解析结果和连接日志。

## 更新与节点管理限制

- Windows 的机场自动刷新和脚本更新是两条路径；外部同步后的磁盘文件必须再被客户端应用。
- Android 的自动脚本更新已按 v0.9.2 源码核实，默认资源自动更新开关为关闭，间隔为 24 小时。
  进程必须有机会运行；启动时及约 20 分钟一次的检查不等于系统后台定时唤醒保证。
- iOS 配置更新、远程规则下载、编译配置、订阅更新分别检查。系统调度不保证即时更新。
- 不同机场可能出现节点重名；内联名称冲突会在脚本里报错，Provider 节点的冲突由内核处理。
  更换机场后应确认节点唯一性和地区匹配，规则源不需要填写机场凭证。
- 用生成的正则组引用 iOS 已导入节点的格式来自作者示例；若实机要求开启订阅筛选，
  需在本地组关联订阅，新机场也应检查关联。该项仍列为实机验收，不声称全版本零操作。
