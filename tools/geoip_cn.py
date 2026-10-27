#!/usr/bin/env python3
import ipaddress
import json
import sys

MIN_PREFIXES = 4000


def main(src, dst):
    data = json.load(open(src, encoding="utf-8"))
    cidrs = [c for r in data.get("rules", []) for c in r.get("ip_cidr", [])]
    for c in cidrs:
        ipaddress.ip_network(c)
    if len(cidrs) < MIN_PREFIXES:
        sys.exit(f"only {len(cidrs)} prefixes in {src}; refusing to write {dst}")
    with open(dst, "w", encoding="utf-8") as f:
        f.write('{"version":1,"rules":[{"ip_cidr":[\n')
        f.write(",\n".join(json.dumps(c) for c in cidrs))
        f.write("\n]}]}\n")
    print(f"wrote {dst} ({len(cidrs)} prefixes)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
