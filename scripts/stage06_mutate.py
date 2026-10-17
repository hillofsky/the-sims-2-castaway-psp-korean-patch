"""Stage06 attempt 1: index 5 LOAD %s -> TEST %s from ORIGINAL."""
import sys, hashlib
sys.path.insert(0, "logs/stage03")
from parse_loc import parse_loc
from rebuild_loc import build
SRC, DST = "logs/stage03/eng_us_orig.loc", "logs/stage06/eng_us_render_test.loc"
IDX, OLD, NEW = 5, "LOAD %s", "TEST %s"
r = parse_loc(SRC)
assert r["header"]["count_at_locl_plus_12"] == 52 and r["entries"][IDX]["text"] == OLD
texts = [e["text"] for e in r["entries"]]
texts[IDX] = NEW
info = build(texts, SRC, DST)
r2 = parse_loc(DST)
assert r2["ok"] == 52 and r2["fails"] == 0 and r2["size"] == 5580 == len(open(SRC, "rb").read())
assert r2["entries"][IDX]["text"] == NEW
assert all((a["text"] == b["text"]) if k != IDX else True for k, (a, b) in enumerate(zip(r["entries"], r2["entries"])))
o, m = open(SRC, "rb").read(), open(DST, "rb").read()
assert o[:0x14] == m[:0x14] and o[0x14:0x24] == m[0x14:0x24] and o[0x24:0xF4] == m[0x24:0xF4]
mis = [i for i in range(len(o)) if o[i] != m[i]]
print(f"orig {hashlib.sha256(o).hexdigest()}\nmod  {hashlib.sha256(m).hexdigest()}")
print(f"size {len(o)}/{len(m)} mismatch={len(mis)} first={mis[0] if mis else None} last={mis[-1] if mis else None}")
assert len(mis) == 4, mis  # L->T, O->E, A->S, D->T low bytes; high 00 + '%s' unchanged
print("RENDER_MUTATION_ISOLATED = PASS")
with open("logs/stage06/mutation_report.txt", "w", encoding="utf-8") as f:
    f.write(f"index={IDX} {OLD!r} -> {NEW!r}\norig sha={hashlib.sha256(o).hexdigest()}\nmod sha={hashlib.sha256(m).hexdigest()}\n")
    f.write(f"size={len(o)}/{len(m)} mismatch={len(mis)} first={mis[0]} last={mis[-1]}\nRENDER_MUTATION_ISOLATED = PASS\n")
with open("logs/stage06/mutation_diff.txt", "w", encoding="utf-8") as f:
    f.write(f"mismatch bytes: {len(mis)} at {mis}\n")
    fo = r["entries"][IDX]["file_offset"]
    f.write(f"index5 fo={fo:#x} orig={o[fo:fo+14].hex()} mod={m[fo:fo+14].hex()}\n")
print("wrote mutation_report.txt mutation_diff.txt")
