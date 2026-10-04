# 🧱 GFW-VNM — Global Firewall Jumper

[English](README.md) | [简体中文](README.zh-CN.md) | **Русский**

Наборы правил для обхода государственных файрволов — **Китай (GFW)**, **ОАЭ (TDRA)** и **Россия (ТСПУ / Роскомнадзор)** — в **режиме чёрного списка**: через прокси идёт только то, что блокирует файрвол, всё остальное — напрямую, поэтому местные приложения, банки и внутренние сайты работают на полной скорости.

Для **Shadowrocket**, **sing-box** и **Hiddify**.

<p>
  <a href="https://github.com/kulinh/gfw-vnm/stargazers"><img src="https://img.shields.io/github/stars/kulinh/gfw-vnm?style=social" alt="Stars"></a>
  <a href="https://github.com/kulinh/gfw-vnm/commits/master"><img src="https://img.shields.io/github/last-commit/kulinh/gfw-vnm" alt="Last commit"></a>
</p>

## Поддерживаемые файрволы

| Файрвол | Страна | Набор правил | Что открывает |
|---|---|---|---|
| **GFW** (Великий китайский файрвол) | 🇨🇳 Китай | `sr_proxy_list_CN` | Google / YouTube, Meta (Facebook, Instagram, WhatsApp, Threads), Telegram, X, TikTok, LINE / Kakao / Naver, ИИ (ChatGPT, Claude, Gemini…), разработка (GitHub raw, Docker, Hugging Face), стриминг, международные СМИ, криптовалюта, магазины APK; IP-CIDR для сервисов с отравленным DNS |
| **TDRA** | 🇦🇪 ОАЭ | `sr_proxy_list_UAE` | Голосовые и видеозвонки в OTT-приложениях (WhatsApp, FaceTime, Messenger, Viber, Telegram, Signal, Discord…) с диапазонами IP их медиасерверов; группы сайтов, которые TDRA блокирует полностью. Ничего из того, что в ОАЭ и так открывается |
| **ТСПУ / РКН** | 🇷🇺 Россия | `sr_proxy_list_RU` | Заблокированные или замедленные OTT-приложения, Meta / X / LinkedIn / Twitch, YouTube и ушедшие из России стриминги, заблокированные СМИ, VPN / ИИ-сервисы, замедленный зарубежный хостинг и диапазоны Cloudflare |

**Как попадают записи:** каждый домен **измерен как заблокированный изнутри** файрвола (зонды Globalping у местных операторов, OONI, itdog…), дата и способ измерения указаны рядом в файле. Сайты, которые по-прежнему открываются — например cursor.com, PayPal или LinkedIn из Китая, — не включаются: через прокси они только медленнее.

## Файлы для каждого клиента

Каждый набор правил выпускается в трёх форматах, все генерируются из одного источника `.module`:

| Клиент | Файл | Как использовать |
|---|---|---|
| **Shadowrocket** | `<name>.module` | модуль (Конфигурация → Модули) |
| **Shadowrocket** | `<name>.list` | `RULE-SET,<url>,PROXY` в конфиге |
| **sing-box** | `sing-box/<name>.srs` | набор правил `remote`, `format: binary` |
| **Hiddify** | `sing-box/<name>.srs` | Настройки → Routing → Route rules → *Rule set* |
| *(для чтения / проверки)* | `sing-box/<name>.json` | исходник `.srs` (версия формата 1, любой sing-box ≥ 1.8) |

`<name>` — это `sr_proxy_list_CN`, `sr_proxy_list_UAE` или `sr_proxy_list_RU`. Скачивание:

```
https://raw.githubusercontent.com/kulinh/gfw-vnm/master/<file>
https://cdn.jsdelivr.net/gh/kulinh/gfw-vnm@master/<file>     # зеркало, может отставать на несколько часов
```

> В Китае `raw.githubusercontent.com` обычно заблокирован: обновляйте правила с включённым прокси или используйте ссылку jsDelivr.

## Shadowrocket

1. Начните с [`examples/shadowrocket.conf`](examples/shadowrocket.conf) (Конфигурация → добавить удалённый файл) и добавьте свои серверы. Раздел `[Rule]` заканчивается на **`FINAL,DIRECT`** — оставьте так.
2. Конфигурация → Модули → **+**, добавьте модуль для вашей страны:
   - 🇨🇳 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_CN.module`
   - 🇦🇪 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_UAE.module`
   - 🇷🇺 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_RU.module`
3. Глобальная маршрутизация — **Конфигурация**. После обновления репозитория просто обновите модуль.

Удобнее RULE-SET? Добавьте перед `FINAL,DIRECT`:

```
RULE-SET,https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_RU.list,PROXY
```

## sing-box

```json
{
  "route": {
    "rule_set": [
      {
        "type": "remote",
        "tag": "gfw-ru",
        "format": "binary",
        "url": "https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sing-box/sr_proxy_list_RU.srs",
        "update_interval": "1d",
        "http_client": { "detour": "proxy" }
      }
    ],
    "rules": [
      { "action": "sniff" },
      { "rule_set": "gfw-ru", "outbound": "proxy" }
    ],
    "final": "direct"
  }
}
```

`http_client` (sing-box **1.14+**) скачивает набор правил через прокси — так он обновляется даже изнутри файрвола — и убирает предупреждение *"implicit default HTTP client … deprecated"* при каждом запуске. Указывать на исходящий `direct` нельзя (sing-box отказывается). В sing-box **1.13 и старше** этого поля нет — удалите строку.

## Hiddify

Настройки → Routing → Route rules → **Добавить**: тип **Rule set**, URL
`https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sing-box/sr_proxy_list_RU.srs`, исходящий **Proxy**. Маршрут по умолчанию оставьте *Direct*, чтобы всё остальное шло мимо прокси.

## Участие в проекте

1. Редактируйте только файлы **`.module`** — это единственный источник. Добавляйте комментарий с датой и способом измерения блокировки (например, `# 0/6 China probes, Globalping 2026-10-04`).
2. Пересоберите остальные форматы (для компиляции `.srs` нужен бинарник `sing-box`):
   ```bash
   python3 tools/build.py            # пишет *.list, sing-box/*.json, sing-box/*.srs
   python3 tools/build.py --check    # падает, если что-то устарело — запускайте перед коммитом
   ```
3. Коммитьте `.module` вместе со сгенерированными файлами.

Строки `USER-AGENT` / `URL-REGEX` работают только в Shadowrocket; в sing-box таких типов правил нет.

## Частые вопросы

**С глобальным прокси всё работает, а в режиме правил — нет?**
Почти всегда это неверный `FINAL` (должен быть `FINAL,DIRECT`) или вспомогательный домен сайта, которого нет в списке. Откройте issue с этим доменом.

**Банковское приложение не запускается с включённым Shadowrocket?**
Настройки → Прокси → смените тип прокси с `HTTP` на `none` (режим TUN).

**Блокировка рекламы?**
Вне задач проекта. Репозиторий только обходит файрволы; рекламу блокируйте на уровне DNS (NextDNS, AdGuard DNS…).

**Несколько сотен правил замедляют телефон?**
Нет. Shadowrocket и sing-box ищут совпадения по хешам / префиксным деревьям, а не перебором списка.

## Структура

```
gfw-vnm/
├── sr_proxy_list_CN.module     # источник: Китай (GFW)
├── sr_proxy_list_UAE.module    # источник: ОАЭ (TDRA)
├── sr_proxy_list_RU.module     # источник: Россия (ТСПУ)
├── *.list                      # Shadowrocket RULE-SET (генерируется)
├── sing-box/*.json, *.srs      # наборы правил sing-box / Hiddify (генерируются)
├── examples/shadowrocket.conf  # минимальный конфиг в режиме чёрного списка
└── tools/build.py              # собирает все форматы из модулей
```

## Благодарности и лицензия

Проект начинался как форк [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules) — спасибо автору. Теперь он развивается самостоятельно: правила подбираются вручную и проверяются для каждого файрвола, а не синхронизируются с ежедневно собираемыми списками upstream. Лицензия: см. [LICENSE](LICENSE).
