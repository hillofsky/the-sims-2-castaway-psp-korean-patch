"""Scan emulated RAM for a byte pattern via chunked memory.read.
Usage: python stage04_memscan.py <port> <pattern_hex> [start_hex=08800000] [size_hex=02000000] [chunk=100000]
Prints matching emulated addresses. Raw binary pattern match (no decoding).
"""
import sys, json, base64
sys.path.insert(0, "scripts")
from stage04_ws import ws_connect, ws_send, ws_recv
port = int(sys.argv[1])
pat = bytes.fromhex(sys.argv[2])
start = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x08800000
total = int(sys.argv[4], 16) if len(sys.argv) > 4 else 0x02000000
chunk = int(sys.argv[5], 16) if len(sys.argv) > 5 else 0x100000
s = ws_connect("127.0.0.1", port)
s.settimeout(2.0)
try:
    while True:
        ws_recv(s, timeout=1)
except Exception:
    pass
found = []
off = 0
while off < total:
    n = min(chunk, total - off)
    a = start + off
    ws_send(s, json.dumps({"event": "memory.read", "address": a, "size": n}))
    try:
        r = ws_recv(s, timeout=120)
    except Exception as e:
        print(f"READ-ERR at {a:#010x}: {e}")
        break
    try:
        d = json.loads(r)
    except Exception:
        print(f"BADJSON at {a:#010x}: {r[:120]}")
        break
    if "base64" not in d:
        print(f"NO-DATA at {a:#010x}: {r[:200]}")
        break
    raw = base64.b64decode(d["base64"])
    i = 0
    while True:
        i = raw.find(pat, i)
        if i < 0:
            break
        found.append(a + i)
        print(f"HIT {a+i:#010x}")
        i += 1
    off += n
    print(f"scanned {off:#x}/{total:#x}", flush=True)
print(f"DONE matches={len(found)}")
for m in found:
    print(f"  {m:#010x}")
s.close()
