"""Observed SHPM PSP textures: indexed swizzled images and DXT3 logo blocks."""
import io
import struct
from PIL import Image


def image_header(payload):
    start = payload.index(b'SHPM')
    if struct.unpack_from('<I', payload, start + 8)[0] != 1:
        raise ValueError('Only single-image SHPM resources supported')
    offset = start + struct.unpack_from('<I', payload, start + 20)[0]
    kind = payload[offset]
    length = int.from_bytes(payload[offset + 1:offset + 4], 'little')
    width, height = struct.unpack_from('<HH', payload, offset + 4)
    if offset + length > len(payload):
        raise ValueError('SHPM image outside resource')
    return offset, kind, length, width, height


def decode_texture(payload):
    offset, kind, length, width, height = image_header(payload)
    raw = payload[offset + 16:offset + length]
    if kind == 0x58:
        if len(raw) != width * height * 2:
            raise ValueError('Unexpected BGR565 texture storage')
        values = struct.unpack('<%dH' % (width * height), raw)
        image = Image.new('RGBA', (width, height))
        image.putdata([((v & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, ((v >> 11) & 31) * 255 // 31, 255) for v in values])
        return image
    if kind in (0x5c, 0x5d):
        stride = (width + 1) // 2 if kind == 0x5c else width
        palette_width, palette_height = struct.unpack_from('<HH', payload, offset + length + 4)
        count = palette_width * palette_height
        if count < 1 or count > (16 if kind == 0x5c else 256):
            raise ValueError('Invalid indexed palette count')
        palette = payload[offset + length + 16:offset + length + 16 + count * 4]
        if len(palette) != count * 4:
            raise ValueError('Unsupported indexed texture geometry')
        indices = []
        for y in range(height):
            for x in range(stride):
                source = ((y // 8) * (stride // 16) + x // 16) * 128 + (y % 8) * 16 + x % 16 if stride >= 16 and height >= 8 else y * stride + x
                value = raw[source]
                indices.extend((value & 15, value >> 4) if kind == 0x5c else (value,))
        rgba = b''.join(palette[v * 4:v * 4 + 4] for v in indices[:width * height])
        return Image.frombytes('RGBA', (width, height), rgba)
    if kind not in (0x45, 0x46):
        raise ValueError('Unsupported SHPM image type: ' + hex(kind))
    image = Image.new('RGBA', (width, height))
    pixels = image.load()
    for by in range((height + 3) // 4):
        for bx in range((width + 3) // 4):
            block_size = 8 if kind == 0x45 else 16
            block = raw[(by * ((width + 3) // 4) + bx) * block_size:][:block_size]
            color_indices = int.from_bytes(block[:4], 'little')
            c0, c1 = struct.unpack_from('<HH', block, 4)
            # SHPM 0x46 is PSP DXT3/BC2: sixteen explicit 4-bit alphas.
            alpha_bits = int.from_bytes(block[8:16], 'little') if kind == 0x46 else 0
            colors = [tuple(round(v * 255 / m) for v, m in (((c >> 11) & 31, 31), ((c >> 5) & 63, 63), (c & 31, 31))) for c in (c0, c1)]
            colors += [tuple((2 * colors[0][j] + colors[1][j]) // 3 for j in range(3)), tuple((colors[0][j] + 2 * colors[1][j]) // 3 for j in range(3))]
            if kind == 0x45 and c0 <= c1:
                colors[2] = tuple((colors[0][j] + colors[1][j]) // 2 for j in range(3))
                colors[3] = (0, 0, 0)
            for y in range(4):
                for x in range(4):
                    if bx * 4 + x < width and by * 4 + y < height:
                        k = y * 4 + x
                        color_index = (color_indices >> (k * 2)) & 3
                        alpha = ((alpha_bits >> (k * 4)) & 15) * 17 if kind == 0x46 else (0 if c0 <= c1 and color_index == 3 else 255)
                        pixels[bx * 4 + x, by * 4 + y] = colors[color_index] + (alpha,)
    return image


def replace_dxt3_texture(payload, image):
    """Keep all headers and dimensions; write PSP BC2 color/explicit alpha."""
    offset, kind, length, width, height = image_header(payload)
    if kind != 0x46:
        raise ValueError('Expected observed PSP DXT3 texture')
    image = image.convert('RGBA').resize((width, height), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format='DDS', pixel_format='DXT5')
    dds = buffer.getvalue()
    if dds[84:88] != b'DXT5':
        raise ValueError('Unexpected DDS codec')
    blocks = dds[128:]
    if len(blocks) != length - 16:
        raise ValueError('Compressed color block count changed')
    raw = bytearray()
    for pos in range(0, len(blocks), 16):
        b = blocks[pos:pos + 16]
        # Use the BC1-compatible color portion only. The SHPM resource uses
        # explicit BC2 alpha, not the BC3 alpha endpoint/index scheme.
        block_index = pos // 16
        bx = block_index % ((width + 3) // 4)
        by = block_index // ((width + 3) // 4)
        values = [image.getpixel((min(bx * 4 + x, width - 1),
                                  min(by * 4 + y, height - 1)))[3]
                  for y in range(4) for x in range(4)]
        alpha_bits = sum(round(v * 15 / 255) << (i * 4) for i, v in enumerate(values))
        raw.extend(b[12:16] + b[8:12] + alpha_bits.to_bytes(8, 'little'))
    return payload[:offset + 16] + bytes(raw) + payload[offset + length:]


def replace_indexed_texture(payload, image):
    """Replace indexed pixels using the original RGBA palette and PSP layout."""
    offset, kind, length, width, height = image_header(payload)
    if kind not in (0x5c, 0x5d):
        raise ValueError('Expected indexed SHPM texture')
    stride = (width + 1) // 2 if kind == 0x5c else width
    palette_width, palette_height = struct.unpack_from('<HH', payload, offset + length + 4)
    count = palette_width * palette_height
    if not 1 <= count <= (16 if kind == 0x5c else 256):
        raise ValueError('Invalid indexed palette count')
    data = payload[offset + length + 16:offset + length + 16 + count * 4]
    if len(data) != count * 4:
        raise ValueError('Truncated indexed palette')
    palette = [tuple(data[i:i + 4]) for i in range(0, len(data), 4)]
    image = image.convert('RGBA').resize((width, height), Image.Resampling.LANCZOS)
    cache = {}
    indices = []
    for pixel in image.getdata():
        if pixel not in cache:
            cache[pixel] = min(range(count), key=lambda i: sum((pixel[j] - palette[i][j]) ** 2 for j in range(4)))
        indices.append(cache[pixel])
    raw = bytearray(payload[offset + 16:offset + length])
    for y in range(height):
        row = indices[y * width:(y + 1) * width]
        for x in range(stride):
            target = ((y // 8) * (stride // 16) + x // 16) * 128 + (y % 8) * 16 + x % 16 if stride >= 16 and height >= 8 else y * stride + x
            if target >= len(raw):
                raise ValueError('Indexed storage outside resource')
            if kind == 0x5c:
                raw[target] = row[x * 2] | ((row[x * 2 + 1] if x * 2 + 1 < width else 0) << 4)
            else:
                raw[target] = row[x]
    return payload[:offset + 16] + bytes(raw) + payload[offset + length:]


def replace_bgr565_texture(payload, image):
    """Observed linear 16-bit boot-screen texture, preserving all headers."""
    offset, kind, length, width, height = image_header(payload)
    if kind != 0x58 or length - 16 != width * height * 2:
        raise ValueError('Expected linear BGR565 SHPM texture')
    image = image.convert('RGB').resize((width, height), Image.Resampling.LANCZOS)
    values = [round(r * 31 / 255) | (round(g * 63 / 255) << 5) | (round(b * 31 / 255) << 11) for r, g, b in image.getdata()]
    raw = struct.pack('<%dH' % len(values), *values)
    return payload[:offset + 16] + raw + payload[offset + length:]
