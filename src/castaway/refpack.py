"""Bounded decoder for the 10 FB RefPack variant found in APT BIG files.
Format reference: https://github.com/actioninja/refpack-rs
Independent implementation; no third-party code dependency.
"""
def decompress(data, limit=64*1024*1024):
    if data[:2] != b'\x10\xfb' or len(data)<5:
        raise ValueError('Unsupported RefPack header')
    expected=int.from_bytes(data[2:5],'big')
    if expected > limit:
        raise ValueError('RefPack output exceeds configured limit')
    pos,out=5,bytearray()
    def take(n):
        nonlocal pos
        if pos+n>len(data): raise ValueError('Truncated RefPack')
        result=data[pos:pos+n];pos+=n
        return result
    while True:
        code=take(1)[0]
        length,distance=0,0
        if code<0x80:
            b=take(1)[0]
            literal=code&3
            length=((code>>2)&7)+3
            distance=((code&0x60)<<3)+b+1
        elif code<0xc0:
            b,c=take(2)
            literal=b>>6
            length=(code&0x3f)+4
            distance=((b&0x3f)<<8)+c+1
        elif code<0xe0:
            b,c,d=take(3)
            literal=code&3
            length=((code&0xc)<<6)+d+5
            distance=((code&0x10)<<12)+(b<<8)+c+1
        elif code<0xfc:
            literal=((code&0x1f)<<2)+4
        else:
            literal=code&3
        if len(out)+literal+length>expected:
            raise ValueError('RefPack output exceeds declared size')
        out.extend(take(literal))
        if length:
            if distance>len(out): raise ValueError('Invalid RefPack backreference')
            for _ in range(length): out.append(out[-distance])
        if code>=0xfc: break
    if len(out)!=expected: raise ValueError('RefPack size mismatch')
    return bytes(out)
