# 🧱 GFW-VNM — Global Firewall Jumper

> Bộ **rule vượt tường lửa quốc gia** cho người Việt ở nước ngoài: **Trung Quốc (GFW)**, **UAE (TDRA)**, **Nga (TSPU / Roskomnadzor)**. Chỉ những gì bị chặn mới đi qua proxy, mọi thứ còn lại đi thẳng — app trong nước và trang nội địa giữ nguyên tốc độ.
>
> Tối ưu cho **Shadowrocket**, **sing-box** và **Hiddify**.

<p align="center">
  <a href="https://github.com/kulinh/gfw-vnm/stargazers"><img src="https://img.shields.io/github/stars/kulinh/gfw-vnm?label=Stars&style=social"></a>
  <a href="https://github.com/kulinh/gfw-vnm/network/members"><img src="https://img.shields.io/github/forks/kulinh/gfw-vnm?label=Fork&style=social"></a>
</p>

---

## 🌍 Tường lửa được hỗ trợ

| Tường lửa | Nước | Bộ rule | Nội dung chính |
|---|---|---|---|
| **GFW** (Great Firewall) | 🇨🇳 Trung Quốc | `sr_proxy_list_CN` | Google/YouTube, Meta (Facebook, Instagram, WhatsApp, Threads), Telegram, X, TikTok, LINE/Kakao/Naver, AI (ChatGPT, Claude, Gemini…), dev (GitHub raw, Docker, Hugging Face), streaming, báo chí quốc tế, crypto, kho APK; IP-CIDR đối chiếu BGP cho dịch vụ hay bị nhiễm DNS |
| **TDRA** | 🇦🇪 UAE | `sr_proxy_list_UAE` | Cuộc gọi OTT (WhatsApp, FaceTime, Messenger, Viber, Zalo, Telegram, Signal, Discord…) + IP media relay; nhóm site TDRA chặn hẳn. Không proxy những gì vẫn mở ở UAE |
| **TSPU / Roskomnadzor** | 🇷🇺 Nga | `sr_proxy_list_RU` | OTT bị chặn / bóp, Meta/X/LinkedIn/Twitch, YouTube & streaming đã rút khỏi Nga, báo chí, VPN/AI, dải hosting & Cloudflare bị bóp |
| — | mọi nơi | `zalo_zalopay` | Toàn bộ Zalo / ZaloPay (domain + dải IP VNG AS38244) — dùng khi muốn ép Zalo qua proxy |

**Nguyên tắc:** chỉ đưa vào rule những gì **đo được là bị chặn từ bên trong** tường lửa (Globalping từ các nhà mạng nội địa, OONI, itdog…), có ghi ngày đo ngay trong file. Thứ vẫn mở (ví dụ cursor.com, PayPal, LinkedIn ở TQ) không cho đi proxy vì chỉ làm chậm.

---

## 📦 Định dạng theo app

Mỗi bộ rule có sẵn ở ba định dạng, sinh từ cùng một nguồn (`.module`):

| App | File | Cách dùng |
|---|---|---|
| **Shadowrocket** | `<tên>.module` | Module (Cấu hình → Mô-đun) |
| **Shadowrocket** | `<tên>.list` | `RULE-SET,<url>,PROXY` trong config |
| **sing-box** | `sing-box/<tên>.srs` | `route.rule_set` kiểu `remote`, `format: binary` |
| **Hiddify** | `sing-box/<tên>.srs` | Cài đặt → Routing → Route rules → *Rule set* = URL, outbound = proxy |
| (đọc / chỉnh) | `sing-box/<tên>.json` | Bản nguồn của `.srs` (rule-set version 1, chạy trên sing-box ≥ 1.8) |

Thay `<tên>` bằng `sr_proxy_list_CN`, `sr_proxy_list_UAE`, `sr_proxy_list_RU` hoặc `zalo_zalopay`. Link gốc:

```
https://raw.githubusercontent.com/kulinh/gfw-vnm/master/<file>
https://cdn.jsdelivr.net/gh/kulinh/gfw-vnm@master/<file>      # mirror, có thể trễ vài giờ
```

> Ở **trong** Trung Quốc, `raw.githubusercontent.com` thường bị chặn: hãy tải/cập nhật rule khi đang bật proxy, hoặc dùng link jsDelivr.

---

## 🚀 Shadowrocket

1. **Config tối giản** — *Cấu hình → Tệp từ xa*, dán link rồi thêm máy chủ của bạn:
   ```
   https://raw.githubusercontent.com/kulinh/gfw-vnm/master/docs/03.shadowsocks_tiny.conf
   ```
   Phần `[Rule]` phải kết thúc bằng **`FINAL,DIRECT`** (blacklist mode).
2. **Module** — *Cấu hình → Mô-đun → (+)*:
   - 🇨🇳 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_CN.module`
   - 🇦🇪 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_UAE.module` (ở UAE **không** nạp `zalo_zalopay`)
   - 🇷🇺 `https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_RU.module`
3. Bật config, *Định tuyến toàn cục* = **Cấu hình**. Khi repo cập nhật, chỉ cần **làm mới module**.

Muốn dùng RULE-SET thay module: thêm vào `[Rule]` (trước `FINAL,DIRECT`):
```
RULE-SET,https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sr_proxy_list_CN.list,PROXY
```

## 📦 sing-box

Thêm rule set và một route rule đưa nó ra proxy; `route.final` để `direct`:

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

`http_client` (sing-box **≥ 1.14**): tải rule qua chính proxy — ở trong TQ không bị chặn GitHub, và hết cảnh báo *"implicit default HTTP client … deprecated"* mỗi lần khởi động. Không trỏ được vào outbound `direct` (sing-box báo lỗi). Với sing-box **≤ 1.13** bỏ dòng này (trường chưa tồn tại).

## 🛡️ Hiddify

*Cài đặt → Routing → Route rules → Thêm*: chọn **Rule set**, dán URL
`https://raw.githubusercontent.com/kulinh/gfw-vnm/master/sing-box/sr_proxy_list_CN.srs`, outbound = **Proxy**.
Để phần còn lại đi thẳng, đặt chế độ định tuyến mặc định của Hiddify là *Direct* (hoặc thêm rule bypass tương ứng).

---

## 🔗 Dùng với cf-vpn

Fleet **cf-vpn** sinh sẵn config cho cả ba app, đã **nhúng thẳng** rule của repo này (Worker tải module ở edge Cloudflare, nơi GitHub không bị chặn), nên **không cần** cài module:

| Profile | Dùng khi | Rule |
|---|---|---|
| `RWL-CN` | ở Trung Quốc | `sr_proxy_list_CN` → proxy, còn lại thẳng |
| `RWL-UAE` | ở UAE | `sr_proxy_list_UAE` |
| `RWL-RU` | ở Nga | `sr_proxy_list_RU` |
| `RWL-TOCN` | **ngoài** Trung Quốc | ngược lại: site TQ → proxy (node tối ưu cho TQ), còn lại thẳng |

Sửa module ở đây → lần cập nhật config kế tiếp tự có, không cần deploy. Không đưa config cá nhân (chứa UUID/mật khẩu) hay địa chỉ node vào repo này — repo là danh sách chung, public.

---

## 🛠️ Đóng góp / bảo trì

1. Chỉ sửa file **`.module`** (nguồn duy nhất). Thêm domain **kèm dòng ghi chú ngày + cách đo** (ví dụ `# 0/6 node CN vào được, globalping 04/10/2026`).
2. Sinh lại các định dạng khác (cần binary `sing-box` để biên dịch `.srs`):
   ```bash
   python3 tools/build.py            # ghi .list + sing-box/*.json + sing-box/*.srs
   python3 tools/build.py --check    # chỉ kiểm tra lệch (chạy trước khi commit)
   ```
3. Commit cả `.module` lẫn file sinh ra.

Dòng `USER-AGENT` / `URL-REGEX` chỉ có hiệu lực trong Shadowrocket (sing-box không có loại rule tương đương).

---

## ❓ Câu hỏi thường gặp

**Bật proxy toàn cục thì vào được, bật theo rule thì không?**
> Gần như luôn do `FINAL` sai (phải là `FINAL,DIRECT`) hoặc thiếu một domain phụ trợ của site. Báo domain đó để bổ sung.

**App ngân hàng / app nội địa báo lỗi khi bật Shadowrocket?**
> *Cài đặt → Proxy*, đổi loại proxy từ `HTTP` sang `none` (chế độ TUN).

**Có chặn quảng cáo không?**
> Không. Repo chỉ lo vượt tường lửa; chặn quảng cáo nên làm ở tầng DNS (NextDNS, AdGuard DNS…).

**Hàng trăm rule có làm chậm máy?**
> Không đáng kể: cả Shadowrocket lẫn sing-box tra rule theo cấu trúc băm / cây, không duyệt tuần tự.

---

## 📁 Cấu trúc

```
gfw-vnm/
├── sr_proxy_list_CN.module    # nguồn: GFW (Trung Quốc)
├── sr_proxy_list_UAE.module   # nguồn: TDRA (UAE)
├── sr_proxy_list_RU.module    # nguồn: TSPU (Nga)
├── zalo_zalopay.module        # nguồn: Zalo / ZaloPay
├── *.list                     # Shadowrocket RULE-SET (sinh tự động)
├── sing-box/*.json, *.srs     # sing-box / Hiddify rule-set (sinh tự động)
├── tools/build.py             # sinh mọi định dạng từ .module
└── docs/                      # config mẫu + tài liệu Shadowrocket (tham khảo)
```

---

Khởi đầu là bản fork của [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules) (cảm ơn tác giả), nay đi hướng riêng: rule được chọn lọc và kiểm chứng theo từng tường lửa, không đồng bộ các danh sách tự động của upstream. Giấy phép: xem [LICENSE](LICENSE).
