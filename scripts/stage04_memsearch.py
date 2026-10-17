"""Search emulated RAM via WS memory.search (bytes pattern, base64).
Usage: python stage04_memsearch.py <port> <addr_hex> <size_hex> <pattern_hex> [maxResults]
"""
import sys, json, base64
sys.path.insert(0, "scripts")
from stage04_ws import ws_connect, ws_send, ws_recv
port = int(sys.argv[1])
addr = int(sys.argv[2], 16)
size = int(sys.argv[3], 16)
pat = bytes.fromhex(sys.argv[4])
mx = int(sys.argv[5]) if len(sys.argv) > 5 else 50
b64 = base64.b64encode(pat).decode()
msg = json.dumps({"event": "memory.search", "address": addr, "size": size,
                  "type": "bytes", "base64": b64, "maxResults": mx})
s = ws_connect("127.0.0.1", port)
s.settimeout(1.0)
try:
    while True:
        ws_recv(s, timeout=1)
except Exception:
    pass
ws_send(s, msg)
print("SENT", msg[:160])
try:
    r = ws_recv(s, timeout=120)
    print("RECV", r[:2000])
    d = json.loads(r)
    ms = d.get("matches", [])
    print(f"MATCHES={len(ms)} truncated={d.get('truncated')}")
    for m in ms[:20]:
        print(f"  {m:#010x}")
except Exception as e:
    print("RECV-ERR", type(e).__name__, e)
s.close()
