# 公共规则来源

原始脚本定义的 19 个 URL 保留于 `src/rule-providers.yaml`。
`dist/upstream` 保存构建时取得的原文，`dist/rules` 为这些原文的格式转换；
SHA-256 见 `dist/manifest.json`。本项目不把这些第三方规则声明为自有规则。

- [Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules)：13 个规则集，
  [上游 GPL-3.0 许可证](https://github.com/Loyalsoldier/clash-rules/blob/master/LICENSE)，完整原文保存在 `licenses/`。
- [MetaCubeX/meta-rules-dat](https://github.com/MetaCubeX/meta-rules-dat)：6 个规则集，
  [上游 GPL-3.0 许可证](https://github.com/MetaCubeX/meta-rules-dat/blob/master/LICENSE)，完整原文保存在 `licenses/`。
- [LOWERTOP/Shadowrocket](https://github.com/LOWERTOP/Shadowrocket)：手册与配置语法核实参考；
  未复制其整套配置、DNS 设置或业务规则。

重新分发转换规则时应同时保留来源、上游授权及其要求的许可证文件。
构建过程保持规则内容和每条规则的来源对应，不混入机场订阅或节点凭证。
