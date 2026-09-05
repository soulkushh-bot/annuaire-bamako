"""Génère icons/icon-192.png et icon-512.png sans dépendance (PNG écrit à la main).
La marque reprend les trois bandes du drapeau malien, avec le repère de lieu en réserve.
"""
import zlib, struct, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
VERT, OR, ROUGE, BLANC = (0x14, 0xB5, 0x3A), (0xFC, 0xD1, 0x16), (0xCE, 0x11, 0x26), (255, 255, 255)

def png(size, path):
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            r = size * 0.22                       # coins arrondis
            cx = min(max(x, r), size - r); cy = min(max(y, r), size - r)
            if (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                row += b"\x00\x00\x00\x00"; continue
            t = x / size                          # trois bandes égales
            col = VERT if t < 1 / 3 else (OR if t < 2 / 3 else ROUGE)
            if math.hypot(x - size / 2, y - size * 0.4375) < size * 0.172:   # disque du repère
                col = BLANC
            if size * 0.55 < y < size * 0.83 and abs(x - size / 2) < (size * 0.83 - y) * 0.62:
                col = BLANC                        # pointe du repère
            row += bytes(col) + b"\xff"
        rows.append(bytes(row))
    raw = b"".join(rows)
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    data = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    open(path, "wb").write(data)

for s in (192, 512):
    png(s, os.path.join(HERE, "..", "icons", f"icon-{s}.png"))
print("icônes tricolores générées")
