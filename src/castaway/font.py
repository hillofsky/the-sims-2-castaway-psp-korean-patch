"""Experimental FntM v414 glyph extension for observed PSP resources."""
import struct
from PIL import Image, ImageDraw, ImageFont
from .font_packing import compact_layout

def parse_font(payload):
    start=payload.index(b'FntM');data=payload[start:]
    version,count=struct.unpack_from('<HH',data,8)
    if version!=414 or struct.unpack_from('<I',data,4)[0]!=len(data):raise ValueError('Unsupported FntM variant')
    flags=struct.unpack_from('<I',data,12)[0];stride=16 if flags&0x10000 else 12
    defs,kern,bmp=struct.unpack_from('<III',data,20)
    width,height=struct.unpack_from('<HH',data,bmp+4)
    kind=data[bmp]
    if kind!=0x5c:raise ValueError('Only observed 4bpp font image supported')
    pixel_size=(width*height+1)//2
    raw=data[bmp+16:bmp+16+pixel_size]
    pixels=bytes(n for b in raw for n in (b&15,b>>4))[:width*height]
    glyphs=[data[defs+i*stride:defs+(i+1)*stride] for i in range(count)]
    codes=[struct.unpack_from('<H',g)[0] for g in glyphs]
    if codes!=sorted(set(codes)):raise ValueError('Font glyphs not strictly sorted')
    return dict(start=start,data=data,version=version,count=count,stride=stride,defs=defs,kern=kern,bmp=bmp,width=width,height=height,pixels=pixels,glyphs=glyphs,codes=codes,pixel_size=pixel_size)

def extend_font(payload,characters,ttf_path,size):
    old=parse_font(payload);missing=sorted(set(ord(c) for c in characters)-set(old['codes']))
    if not missing:return payload,None
    if any(c>65535 for c in missing):raise ValueError('Only BMP glyphs currently supported')
    font=ImageFont.truetype(str(ttf_path),size)
    width=old['width'];cell=size+2
    while True:
        cols=width//cell;rows=(len(missing)+cols-1)//cols
        height=old['height']+1+rows*cell
        if height<=512 or width>=512:break
        width*=2
    raster_size=size;packing_mode='original_grid';positions=None
    if width>512 or height>512:
        packing_mode='compact';width=512
        minimum=11 if size>=13 else 9
        for candidate_size in range(size,minimum-1,-1):
            candidate_font=ImageFont.truetype(str(ttf_path),candidate_size)
            layout=compact_layout(old['width'],old['height'],missing,candidate_font)
            if layout is not None:
                positions,height=layout;font=candidate_font;raster_size=candidate_size;break
        if positions is None:raise ValueError('All required glyphs do not fit PSP atlas; no characters omitted')
    atlas=Image.new('L',(width,height));atlas.paste(Image.frombytes('L',(old['width'],old['height']),old['pixels']),(0,0))
    tail=old['data'][old['bmp']+16+old['pixel_size']:]
    if len(tail)!=208:raise ValueError('Unexpected palette/trailer')
    alphas=[tail[48+i*4+3] for i in range(16)]
    stride=16
    glyphs=[]
    for original_record in old['glyphs']:
        if old['stride']==16:glyphs.append(original_record)
        else:
            converted=bytearray(16);converted[:12]=original_record
            converted[8]=0;converted[11]=0
            struct.pack_into('<H',converted,14,original_record[8])
            glyphs.append(bytes(converted))
    for i,code in enumerate(missing):
        ch=chr(code);box=font.getbbox(ch);gw=box[2]-box[0];gh=box[3]-box[1]
        if gw>255 or gh>255 or gw>cell or gh>cell:raise ValueError('Glyph does not fit cell')
        if positions is None:x=(i%cols)*cell;y=old['height']+1+(i//cols)*cell
        else:x,y=positions[code]
        glyph_image=Image.new('L',(gw,gh));ImageDraw.Draw(glyph_image).text((-box[0],-box[1]),ch,font=font,fill=255)
        quantized=bytes(min(range(16),key=lambda k:abs(alphas[k]-v)) for v in glyph_image.tobytes())
        atlas.paste(Image.frombytes('L',(gw,gh),quantized),(x,y))
        advance=round(font.getlength(ch))
        record=bytearray(stride);struct.pack_into('<HBBHH',record,0,code,gw,gh,x,y)
        # Align ink to the source font's uppercase baseline, rather than
        # vertically centering an em square. Title glyph offsets are negative.
        capitals=[g for c,g in zip(old['codes'],old['glyphs']) if 65<=c<=90]
        bottoms=sorted(struct.unpack_from('<b',g,10)[0]+g[3] for g in capitals)
        bottom=bottoms[len(bottoms)//2] if bottoms else old['data'][18]
        if old['stride']==12:
            # Glow originals have large blur margins; Korean title/glow ink
            # shares the non-glow title baseline instead.
            bottom=3
        y_offset=bottom-gh
        if not -128<=y_offset<=127:raise ValueError('Glyph bearing out of range')
        record[8]=advance if stride==12 else 0;record[9]=0
        struct.pack_into('<b',record,10,y_offset)
        if stride==16:struct.pack_into('<H',record,14,advance)
        glyphs.append(bytes(record))
    defs_end=old['defs']+old['count']*old['stride']
    gap=bytearray(old['data'][defs_end:old['bmp']])
    added=len(glyphs)*stride-old['count']*old['stride'];header=bytearray(old['data'][:old['defs']])
    struct.pack_into('<I',header,12,struct.unpack_from('<I',header,12)[0]|0x50000)
    newbmp=old['bmp']+added
    struct.pack_into('<H',header,10,len(glyphs))
    if old['stride']==12 or min(missing)<=old['codes'][-1]:struct.pack_into('<I',header,24,0)
    elif old['kern']:struct.pack_into('<I',header,24,old['kern']+added)
    struct.pack_into('<I',header,28,newbmp)
    pointer48=struct.unpack_from('<I',header,48)[0]
    if pointer48!=old['bmp']-32:raise ValueError('Unexpected image descriptor pointer')
    struct.pack_into('<I',header,48,pointer48+added)
    struct.pack_into('<ff',header,64,1.0/width,1.0/height)
    pixels=atlas.tobytes();packed=bytes(pixels[i]|((pixels[i+1] if i+1<len(pixels) else 0)<<4) for i in range(0,len(pixels),2))
    image_header=bytearray(old['data'][old['bmp']:old['bmp']+16])
    struct.pack_into('<I',image_header,0,0x5c|((len(packed)+48)<<8))
    struct.pack_into('<HH',image_header,4,width,height)
    struct.pack_into('<I',gap,len(gap)-28,len(packed)+48)
    struct.pack_into('<I',gap,len(gap)-20,len(packed))
    struct.pack_into('<II',gap,len(gap)-8,width,height)
    glyphs.sort(key=lambda g:struct.unpack_from('<H',g)[0])
    new=header+b''.join(glyphs)+gap+image_header+packed+tail
    struct.pack_into('<I',new,4,len(new))
    prefix=bytearray(payload[:old['start']]);delta=len(new)-len(old['data'])
    name_length=struct.unpack_from('<I',prefix,12)[0];outer_size_offset=16+name_length
    struct.pack_into('<I',prefix,outer_size_offset,struct.unpack_from('<I',prefix,outer_size_offset)[0]+delta)
    struct.pack_into('<I',prefix,len(prefix)-4,len(new))
    result=bytes(prefix+new);parsed=parse_font(result)
    if parsed['codes']!=sorted(old['codes']+missing):raise ValueError('New font code coverage mismatch')
    # Reconstruct old pixels to ensure old glyph images are unchanged.
    for y in range(old['height']):
        if parsed['pixels'][y*width:y*width+old['width']]!=old['pixels'][y*old['width']:(y+1)*old['width']]:raise ValueError('Original font bitmap changed')
    descriptor=struct.unpack_from('<8I',parsed['data'],parsed['bmp']-32)
    if descriptor[1]!=len(packed)+48 or descriptor[3]!=len(packed) or descriptor[6:]!=(width,height):raise ValueError('Image descriptor mismatch')
    preview=atlas.point([a for a in alphas]+[0]*240)
    preview.info['packing']={'mode':packing_mode,'raster_size':raster_size,'requested_size':size}
    return result,preview



