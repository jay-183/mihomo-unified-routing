// Unified routing build: c66d64ab22c1f5eb
// Generated file. Edit src/*.yaml and rebuild.
const ROUTING = {
  "proxy-groups": [
    {
      "name": "默认线路",
      "type": "select",
      "proxies": [
        "美国节点",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "手动选择",
      "type": "select",
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "自动选择",
      "type": "url-test",
      "tolerance": 50,
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset"
    },
    {
      "name": "国外媒体",
      "type": "select",
      "proxies": [
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "AI 服务",
      "type": "select",
      "proxies": [
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "通讯社交",
      "type": "select",
      "proxies": [
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "YouTube",
      "type": "select",
      "proxies": [
        "国外媒体",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Netflix",
      "type": "select",
      "proxies": [
        "国外媒体",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Disney+",
      "type": "select",
      "proxies": [
        "国外媒体",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "TikTok",
      "type": "select",
      "proxies": [
        "国外媒体",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "OpenAI",
      "type": "select",
      "proxies": [
        "AI 服务",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Gemini",
      "type": "select",
      "proxies": [
        "AI 服务",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Claude",
      "type": "select",
      "proxies": [
        "AI 服务",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Grok",
      "type": "select",
      "proxies": [
        "AI 服务",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Telegram",
      "type": "select",
      "proxies": [
        "通讯社交",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Discord",
      "type": "select",
      "proxies": [
        "通讯社交",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "X",
      "type": "select",
      "proxies": [
        "通讯社交",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Facebook",
      "type": "select",
      "proxies": [
        "通讯社交",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Instagram",
      "type": "select",
      "proxies": [
        "通讯社交",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Reddit",
      "type": "select",
      "proxies": [
        "通讯社交",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Google",
      "type": "select",
      "proxies": [
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Apple",
      "type": "select",
      "proxies": [
        "直连模式",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "Microsoft",
      "type": "select",
      "proxies": [
        "直连模式",
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "香港节点",
      "type": "url-test",
      "tolerance": 50,
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset",
      "filter": "(?i)香港|港|HK|Hong Kong|HongKong"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "台湾节点",
      "type": "url-test",
      "tolerance": 50,
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset",
      "filter": "(?i)台湾|台北|新北|TW|Taiwan"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "日本节点",
      "type": "url-test",
      "tolerance": 50,
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset",
      "filter": "(?i)日本|东京|大阪|JP|Japan|Tokyo|Osaka"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "新加坡节点",
      "type": "url-test",
      "tolerance": 50,
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset",
      "filter": "(?i)新加坡|狮城|SG|Singapore"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "美国节点",
      "type": "url-test",
      "tolerance": 50,
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset",
      "filter": "(?i)美国|洛杉矶|圣何塞|西雅图|纽约|达拉斯|芝加哥|US|USA|United States|Los Angeles|San Jose|Seattle|New York|Dallas|Chicago"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "欧洲节点",
      "type": "url-test",
      "tolerance": 50,
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset",
      "filter": "(?i)欧洲|EU|Europe|英国|伦敦|UK|United Kingdom|London|法国|France|巴黎|Paris|德国|Germany|法兰克福|Frankfurt|荷兰|Netherlands|阿姆斯特丹|Amsterdam|瑞士|Switzerland|西班牙|Spain|意大利|Italy|波兰|Poland|芬兰|Finland|瑞典|Sweden|挪威|Norway"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "其他地区节点",
      "type": "url-test",
      "tolerance": 50,
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset|香港|港|HK|Hong Kong|HongKong|台湾|台北|新北|TW|Taiwan|日本|东京|大阪|JP|Japan|Tokyo|Osaka|新加坡|狮城|SG|Singapore|美国|洛杉矶|圣何塞|西雅图|纽约|达拉斯|芝加哥|US|USA|United States|Los Angeles|San Jose|Seattle|New York|Dallas|Chicago|欧洲|EU|Europe|英国|伦敦|UK|United Kingdom|London|法国|France|巴黎|Paris|德国|Germany|法兰克福|Frankfurt|荷兰|Netherlands|阿姆斯特丹|Amsterdam|瑞士|Switzerland|西班牙|Spain|意大利|Italy|波兰|Poland|芬兰|Finland|瑞典|Sweden|挪威|Norway"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "美国故障转移",
      "type": "fallback",
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset",
      "filter": "(?i)美国|洛杉矶|圣何塞|西雅图|纽约|达拉斯|芝加哥|US|USA|United States|Los Angeles|San Jose|Seattle|New York|Dallas|Chicago"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "美国负载均衡",
      "type": "load-balance",
      "strategy": "consistent-hashing",
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset",
      "filter": "(?i)美国|洛杉矶|圣何塞|西雅图|纽约|达拉斯|芝加哥|US|USA|United States|Los Angeles|San Jose|Seattle|New York|Dallas|Chicago"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "故障转移",
      "type": "fallback",
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset"
    },
    {
      "interval": 300,
      "timeout": 5000,
      "url": "https://www.gstatic.com/generate_204",
      "lazy": true,
      "max-failed-times": 3,
      "hidden": false,
      "name": "负载均衡",
      "type": "load-balance",
      "strategy": "consistent-hashing",
      "include-all": true,
      "exclude-filter": "(?i)剩余流量|流量剩余|套餐到期|到期时间|到期|重置时间|重置|traffic|expire|expiry|reset"
    },
    {
      "name": "广告过滤",
      "type": "select",
      "proxies": [
        "REJECT",
        "DIRECT"
      ]
    },
    {
      "name": "直连模式",
      "type": "select",
      "proxies": [
        "DIRECT",
        "默认线路"
      ]
    },
    {
      "name": "自定义代理",
      "type": "select",
      "proxies": [
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    },
    {
      "name": "漏网之鱼",
      "type": "select",
      "proxies": [
        "默认线路",
        "手动选择",
        "自动选择",
        "香港节点",
        "台湾节点",
        "日本节点",
        "新加坡节点",
        "美国节点",
        "欧洲节点",
        "其他地区节点",
        "故障转移",
        "负载均衡",
        "美国故障转移",
        "美国负载均衡",
        "DIRECT"
      ]
    }
  ],
  "rule-providers": {
    "reject": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt",
      "path": "./ruleset/loyalsoldier/reject.yaml"
    },
    "icloud": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/icloud.txt",
      "path": "./ruleset/loyalsoldier/icloud.yaml"
    },
    "apple": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/apple.yaml",
      "path": "./ruleset/MetaCubeX/apple.yaml"
    },
    "google": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/google.yaml",
      "path": "./ruleset/MetaCubeX/google.yaml"
    },
    "proxy": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/proxy.txt",
      "path": "./ruleset/loyalsoldier/proxy.yaml"
    },
    "direct": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/direct.txt",
      "path": "./ruleset/loyalsoldier/direct.yaml"
    },
    "private": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt",
      "path": "./ruleset/loyalsoldier/private.yaml"
    },
    "gfw": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/gfw.txt",
      "path": "./ruleset/loyalsoldier/gfw.yaml"
    },
    "tld-not-cn": {
      "type": "http",
      "behavior": "domain",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/tld-not-cn.txt",
      "path": "./ruleset/loyalsoldier/tld-not-cn.yaml"
    },
    "applications": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/applications.txt",
      "path": "./ruleset/loyalsoldier/applications.yaml"
    },
    "telegramcidr": {
      "type": "http",
      "behavior": "ipcidr",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt",
      "path": "./ruleset/loyalsoldier/telegramcidr.yaml"
    },
    "cncidr": {
      "type": "http",
      "behavior": "ipcidr",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/cncidr.txt",
      "path": "./ruleset/loyalsoldier/cncidr.yaml"
    },
    "lancidr": {
      "type": "http",
      "behavior": "ipcidr",
      "format": "yaml",
      "interval": 86400,
      "url": "https://fastly.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/lancidr.txt",
      "path": "./ruleset/loyalsoldier/lancidr.yaml"
    },
    "openai": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/openai.yaml",
      "path": "./ruleset/MetaCubeX/openai.yaml"
    },
    "anthropic": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/anthropic.yaml",
      "path": "./ruleset/MetaCubeX/anthropic.yaml"
    },
    "google-gemini": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/google-gemini.yaml",
      "path": "./ruleset/MetaCubeX/google-gemini.yaml"
    },
    "xai": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/xai.yaml",
      "path": "./ruleset/MetaCubeX/xai.yaml"
    },
    "microsoft": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/microsoft.yaml",
      "path": "./ruleset/MetaCubeX/microsoft.yaml"
    },
    "youtube": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/youtube.yaml",
      "path": "./ruleset/MetaCubeX/youtube.yaml"
    },
    "netflix": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/netflix.yaml",
      "path": "./ruleset/MetaCubeX/netflix.yaml"
    },
    "tiktok": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/tiktok.yaml",
      "path": "./ruleset/MetaCubeX/tiktok.yaml"
    },
    "telegram": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/telegram.yaml",
      "path": "./ruleset/MetaCubeX/telegram.yaml"
    },
    "discord": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/discord.yaml",
      "path": "./ruleset/MetaCubeX/discord.yaml"
    },
    "twitter": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/twitter.yaml",
      "path": "./ruleset/MetaCubeX/twitter.yaml"
    },
    "disney": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/disney.yaml",
      "path": "./ruleset/MetaCubeX/disney.yaml"
    },
    "instagram": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/instagram.yaml",
      "path": "./ruleset/MetaCubeX/instagram.yaml"
    },
    "facebook": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/facebook.yaml",
      "path": "./ruleset/MetaCubeX/facebook.yaml"
    },
    "reddit": {
      "type": "http",
      "behavior": "classical",
      "format": "yaml",
      "interval": 86400,
      "url": "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/meta/geo/geosite/classical/reddit.yaml",
      "path": "./ruleset/MetaCubeX/reddit.yaml"
    }
  },
  "rules": [
    "DOMAIN-KEYWORD,dnscheck.tools,自定义代理",
    "DOMAIN-KEYWORD,ip.net.coffee,自定义代理",
    "DOMAIN-KEYWORD,github,自定义代理",
    "DOMAIN-KEYWORD,9kqz23b19z,自定义代理",
    "DOMAIN-KEYWORD,ippure,手动选择",
    "DOMAIN-KEYWORD,todetect,自定义代理",
    "DOMAIN-KEYWORD,biu.moe,直连模式",
    "DOMAIN-KEYWORD,joox,香港节点",
    "DOMAIN-KEYWORD,music-api.gdstudio.xyz,直连模式",
    "DOMAIN-KEYWORD,dglab.xiaoyudi,直连模式",
    "DOMAIN-KEYWORD,blinkroom,直连模式",
    "DOMAIN-KEYWORD,dglabplay,直连模式",
    "IP-CIDR,18.162.180.119/32,直连模式,no-resolve",
    "DOMAIN-KEYWORD,clerk,直连模式",
    "DOMAIN-KEYWORD,dghub.top,直连模式",
    "RULE-SET,openai,OpenAI",
    "RULE-SET,google-gemini,Gemini",
    "RULE-SET,anthropic,Claude",
    "RULE-SET,xai,Grok",
    "RULE-SET,applications,直连模式",
    "RULE-SET,private,直连模式",
    "RULE-SET,reject,广告过滤",
    "RULE-SET,youtube,YouTube",
    "RULE-SET,netflix,Netflix",
    "RULE-SET,disney,Disney+",
    "RULE-SET,tiktok,TikTok",
    "RULE-SET,telegram,Telegram",
    "RULE-SET,telegramcidr,Telegram,no-resolve",
    "RULE-SET,discord,Discord",
    "RULE-SET,twitter,X",
    "RULE-SET,facebook,Facebook",
    "RULE-SET,instagram,Instagram",
    "RULE-SET,reddit,Reddit",
    "DOMAIN-SUFFIX,googleapis.cn,Google",
    "DOMAIN-SUFFIX,gstatic.com,Google",
    "DOMAIN-SUFFIX,xn--ngstr-lra8j.com,Google",
    "RULE-SET,microsoft,Microsoft",
    "RULE-SET,icloud,Apple",
    "RULE-SET,apple,Apple",
    "RULE-SET,google,Google",
    "RULE-SET,proxy,默认线路",
    "RULE-SET,gfw,默认线路",
    "RULE-SET,tld-not-cn,默认线路",
    "RULE-SET,direct,直连模式",
    "RULE-SET,lancidr,直连模式,no-resolve",
    "RULE-SET,cncidr,直连模式,no-resolve",
    "GEOIP,LAN,直连模式,no-resolve",
    "GEOIP,CN,直连模式,no-resolve",
    "MATCH,漏网之鱼"
  ]
};

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
  config.proxies = valid.map(p => ({...p, udp: true}));
  config.profile = {...config.profile, "store-selected": true};
  return config;
}

