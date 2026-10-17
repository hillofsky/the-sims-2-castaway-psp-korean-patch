"""Deterministic compact packing outside the untouched original atlas rectangle."""
def compact_layout(old_width,old_height,codes,font,limit=512):
    free=[]
    if old_width+1<limit:free.append((old_width+1,0,limit-old_width-1,old_height+1))
    if old_height+1<limit:free.append((0,old_height+1,limit,limit-old_height-1))
    boxes={code:font.getbbox(chr(code)) for code in codes}
    sizes={code:(b[2]-b[0]+1,b[3]-b[1]+1) for code,b in boxes.items()}
    order=sorted(codes,key=lambda c:(-max(sizes[c]),-sizes[c][0]*sizes[c][1],c))
    positions={}
    for code in order:
        w,h=sizes[code]
        options=[(min(rw-w,rh-h),max(rw-w,rh-h),y,x,rw,rh) for x,y,rw,rh in free if rw>=w and rh>=h]
        if not options:return None
        _,_,y,x,_,_=min(options)
        positions[code]=(x,y)
        updated=[]
        for fx,fy,fw,fh in free:
            if x>=fx+fw or x+w<=fx or y>=fy+fh or y+h<=fy:
                updated.append((fx,fy,fw,fh));continue
            if x>fx:updated.append((fx,fy,x-fx,fh))
            if x+w<fx+fw:updated.append((x+w,fy,fx+fw-x-w,fh))
            if y>fy:updated.append((fx,fy,fw,y-fy))
            if y+h<fy+fh:updated.append((fx,y+h,fw,fy+fh-y-h))
        candidates=sorted(set(updated))
        free=[a for i,a in enumerate(candidates) if not any(i!=j and a[0]>=b[0] and a[1]>=b[1] and a[0]+a[2]<=b[0]+b[2] and a[1]+a[3]<=b[1]+b[3] for j,b in enumerate(candidates))]
    height=max([old_height]+[positions[c][1]+sizes[c][1] for c in codes])
    return positions,height
