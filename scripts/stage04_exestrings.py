import re
d = open('C:/Users/admin/AppData/Local/Temp/opencode/ppsspp/PPSSPPWindows64.exe', 'rb').read()
strs = re.findall(rb'[ -~]{4,90}', d)
seen = set()
for s in strs:
    if b'ebugger' in s or b'eveloper' in s or b'WebSocket' in s:
        if s not in seen:
            seen.add(s)
            try:
                print(s.decode('ascii'))
            except Exception:
                pass
