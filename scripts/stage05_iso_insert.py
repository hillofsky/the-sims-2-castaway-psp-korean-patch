"""Stage05 Tasks 7-8: copy ISO, patch payload + zero tail + dir-record size LE/BE, verify.
Usage: python stage05_iso_insert.py
"""
import os, struct, hashlib, shutil

ORIG = "Sims 2, The - Castaway (USA) (En,Fr,De,Es,It,Nl,Pt).iso"
TEST = "The_Sims_2_STAGE05_VARIABLE.iso"
MOD = "logs/stage05/eng_us_variable.loc"
SECTOR = 2048
LBA = 275296          # from iso_filesystem_report (TOC-derived, cross-checked)
REC_OFF = 0x118D4     # dir record byte offset (TOC-derived)
OLD_SIZE, NEW_SIZE = 5580, 5574

assert not os.path.exists(TEST), f"{TEST} exists; refusing overwrite"
mod = open(MOD, "rb").read()
assert len(mod) == NEW_SIZE
print("copying ISO...")
shutil.copyfile(ORIG, TEST)
with open(TEST, "r+b") as fh:
    fh.seek(LBA * SECTOR)
    fh.write(mod)
    fh.write(b"\x00" * (OLD_SIZE - NEW_SIZE))  # zero stale tail within own sectors
    # patch dir record size LE + BE
    fh.seek(REC_OFF + 10)
    fh.write(struct.pack("<I", NEW_SIZE))
    fh.seek(REC_OFF + 14)
    fh.write(struct.pack(">I", NEW_SIZE))
    fh.flush()
print("patched payload + zero tail + size LE/BE")

# verify: record + re-extract via TOC lookup
with open(TEST, "rb") as fh:
    fh.seek(REC_OFF + 10)
    le = struct.unpack("<I", fh.read(4))[0]
    be = struct.unpack(">I", fh.read(4))[0]
    print(f"record size LE={le} BE={be}")
    assert le == NEW_SIZE and be == NEW_SIZE
    fh.seek(LBA * SECTOR)
    back = fh.read(NEW_SIZE)
    print(f"reextract sha: {hashlib.sha256(back).hexdigest()}")
    print(f"expected  sha: {hashlib.sha256(mod).hexdigest()}")
    ok = back == mod
    # stale tail must be zero
    tail = fh.read(OLD_SIZE - NEW_SIZE)
    print(f"tail zeroed: {tail == bytes(OLD_SIZE-NEW_SIZE)}")
    ok = ok and tail == bytes(OLD_SIZE - NEW_SIZE)
print(f"ISO_VARIABLE_INSERT = {'PASS' if ok else 'FAIL'}")
with open("logs/stage05/iso_insert_report.txt", "w", encoding="utf-8") as f:
    f.write(f"ORIG: {os.path.abspath(ORIG)}\nTEST: {os.path.abspath(TEST)}\n")
    f.write(f"LBA={LBA} old={OLD_SIZE} new={NEW_SIZE} rec_off={REC_OFF:#x}\n")
    f.write(f"record LE/BE={le}/{be}\n")
    f.write(f"reextract sha={hashlib.sha256(back).hexdigest()} expected={hashlib.sha256(mod).hexdigest()}\n")
    f.write(f"ISO_VARIABLE_INSERT = {'PASS' if ok else 'FAIL'}\n")
