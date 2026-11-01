# 验证结果

完成于 2026-11-01，北京时间。对应 build：`c4446f9798c2f655`。

## 已实际执行

| 检查 | 结果 |
|---|---|
| Python unittest | 32 项通过 |
| 两份原脚本数据快照比较 | 完全一致 |
| 初次迁移基准 | 15 条个人规则、24 个组、19 个 Provider、41 条规则逐字段一致 |
| 两客户端 JS | Node 24 语法检查及 main 调用通过，输出一致 |
| DNS/IPv6 | 原对象保留；无输入时不新增；DNS 对象身份未改变 |
| 个人规则修改 | 仅修改 user-rules 源即可把 GitHub 目标切换到日本，其他规则保持顺序 |
| 地区扩展 | 一个地区源定义即可扩展模式组、业务组及其他地区排除逻辑 |
| 分层选择 | 14 个软件默认跟随 3 个大类；3 个公司组直接跟随模式选择；均可独立覆盖 |
| 地区自动选择 | 七个地区各一个 url-test 组；需要固定节点时通过手动选择组 |
| 节点过滤 | 地区关键词、其他地区及流量/到期假节点的跨格式成员测试通过 |
| 规则对照 | GitHub、YouTube、Netflix、Disney+、TikTok、Facebook、Instagram、Reddit、Discord、X、Grok、Gemini、Claude、Telegram 域名/IP、Apple、Microsoft、Google、个人规则及兜底通过 |
| 公共规则转换 | 28 份公共源逐项计数核对，Netflix、Disney 的一对多展开单独计数；已知 iOS 差异有显式报告 |
| 构建失败保护 | 下载失败、临时产物校验失败保留原 dist；替换失败可恢复，即使恢复也失败，旧产物仍完整保存在备份目录 |
| Windows 同步保护 | 哈希/配置检查失败不覆盖；正常更新备份；相同内容不重写 |
| 发布逻辑 | 本地 bare Git 仓库测试首次发布、重复发布、旧快照保留通过 |

命令：

```text
python scripts/build.py
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/verify_mihomo.py --core .cache/mihomo.exe
```

Python 3.12、Node v24.19.0、PyYAML 6.0.3。
Windows 环境已使用 UTF-8 模式运行；原始文件和新源均为 UTF-8。

## 真实 Mihomo 内核

实际执行官方 `Mihomo Meta v1.19.33 windows amd64`，下载包按官方发布 SHA-256 校验：
`7aaf636a4f2172dcd8ec34ac4f52797b059195e5afd6409508c963e545f8864d`。

三类配置均先通过 `mihomo -t`，再启动临时回环控制器读取 `/proxies`，检查实际成员：

| 节点来源 | 配置解析 | 动态组成员 |
|---|---|---|
| 内联代理节点 | 通过 | 通过 |
| 只有 inline Proxy Provider | 通过 | 通过 |
| 内联节点＋Provider 混合 | 通过 | 通过 |

使用与生产相同的生成 JS、36 个组、49 条规则及 28 份公共规则快照。
Provider 的在线下载行为不在该测试范围内，公共规则已预置到内核缓存路径；机场 Provider 使用本地 inline 测试数据。
通过回环 API 实际修改选择并读取运行中的 now 链，已确认：

- YouTube → 国外媒体 → 模式选择 → 美国 → 美国03。
- 国外媒体改为美国，YouTube 单独选日本，Netflix 继续跟随国外媒体。
- AI 服务选美国，Gemini 单独选日本，OpenAI 继续跟随 AI 服务。
- YouTube 重新选择国外媒体后恢复跟随。

测速节点为回环虚拟节点，未连接真实机场。原始结果保存在 `docs/mihomo-validation.json`。

## Shadowrocket 静态检查

已检查节结构、36 个组、组引用、默认父组选项、正则在测试解释器中的成员、15 条个人规则原文和顺序、
RULE-SET 资源路径、no-resolve、IPv6 类型、GEOIP LAN 转换和最终 FINAL。
General 仅允许 update-url，因此不会生成 DNS 或其他网络覆写。

当前快照有 98 条公共进程规则不适用于 iOS，以及 1 条 OpenAI DOMAIN-REGEX 的明确近似转换。
Netflix 四条正则展开为八条通配符，Disney 一条正则精确展开为八个域名，Google 两条冗余正则由原列表已有的域名后缀覆盖，并有独立样例测试。
列表及说明见 `dist/compatibility.json`，没有把未转换项目当作等价通过。

正则对照使用 Python 测试解释器，格式依据手册作者示例；没有调用 Shadowrocket 私有解析器。
跨格式路由对照是指定域名/IP 样例的模拟，不是 iOS 运行中的网络抓包。

## 尚待实机与外部环境验证

- 未在真实 Clash Verge Rev、FlClash、Shadowrocket UI 导入及测试出口流量。
- FlClash URL 脚本和自动更新经过 v0.9.2 源码核实，未在 Android 后台省电环境中持续观测。
- Shadowrocket 编译后的实际优先级、节点库作用范围、空组、自动测速和后台更新未实测。
- GitHub Actions 配置已做 YAML 结构检查，发布程序在本地 Git 远端测试过；托管运行结果以 [Actions 记录](https://github.com/jay-183/mihomo-unified-routing/actions) 为准。
- 仓库为 jay-183/mihomo-unified-routing，产物已使用实际发布 URL；未改动用户现有客户端文件。

实机步骤见 `docs/manual-checks.md`。本地测试通过不代表这几项已经完成。
