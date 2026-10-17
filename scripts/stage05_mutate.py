"""Stage05 mutation: Cancel -> OK! from ORIGINAL (not TEST!!).
Reuses logs/stage03 parse/rebuild logic (variable-length capable).
Usage: python stage05_mutate.py
"""
import sys, hashlib
sys.path.insert(0, "logs/stage03")
from parse_loc import parse_loc
from rebuild_loc import build

SRC = "logs/stage03/eng_us_orig.loc"
DST = "logs/stage05/eng_us_variable.loc"
IDX, OLD, NEW = 8, "Cancel", "OK!"

r = parse_loc(SRC)
assert r["header"]["count_at_locl_plus_12"] == 52
assert r["entries"][IDX]["text"] == OLD, r["entries"][IDX]["text"]
texts = [e["text"] for e in r["entries"]]
texts[IDX] = NEW
info = build(texts, SRC, DST)
print(f"mutated index {IDX}: {OLD!r} -> {NEW!r}")
print(f"size={info['size']} count={info['count']} locl_size={info['locl_size']}")

r2 = parse_loc(DST)
assert r2["ok"] == 52 and r2["fails"] == 0 and r2["size"] == info["size"]
assert r2["entries"][IDX]["text"] == NEW
assert all((a["text"] == b["text"]) if k != IDX else True
           for k, (a, b) in enumerate(zip(r["entries"], r2["entries"])))
# pool reaches EOF exactly, no trailing garbage
last = r2["entries"][-1]
assert last["next_offset"] == r2["size"], (last["next_offset"], r2["size"])
print(f"reparse OK: 52/52, pool end == EOF ({r2['size']})")
o = open(SRC, "rb").read()
m = open(DST, "rb").read()
print(f"orig {len(o)} {hashlib.sha256(o).hexdigest()}")
print(f"mod  {len(m)} {hashlib.sha256(m).hexdigest()}")
print("VARIABLE_BUILD_VERIFY = PASS")
