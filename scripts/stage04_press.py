"""Press a PSP button via WS with explicit hold/release on one connection.
Usage: python stage04_press.py <port> <button> [hold_ms=400]
"""
import sys, time
sys.path.insert(0, "scripts")
from stage04_ws import ws_connect, ws_send, ws_recv
port = int(sys.argv[1]) if len(sys.argv) > 1 else 5300
btn = sys.argv[2] if len(sys.argv) > 2 else "cross"
hold = int(sys.argv[3]) if len(sys.argv) > 3 else 400
s = ws_connect("127.0.0.1", port)
# drain spontaneous
s.settimeout(0.5)
try:
    while True:
        ws_recv(s, timeout=0.5)
except Exception:
    pass
ws_send(s, '{"event":"input.buttons.send","buttons":{"%s":true}}' % btn)
time.sleep(hold / 1000.0)
ws_send(s, '{"event":"input.buttons.send","buttons":{"%s":false}}' % btn)
print(f"PRESSED {btn} hold={hold}ms")
try:
    print("RECV", ws_recv(s, timeout=5))
except Exception as e:
    print("RECV-ERR", e)
s.close()
