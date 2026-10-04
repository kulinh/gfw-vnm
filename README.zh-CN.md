# 🧱 GFW-VNM — Global Firewall Jumper（全球防火墙跳板）

[English](README.md) | **简体中文** | [Русский](README.ru.md)

用于穿越国家级防火墙的规则集 —— **中国（GFW）**、**阿联酋（TDRA）** 和 **俄罗斯（TSPU / 俄联邦通信监管局 RKN）**，采用 **黑名单模式**：只有被防火墙封锁的内容走代理，其余全部直连，本地应用、银行和国内网站保持原有速度。

适配 **Shadowrocket（小火箭）**、**sing-box** 和 **Hiddify**。

<p>
  <a href="https://github.com/kulinh/gfw-vnm/stargazers"><img src="https://img.shields.io/github/stars/kulinh/gfw-vnm?style=social" alt="Stars"></a>
  <a href="https://github.com/kulinh/gfw-vnm/commits/master"><img src="https://img.shields.io/github/last-commit/kulinh/gfw-vnm" alt="Last commit"></a>
</p>

## 支持的防火墙

| 防火墙 | 国家 | 规则集 | 覆盖内容 |
|---|---|---|---|
| **GFW**（防火长城） | 🇨🇳 中国 | `sr_proxy_list_CN` | Google / YouTube、Meta（Facebook、Instagram、WhatsApp、Threads）、Telegram、X、TikTok、LINE / Kakao / Naver、AI（ChatGPT、Claude、Gemini…）、开发（GitHub raw、Docker、Hugging Face）、流媒体、国际新闻、加密货币、APK 应用商店；并为易遭 DNS 污染的服务附带 IP-CIDR |
| **TDRA** | 🇦🇪 阿联酋 | `sr_proxy_list_UAE` | OTT 应用的语音与视频通话（WhatsApp、FaceTime、Messenger、Viber、Telegram、Signal、Discord…）及其媒体服务器 IP 段；TDRA 直接封锁的网站类别。在阿联酋本就能打开的服务一律不加 |
| **TSPU / RKN** | 🇷🇺 俄罗斯 | `sr_proxy_list_RU` | 被封锁或限速的 OTT 应用、Meta / X / LinkedIn / Twitch、YouTube 及已退出俄罗斯的流媒体、被封锁的新闻媒体、VPN / AI 服务、被限速的境外主机与 Cloudflare 网段 |

**收录原则：** 每个域名都必须 **从防火墙内部实测为被封锁**（使用当地运营商的 Globalping 探针、OONI、itdog 等），并在文件中注明测量日期与方法。仍可直接访问的网站（例如在中国的 cursor.com、PayPal、LinkedIn）不予收录 —— 让它们走代理只会变慢。

## 各客户端对应文件

每个规则集都提供三种格式，均由同一个 `.module` 源文件生成：

| 客户端 | 文件 | 用法 |
|---|---|---|
| **Shadowrocket** | `<name>.module` | 模块（配置 → 模块） |
| **Shadowrocket** | `<name>.list` | 在配置中写 `RULE-SET,<url>,PROXY` |
| **sing-box** | `sing-box/<name>.srs` | `remote` 类型规则集，`format: binary` |
| **Hiddify** | `sing-box/<name>.srs` | 设置 → Routing → Route rules → *Rule set* |
| *（阅读 / 审查）* | `sing-box/<name>.json` | `.srs` 的源文件（规则集版本 1，兼容 sing-box ≥ 1.8） |

`<name>` 为 `sr_proxy_list_CN`、`sr_proxy_list_UAE` 或 `sr_proxy_list_RU`。下载地址：

```
https://raw.githubusercontent.com/kulinh/gfw-vnm/master/<file>
https://cdn.jsdelivr.net/gh/kulinh/gfw-vnm@master/<file>     # 镜像，可能延迟几个小时
```

> 在中国境内，`raw.githubusercontent.com` 通常被封锁：请在开启代理时更新规则，或使用 jsDelivr 链接。

## Shadowrocket（小火箭）

1. 以 [`examples/shadowrocket.conf`](examples/shadowrocket.conf) 为起点（配置 → 添加远程文件），再加入你自己的服务器。其 `[Rule]` 部分以 **`FINAL,DIRECT`** 结尾 —— 请保持不变。
2. 配置 → 模块 → **+**，按所在地添加：
   - 🇨🇳 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_CN.module`
   - 🇦🇪 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_UAE.module`
   - 🇷🇺 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_RU.module`
3. 全局路由选择 **配置**。仓库更新后，只需刷新模块。

更喜欢 RULE-SET？把下面这行放在 `FINAL,DIRECT` 之前：

```
RULE-SET,https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_CN.list,PROXY
```

## sing-box

```json
{
  "route": {
    "rule_set": [
      {
        "type": "remote",
        "tag": "gfw-cn",
        "format": "binary",
        "url": "https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sing-box/sr_proxy_list_CN.srs",
        "update_interval": "1d",
        "http_client": { "detour": "proxy" }
      }
    ],
    "rules": [
      { "action": "sniff" },
      { "rule_set": "gfw-cn", "outbound": "proxy" }
    ],
    "final": "direct"
  }
}
```

`http_client`（sing-box **1.14+**）通过代理下载规则集 —— 因此在中国境内也能更新 —— 并消除每次启动时出现的 *"implicit default HTTP client … deprecated"* 警告。它不能指向 `direct` 出站（sing-box 会拒绝）。在 sing-box **1.13 及更早版本** 中该字段不存在，请删除这一行。

## Hiddify

设置 → Routing → Route rules → **添加**：类型选 **Rule set**，URL 填
`https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sing-box/sr_proxy_list_CN.srs`，出站选 **Proxy**。默认路由保持 *Direct*，其余流量即可绕过代理。

## 参与贡献

1. 只修改 **`.module`** 文件 —— 它们是唯一的源。新增条目时附上注释，写明日期与测量方式（例如 `# 0/6 China probes, Globalping 2026-10-04`）。
2. 重新生成其他格式（编译 `.srs` 需要 `sing-box` 可执行文件）：
   ```bash
   python3 tools/build.py            # 生成 *.list、sing-box/*.json、sing-box/*.srs
   python3 tools/build.py --check    # 有过期文件则失败 —— 提交前运行
   ```
3. 将 `.module` 与生成的文件一并提交。

`USER-AGENT` / `URL-REGEX` 规则仅在 Shadowrocket 中生效；sing-box 没有对应的规则类型。

## 常见问题

**全局代理一切正常，规则模式却打不开？**
几乎都是 `FINAL` 写错（必须是 `FINAL,DIRECT`），或网站的某个辅助域名不在列表中。请提交 issue 并附上该域名。

**开启小火箭后，本地银行 App 拒绝运行？**
设置 → 代理 → 将代理类型从 `HTTP` 改为 `none`（TUN 模式）。

**能去广告吗？**
不在本项目范围内。本仓库只负责穿越防火墙；去广告请在 DNS 层处理（NextDNS、AdGuard DNS…）。

**几百条规则会让手机变慢吗？**
不会。Shadowrocket 与 sing-box 使用哈希 / 前缀树匹配，并非逐条扫描。

## 目录结构

```
gfw-vnm/
├── sr_proxy_list_CN.module     # 源：中国（GFW）
├── sr_proxy_list_UAE.module    # 源：阿联酋（TDRA）
├── sr_proxy_list_RU.module     # 源：俄罗斯（TSPU）
├── *.list                      # Shadowrocket RULE-SET（自动生成）
├── sing-box/*.json, *.srs      # sing-box / Hiddify 规则集（自动生成）
├── examples/shadowrocket.conf  # 最小化黑名单模式配置
└── tools/build.py              # 由模块生成全部格式
```

## 致谢与许可

本项目最初 fork 自 [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules)，感谢原作者。现已独立发展：按防火墙逐条挑选并实测规则，不再同步上游每日自动构建的列表。许可证见 [LICENSE](LICENSE)。
