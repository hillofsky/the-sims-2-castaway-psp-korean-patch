"""Minimal stdlib WebSocket client for PPSSPP debugger (subprotocol debugger.ppsspp.org).
Usage: python stage04_ws.py <port> '<json>' [--recv N]
"""
import socket, ssl, hashlib, base64, struct, json, sys, os

def ws_connect(host, port, path="/debugger", proto="debugger.ppsspp.org", timeout=8):
    s = socket.create_connection((host, port), timeout=timeout)
    key = base64.b64encode(os.urandom(16)).decode()
    req = (f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\n"
           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n"
           f"Sec-WebSocket-Protocol: {proto}\r\n\r\n")
    s.sendall(req.encode())
    head = b""
    while b"\r\n\r\n" not in head:
        chunk = s.recv(4096)
        if not chunk:
            raise ConnectionError("handshake closed")
        head += chunk
    htxt = head.decode("latin1")
    if "101" not in htxt.split("\r\n", 1)[0]:
        raise ConnectionError(f"handshake failed: {htxt[:300]}")
    return s

def ws_send(s, text):
    b = text.encode("utf-8")
    mask = os.urandom(4)
    n = len(b)
    if n < 126:
        hdr = struct.pack("!BB", 0x81, 0x80 | n)
    elif n < 65536:
        hdr = struct.pack("!BBH", 0x81, 0x80 | 126, n)
    else:
        hdr = struct.pack("!BBQ", 0x81, 0x80 | 127, n)
    s.sendall(hdr + mask + bytes(x ^ mask[i % 4] for i, x in enumerate(b)))

def recvn(s, n):
    buf = b""
    while len(buf) < n:
        c = s.recv(n - len(buf))
        if not c:
            raise ConnectionError("closed mid-frame")
        buf += c
    return buf

def ws_recv(s, timeout=10):
    # Accumulate fragments (server streams large base64 across continuation frames).
    parts = []
    opcode = None
    s.settimeout(timeout)
    while True:
        h = recvn(s, 2)
        fin, op, mlen = h[0] & 0x80, h[0] & 0x0F, h[1] & 0x7F
        if op != 0x0 and opcode is None:
            opcode = op
        if mlen == 126:
            mlen = struct.unpack("!H", recvn(s, 2))[0]
        elif mlen == 127:
            mlen = struct.unpack("!Q", recvn(s, 8))[0]
        if h[1] & 0x80:
            mask = recvn(s, 4)
        else:
            mask = None
        payload = recvn(s, mlen) if mlen else b""
        if mask:
            payload = bytes(x ^ mask[i % 4] for i, x in enumerate(payload))
        if op == 0x8:
            raise ConnectionError("server close")
        if op == 0x9:  # ping -> pong, continue
            ws_send_pong(s, payload)
            continue
        parts.append(payload)
        if fin:
            break
    data = b"".join(parts)
    if opcode == 0x1:
        return data.decode("utf-8", errors="replace")
    return data

def ws_send_pong(s, payload):
    s.sendall(struct.pack("!BB", 0x8A, len(payload)) + payload)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5300
    msg = sys.argv[2] if len(sys.argv) > 2 else '{"event":"version","name":"stage04","version":"1.0"}'
    want = 3
    for a in sys.argv:
        if a.startswith("--recv="):
            want = int(a.split("=")[1])
    s = ws_connect("127.0.0.1", port)
    print("CONNECTED")
    ws_send(s, msg)
    print("SENT", msg)
    for _ in range(want):
        try:
            print("RECV", ws_recv(s, timeout=12))
        except Exception as e:
            print("RECV-ERR", type(e).__name__, e)
            break
    s.close()
