"""Génère icons/icon-192.png et icon-512.png sans dépendance (PNG écrit à la main)."""
import zlib, struct, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
def png(size, path):
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            r = size * 0.22
            cx = min(max(x, r), size - r); cy = min(max(y, r), size - r)
            if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                row += b"\x00\x00\x00\x00"; continue
            col = (0x0F, 0x7A, 0x4F) if x < size / 2 else (0xC9, 0x9A, 0x1F)
            d = math.hypot(x - size / 2, y - size * 0.42)
            if d < size * 0.2: col = (255, 255, 255)
            if d < size * 0.085: col = (0xB4, 0x23, 0x2C)
            if size * 0.6 < y < size * 0.85 and abs(x - size / 2) < (size * 0.85 - y) * 0.6: col = (255, 255, 255)
            row += bytes(col) + b"\xff"
        rows.append(bytes(row))
    raw = b"".join(rows)
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    open(path, "wb").write(data)
for s in (192, 512):
    png(s, os.path.join(HERE, "..", "icons", f"icon-{s}.png"))
print("icons ok")
