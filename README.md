# 🧱 GFW-VNM — Global Firewall Jumper

**English** | [简体中文](README.zh-CN.md) | [Русский](README.ru.md)

Rule sets for getting past national firewalls — **China (GFW)**, **UAE (TDRA)** and **Russia (TSPU / Roskomnadzor)** — in **blacklist mode**: only what the firewall blocks goes through your proxy, everything else stays direct, so local apps, banks and domestic sites keep their full speed.

Built for **Shadowrocket**, **sing-box** and **Hiddify**.

<p>
  <a href="https://github.com/kulinh/gfw-vnm/stargazers"><img src="https://img.shields.io/github/stars/kulinh/gfw-vnm?style=social" alt="Stars"></a>
  <a href="https://github.com/kulinh/gfw-vnm/commits/master"><img src="https://img.shields.io/github/last-commit/kulinh/gfw-vnm" alt="Last commit"></a>
</p>

## Firewalls covered

| Firewall | Country | Rule set | What it opens |
|---|---|---|---|
| **GFW** (Great Firewall) | 🇨🇳 China | `sr_proxy_list_CN` | Google / YouTube, Meta (Facebook, Instagram, WhatsApp, Threads), Telegram, X, TikTok, LINE / Kakao / Naver, AI (ChatGPT, Claude, Gemini…), dev (GitHub raw, Docker, Hugging Face), streaming, international press, crypto, APK stores; IP-CIDR for services whose DNS gets poisoned |
| **TDRA** | 🇦🇪 UAE | `sr_proxy_list_UAE` | Voice & video calls over OTT apps (WhatsApp, FaceTime, Messenger, Viber, Telegram, Signal, Discord…) with their media-server IP ranges; the site groups TDRA blocks outright. Nothing that already opens in the UAE |
| **TSPU / Roskomnadzor** | 🇷🇺 Russia | `sr_proxy_list_RU` | Blocked or throttled OTT apps, Meta / X / LinkedIn / Twitch, YouTube and streaming that left Russia, blocked press, VPN / AI services, throttled foreign hosting and Cloudflare ranges |

**How entries get in:** every domain is **measured as blocked from inside** the firewall (Globalping probes on the local carriers, OONI, itdog…), with the date and method noted next to it in the file. Sites that still open — cursor.com, PayPal or LinkedIn from China, for example — stay out: proxying them only slows them down.

## Files per client

Every rule set ships in three formats, all generated from the same `.module` source:

| Client | File | Use it as |
|---|---|---|
| **Shadowrocket** | `<name>.module` | a module (Config → Modules) |
| **Shadowrocket** | `<name>.list` | `RULE-SET,<url>,PROXY` in a config |
| **sing-box** | `sing-box/<name>.srs` | a `remote` rule set, `format: binary` |
| **Hiddify** | `sing-box/<name>.srs` | Settings → Routing → Route rules → *Rule set* |
| *(to read / review)* | `sing-box/<name>.json` | source of the `.srs` (rule-set version 1, any sing-box ≥ 1.8) |

`<name>` is `sr_proxy_list_CN`, `sr_proxy_list_UAE` or `sr_proxy_list_RU`. Download from:

```
https://raw.githubusercontent.com/kulinh/gfw-vnm/master/<file>
https://cdn.jsdelivr.net/gh/kulinh/gfw-vnm@master/<file>     # mirror, may lag a few hours
```

> Inside China `raw.githubusercontent.com` is usually blocked: refresh rules with the proxy on, or use the jsDelivr link.

## Shadowrocket

1. Start from [`examples/shadowrocket.conf`](examples/shadowrocket.conf) (Config → add remote file) and add your servers. Its `[Rule]` section ends with **`FINAL,DIRECT`** — keep it that way.
2. Config → Modules → **+**, add the one for where you are:
   - 🇨🇳 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_CN.module`
   - 🇦🇪 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_UAE.module`
   - 🇷🇺 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_RU.module`
3. Set global routing to **Config**. When the repo changes, just refresh the module.

Prefer RULE-SET? Put this before `FINAL,DIRECT`:

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

`http_client` (sing-box **1.14+**) downloads the rule set through the proxy — so it works from inside China — and silences the *"implicit default HTTP client … deprecated"* warning on every start. It cannot point at a `direct` outbound (sing-box refuses). Remove the line on sing-box **1.13 and older**, where the field does not exist.

## Hiddify

Settings → Routing → Route rules → **Add**: type **Rule set**, URL
`https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sing-box/sr_proxy_list_CN.srs`, outbound **Proxy**. Leave the default route on *Direct* so everything else bypasses the proxy.

## Contributing

1. Edit only the **`.module`** files — they are the single source. Add a comment with the date and how the block was measured (e.g. `# 0/6 China probes, Globalping 2026-10-04`).
2. Regenerate the other formats (needs a `sing-box` binary to compile `.srs`):
   ```bash
   python3 tools/build.py            # writes *.list, sing-box/*.json, sing-box/*.srs
   python3 tools/build.py --check    # fails if anything is stale — run before committing
   ```
3. Commit the `.module` together with the generated files.

`USER-AGENT` / `URL-REGEX` lines only take effect in Shadowrocket; sing-box has no such rule types.

## FAQ

**Everything works with global proxy, but not in rule mode?**
Almost always a wrong `FINAL` (it must be `FINAL,DIRECT`) or a helper domain of the site that is missing from the list. Open an issue with the domain.

**A local banking app refuses to run with Shadowrocket on?**
Settings → Proxy → change the proxy type from `HTTP` to `none` (TUN mode).

**Ad blocking?**
Out of scope. This repo only gets you past firewalls; block ads at the DNS layer (NextDNS, AdGuard DNS…).

**Do a few hundred rules slow the phone down?**
No. Shadowrocket and sing-box match with hash / trie lookups, not by scanning the list.

## Layout

```
gfw-vnm/
├── sr_proxy_list_CN.module     # source: China (GFW)
├── sr_proxy_list_UAE.module    # source: UAE (TDRA)
├── sr_proxy_list_RU.module     # source: Russia (TSPU)
├── *.list                      # Shadowrocket RULE-SET (generated)
├── sing-box/*.json, *.srs      # sing-box / Hiddify rule sets (generated)
├── examples/shadowrocket.conf  # minimal blacklist-mode config
└── tools/build.py              # builds every format from the modules
```

## Credits & license

Started as a fork of [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules) — thanks to its author. It now follows its own path: hand-picked, measured rules per firewall, not upstream's daily auto-built lists. License: see [LICENSE](LICENSE).
