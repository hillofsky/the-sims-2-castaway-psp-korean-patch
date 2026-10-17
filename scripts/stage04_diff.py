"""Binary diff eng_us_orig.loc vs eng_us_test.loc (working copies only)."""
import hashlib, struct
o = open("logs/stage03/eng_us_orig.loc", "rb").read()
m = open("logs/stage04/eng_us_test.loc", "rb").read()
print(f"orig size={len(o)} sha={hashlib.sha256(o).hexdigest()}")
print(f"mod  size={len(m)} sha={hashlib.sha256(m).hexdigest()}")
mis = [i for i in range(min(len(o), len(m))) if o[i] != m[i]]
print(f"mismatch bytes={len(mis)} first={mis[0] if mis else None} last={mis[-1] if mis else None}")
# ranges
ranges = []
if mis:
    s = p = mis[0]
    for i in mis[1:]:
        if i == p + 1:
            p = i
        else:
            ranges.append((s, p))
            s = p = i
    ranges.append((s, p))
    print("ranges:", ranges)
# header / table checks
print("LOCH hdr same:", o[:0x14] == m[:0x14])
print("LOCL hdr same:", o[0x14:0x24] == m[0x14:0x24])
print("table same:", o[0x24:0xF4] == m[0x24:0xF4])
# expected: index8 fo? parse table
import sys
sys.path.insert(0, "logs/stage03")
from parse_loc import parse_loc
ro = parse_loc("logs/stage03/eng_us_orig.loc")
fo8 = ro["entries"][8]["file_offset"]
print(f"index8 fo={fo8:#x} alloc={ro['entries'][8]['allocated_bytes']}")
print(f"orig payload hex: {o[fo8:fo8+12].hex()}")
print(f"mod  payload hex: {m[fo8:fo8+12].hex()}")
with open("logs/stage04/mutation_diff.txt", "w", encoding="utf-8") as f:
    f.write(f"original SHA-256: {hashlib.sha256(o).hexdigest()}\n")
    f.write(f"modified SHA-256: {hashlib.sha256(m).hexdigest()}\n")
    f.write(f"original size: {len(o)}\nmodified size: {len(m)}\n")
    f.write(f"mismatch byte count: {len(mis)}\n")
    f.write(f"first mismatch: {mis[0] if mis else None}\nlast mismatch: {mis[-1] if mis else None}\n")
    f.write(f"mismatch ranges: {ranges if mis else []}\n")
    f.write(f"LOCH header identical: {o[:0x14] == m[:0x14]}\n")
    f.write(f"LOCL header identical: {o[0x14:0x24] == m[0x14:0x24]}\n")
    f.write(f"offset table identical: {o[0x24:0xF4] == m[0x24:0xF4]}\n")
    f.write(f"index8 file_offset: {fo8:#x} ({fo8})\n")
    f.write(f"orig bytes @fo8: {o[fo8:fo8+16].hex()}\nmod  bytes @fo8: {m[fo8:fo8+16].hex()}\n")
    f.write(f"expected: only UTF-16LE low bytes of index8 payload differ (6 chars -> 6 bytes at even offsets within 12B payload; high 00 bytes unchanged)\n")
    iso = (len(mis) == 6 and all(fo8 <= i < fo8 + 12 and (i - fo8) % 2 == 0 for i in mis)
           and o[:0x14] == m[:0x14] and o[0x14:0x24] == m[0x14:0x24] and o[0x24:0xF4] == m[0x24:0xF4] and len(o) == len(m))
    f.write(f"MUTATION_ISOLATED = {'PASS' if iso else 'FAIL'}\n")
print("wrote logs/stage04/mutation_diff.txt")
