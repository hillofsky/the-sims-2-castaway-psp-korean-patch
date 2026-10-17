"""Stage04 mutation via entry index (no hardcoded file offsets).
Reuses logs/stage03 parse/rebuild structure logic.
Usage: python stage04_mutate.py
"""
import struct, sys, os, hashlib
sys.path.insert(0, "logs/stage03")
from parse_loc import parse_loc

SRC = "logs/stage03/eng_us_orig.loc"
DST = "logs/stage04/eng_us_test.loc"
IDX, OLD, NEW = 8, "Cancel", "TEST!!"
assert len(OLD) == len(NEW) == 6, "same-length requirement"

r = parse_loc(SRC)
assert r["header"]["count_at_locl_plus_12"] == 52
e8 = r["entries"][IDX]
assert e8["text"] == OLD, f"index {IDX} is {e8['text']!r}, expected {OLD!r}"
assert e8["error"] is None

# rebuild through builder logic (recompute offsets; same length => identical table)
sys.path.insert(0, "logs/stage03")
from rebuild_loc import build
texts = [e["text"] for e in r["entries"]]
assert len(texts) == 52
texts[IDX] = NEW
info = build(texts, SRC, DST)
print(f"mutated index {IDX}: {OLD!r} -> {NEW!r}")
print(f"wrote {DST}: size={info['size']} count={info['count']}")

# re-parse verification
r2 = parse_loc(DST)
ok = r2["ok"]
others_same = all(
    (a["text"] == b["text"]) if k != IDX else (b["text"] == NEW)
    for k, (a, b) in enumerate(zip(r["entries"], r2["entries"]))
)
print(f"reparse: ok={ok}/52 fails={r2['fails']} others_same={others_same} size={r2['size']}")
assert ok == 52 and r2["fails"] == 0 and others_same and r2["size"] == 5580
print("MUTATION_VERIFY = PASS")
