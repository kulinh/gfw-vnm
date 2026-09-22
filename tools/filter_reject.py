#!/usr/bin/env python3
# Drop allowlisted domains from sr_reject_list.module (idempotent).
# Run from the repo root after each manual sync from GMOogway.
import pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
allow = [l.strip().lower() for l in (root / "tools/reject_allowlist.txt").read_text().splitlines()
         if l.strip() and not l.startswith("#")]
mod = root / "sr_reject_list.module"

def allowed(domain: str) -> bool:
    return any(domain == a or domain.endswith("." + a) for a in allow)

out, dropped = [], []
for line in mod.read_text().splitlines():
    if line.startswith("DOMAIN-SUFFIX,") and allowed(line.split(",")[1].strip().lower()):
        dropped.append(line)
        continue
    out.append(line)
rules = sum(1 for l in out if l.startswith("DOMAIN-SUFFIX,"))
out = [re.sub(r"Rules:\d+", f"Rules:{rules}", l) if l.startswith("#!desc=") else l for l in out]
mod.write_text("\n".join(out) + "\n")
print(f"dropped {len(dropped)}, {rules} rules left")
for l in dropped:
    print("  " + l)
