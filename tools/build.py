#!/usr/bin/env python3
"""Build every client format from the Shadowrocket modules (the single source).

For each module (sr_proxy_list_CN / _UAE / _RU, zalo_zalopay):

  <name>.list                 Shadowrocket RULE-SET (TYPE,value — no policy)
  sing-box/<name>.json        sing-box rule-set, source format (version 1)
  sing-box/<name>.srs         sing-box rule-set, binary — sing-box and Hiddify

    python3 tools/build.py            # write everything (.srs needs a sing-box binary)
    python3 tools/build.py --check    # exit 1 if a .list / .json is stale

Version 1 of the rule-set format loads on every sing-box since 1.8, which
covers the Hiddify builds still in use. USER-AGENT / URL-REGEX lines have no
sing-box equivalent and are left out of the sing-box files (Shadowrocket
keeps them). Order follows the module, so a diff reads like the module edit.
"""
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REPO = "kulinh/gfw-vnm"
MODULES = ("sr_proxy_list_CN", "sr_proxy_list_UAE", "sr_proxy_list_RU", "zalo_zalopay")
LIST_TYPES = ("DOMAIN-SUFFIX", "DOMAIN", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6",
              "USER-AGENT", "URL-REGEX", "GEOIP", "IP-ASN")
SINGBOX = {"DOMAIN": "domain", "DOMAIN-SUFFIX": "domain_suffix",
           "DOMAIN-KEYWORD": "domain_keyword", "IP-CIDR": "ip_cidr", "IP-CIDR6": "ip_cidr"}


def rules(path):
    """(type, value, flags) for every rule line of a module, first occurrence only."""
    out, seen = [], set()
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line[0] in "#[;":
            continue
        parts = [p.strip() for p in line.split(",")]
        if parts[0] not in LIST_TYPES or len(parts) < 2 or not parts[1]:
            continue
        key = (parts[0], parts[1])
        if key in seen:
            continue
        seen.add(key)
        out.append((parts[0], parts[1], [f for f in parts[3:] if f.lower() == "no-resolve"]))
    return out


def build_list(name, rs):
    head = (f"# {name}.list — generated from {name}.module by tools/build.py (do not edit).\n"
            f"# Shadowrocket: RULE-SET,https://raw.githubusercontent.com/{REPO}/master/{name}.list,PROXY\n")
    return head + "\n".join(",".join([t, v] + f) for t, v, f in rs) + "\n"


def build_singbox(rs):
    rule = {}
    for t, v, _ in rs:
        key = SINGBOX.get(t)
        if key:
            rule.setdefault(key, []).append(v)
    order = ("domain", "domain_suffix", "domain_keyword", "ip_cidr")
    return json.dumps({"version": 1, "rules": [{k: rule[k] for k in order if k in rule}]},
                      indent=2, ensure_ascii=False) + "\n"


def main():
    check = "--check" in sys.argv
    singbox = os.environ.get("SINGBOX") or shutil.which("sing-box")
    os.makedirs(os.path.join(ROOT, "sing-box"), exist_ok=True)
    rc = 0
    for name in MODULES:
        rs = rules(os.path.join(ROOT, f"{name}.module"))
        skipped = sum(1 for t, _, _ in rs if t not in SINGBOX)
        outputs = [(f"{name}.list", build_list(name, rs)),
                   (f"sing-box/{name}.json", build_singbox(rs))]
        for rel, want in outputs:
            path = os.path.join(ROOT, rel)
            current = open(path, encoding="utf-8").read() if os.path.exists(path) else None
            if check:
                if current != want:
                    print(f"STALE: {rel} — run tools/build.py")
                    rc = 1
            elif current != want:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(want)
                print(f"wrote {rel}")
        srs = os.path.join(ROOT, f"sing-box/{name}.srs")
        if not check:
            if not singbox:
                print(f"no sing-box binary: {name}.srs not rebuilt", file=sys.stderr)
                rc = 1
            else:
                subprocess.run([singbox, "rule-set", "compile", "--output", srs,
                                os.path.join(ROOT, f"sing-box/{name}.json")], check=True)
        elif not os.path.exists(srs):
            print(f"MISSING: sing-box/{name}.srs")
            rc = 1
        print(f"{name}: {len(rs)} rules ({skipped} Shadowrocket-only: USER-AGENT / URL-REGEX / GEOIP / IP-ASN)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
