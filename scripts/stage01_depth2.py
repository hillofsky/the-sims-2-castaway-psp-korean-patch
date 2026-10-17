import json
d = json.load(open('logs/stage01/toc.json', encoding='utf-8'))
entries = d['all_entries']
def children(prefix):
    pfx = prefix.rstrip('/') + '/' if prefix != '/' else '/'
    out = []
    for e in entries:
        p = e['path']
        if p == prefix:
            continue
        if p.startswith(pfx):
            rest = p[len(pfx):]
            if '/' not in rest:
                out.append(e)
    return sorted(out, key=lambda x: x['path'])
with open('logs/stage01/depth2.txt', 'w', encoding='utf-8') as f:
    for prefix in ['/', '/PSP_GAME', '/PSP_GAME/SYSDIR', '/PSP_GAME/USRDIR']:
        f.write('== ' + prefix + ' ==\n')
        for e in children(prefix):
            tag = 'DIR ' if e['is_dir'] else 'FILE'
            f.write(f"{tag} {e['size']:>10} {e['path']}\n")
        f.write('\n')
print('wrote depth2.txt')
