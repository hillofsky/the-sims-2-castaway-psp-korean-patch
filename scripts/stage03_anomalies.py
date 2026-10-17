"""Anomaly scan over parsed entries (working copy only)."""
import struct, sys
sys.path.insert(0, "logs/stage03")
from parse_loc import parse_loc
r = parse_loc("logs/stage03/eng_us_orig.loc")
entries = r["entries"]
ra = [e["raw_offset"] for e in entries]
rows = []
def add(idx, kind, detail):
    rows.append((idx, kind, detail))
# per-entry checks
seen_text = {}
for e in entries:
    i, t = e["index"], e["text"]
    if t == "":
        add(i, "empty_string", "zero-length text")
    if t in seen_text:
        add(i, "duplicate_string", f"same as index {seen_text[t]}")
    else:
        seen_text[t] = i
    if e["error"]:
        add(i, "decode_or_range_fail", e["error"])
    if e["terminator_bytes"] != 2:
        add(i, "terminator_not_2", str(e["terminator_bytes"]))
    if e["padding_bytes"] != 2:
        add(i, "padding_not_2", str(e["padding_bytes"]))
    exp = len(t.encode("utf-16-le")) + 4 if t is not None else -1
    if exp != e["allocated_bytes"]:
        add(i, "alloc_mismatch", f"alloc={e['allocated_bytes']} text+4={exp}")
    if t and "%" in t:
        add(i, "format_token", t[:80])
    if t and ("\n" in t or "\r" in t):
        add(i, "newline", repr(t[:80]))
    if t and any(ord(c) > 127 for c in t):
        nona = "".join(f"U+{ord(c):04X}" for c in t if ord(c) > 127)
        add(i, "non_ascii", nona[:80] + " :: " + t[:60])
# table-level checks
for i in range(1, len(ra)):
    if ra[i] == ra[i-1]:
        add(i, "offset_duplicate", str(ra[i]))
    if ra[i] < ra[i-1]:
        add(i, "offset_inversion", f"{ra[i-1]} -> {ra[i]}")
    if not (0 <= ra[i] < r["header"]["locl_size"]):
        add(i, "offset_out_of_range", str(ra[i]))
with open("logs/stage03/anomalies.tsv", "w", encoding="utf-8") as f:
    f.write("index\tkind\tdetail\n")
    for i, k, dt in rows:
        dt = dt.replace("\n", "\\n").replace("\t", " ")
        f.write(f"{i}\t{k}\t{dt}\n")
print(f"anomalies: {len(rows)}")
from collections import Counter
print(Counter(k for _, k, _ in rows))
for row in rows:
    print(row)
