# Procedural demo photos for the walkthrough: fabrics, garment designs, bundles, boxes, illustrated avatars.
import math, random, json, base64, io, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops
OUT = sys.argv[1]
S = 480
def fold_shade(img, freq=3, amp=0.22, seed=0):
    random.seed(seed)
    w, h = img.size
    sh = Image.new('L', (w, h))
    px = sh.load()
    ph = random.random() * 6
    ang = random.uniform(-0.5, 0.5)
    for y in range(h):
        for x in range(w):
            t = (x * math.cos(ang) + y * math.sin(ang)) / w
            v = math.sin(t * math.pi * 2 * freq + ph) * 0.6 + math.sin(t * math.pi * 2 * freq * 2.3 + ph * 2) * 0.4
            px[x, y] = int(255 * (1 - amp / 2 + amp / 2 * v))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    return ImageChops.multiply(img, Image.merge('RGB', (sh, sh, sh)))
def weave(img, a=10):
    w, h = img.size
    n = Image.effect_noise((w, h), 18).convert('L')
    return Image.blend(img, ImageChops.multiply(img, Image.merge('RGB', (n, n, n)).point(lambda v: 200 + v // 5)), 0.35)
def floral(bg, fg, acc, seed):
    random.seed(seed); im = Image.new('RGB', (S, S), bg); d = ImageDraw.Draw(im)
    for i in range(0, S + 60, 70):
        for j in range(0, S + 60, 70):
            cx, cy = i + (35 if (j // 70) % 2 else 0) + random.randint(-6, 6), j + random.randint(-6, 6)
            for k in range(6):
                a = k * math.pi / 3
                d.ellipse([cx + 14 * math.cos(a) - 9, cy + 14 * math.sin(a) - 9, cx + 14 * math.cos(a) + 9, cy + 14 * math.sin(a) + 9], fill=fg)
            d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=acc)
            d.line([cx + 22, cy + 18, cx + 34, cy + 30], fill=acc, width=3)
    return im
def stripes(c1, c2, c3, seed):
    im = Image.new('RGB', (S, S), c1); d = ImageDraw.Draw(im)
    for x in range(-S, S * 2, 48):
        d.polygon([(x, 0), (x + 18, 0), (x + 18 + S * 0.3, S), (x + S * 0.3, S)], fill=c2)
        d.polygon([(x + 26, 0), (x + 30, 0), (x + 30 + S * 0.3, S), (x + 26 + S * 0.3, S)], fill=c3)
    return im
def dots(bg, fg, seed):
    im = Image.new('RGB', (S, S), bg); d = ImageDraw.Draw(im)
    for i in range(0, S + 40, 32):
        for j in range(0, S + 40, 32):
            o = 16 if (j // 32) % 2 else 0
            d.ellipse([i + o - 5, j - 5, i + o + 5, j + 5], fill=fg)
    return im
def checks(c1, c2, seed):
    im = Image.new('RGB', (S, S), c1); d = ImageDraw.Draw(im)
    for x in range(0, S, 60):
        d.rectangle([x, 0, x + 24, S], fill=c2)
    ov = Image.new('RGB', (S, S), c1); d2 = ImageDraw.Draw(ov)
    for y in range(0, S, 60):
        d2.rectangle([0, y, S, y + 24], fill=c2)
    return Image.blend(im, ov, 0.5)
def zigzag(c1, c2, c3, seed):
    im = Image.new('RGB', (S, S), c1); d = ImageDraw.Draw(im)
    for y in range(-40, S + 40, 46):
        pts = [(x, y + (18 if (x // 30) % 2 else 0)) for x in range(-30, S + 60, 30)]
        d.line(pts, fill=c2, width=12); d.line([(x, yy + 14) for x, yy in pts], fill=c3, width=4)
    return im
def paisley(bg, fg, acc, seed):
    random.seed(seed); im = Image.new('RGB', (S, S), bg); d = ImageDraw.Draw(im)
    for i in range(0, S + 80, 90):
        for j in range(0, S + 80, 90):
            cx, cy = i + (45 if (j // 90) % 2 else 0), j
            d.ellipse([cx - 22, cy - 14, cx + 18, cy + 22], fill=fg)
            d.ellipse([cx + 4, cy - 30, cx + 20, cy - 8], fill=fg)
            d.ellipse([cx - 10, cy - 2, cx + 6, cy + 12], fill=acc)
            for k in range(8):
                a = k * math.pi / 4
                d.ellipse([cx + 34 * math.cos(a) - 3, cy + 34 * math.sin(a) - 3, cx + 34 * math.cos(a) + 3, cy + 34 * math.sin(a) + 3], fill=acc)
    return im
def solid(c):
    return Image.new('RGB', (S, S), c)
def finish(im, seed, freq=3):
    return weave(fold_shade(im, freq=freq, seed=seed))
fabrics = {
 'f_maroon_floral': finish(floral((122, 22, 44), (236, 170, 92), (250, 236, 210), 1), 1),
 'f_blue_stripe': finish(stripes((236, 241, 250), (36, 72, 150), (240, 180, 60), 2), 2),
 'f_yellow_dots': finish(dots((242, 190, 40), (160, 40, 40), 3), 3),
 'f_green_paisley': finish(paisley((22, 96, 74), (240, 220, 170), (210, 80, 60), 4), 4),
 'f_pink_floral': finish(floral((246, 196, 208), (250, 250, 250), (214, 72, 120), 5), 5),
 'f_black_check': finish(checks((30, 30, 34), (190, 30, 40), 6), 6),
 'f_teal_zigzag': finish(zigzag((20, 120, 130), (250, 240, 220), (240, 150, 40), 7), 7),
 'f_mustard': finish(solid((206, 150, 40)), 8, freq=4),
 'f_white_chikan': finish(dots((246, 244, 236), (220, 214, 200), 9), 9),
 'f_navy_paisley': finish(paisley((24, 34, 80), (120, 160, 220), (250, 210, 120), 10), 10),
 'f_rust': finish(solid((176, 76, 40)), 11, freq=5),
 'f_lilac_stripe': finish(stripes((210, 190, 236), (120, 80, 170), (255, 255, 255), 12), 12),
}
def roll(fab, seed):
    """A fabric roll lying on a cutting table, seen from above."""
    random.seed(seed)
    im = Image.new('RGB', (S, S), (190, 160, 120)); d = ImageDraw.Draw(im)
    for y in range(0, S, 7):  # wood grain
        d.line([(0, y + random.randint(-2, 2)), (S, y + random.randint(-2, 2))], fill=(178 + random.randint(-8, 8), 146, 104), width=2)
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    sheet = fab.resize((int(S * 0.86), int(S * 0.62)))
    m = Image.new('L', sheet.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, sheet.size[0], sheet.size[1]], 40, fill=255)
    shadow = Image.new('L', (S, S), 0); ImageDraw.Draw(shadow).rounded_rectangle([40, 112, 40 + sheet.size[0] + 10, 112 + sheet.size[1] + 14], 40, fill=120)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    im = Image.composite(Image.new('RGB', (S, S), (80, 60, 40)), im, shadow)
    im.paste(sheet, (34, 96), m)
    # roll end
    end = fab.resize((150, sheet.size[1])).transpose(Image.ROTATE_90).resize((150, sheet.size[1]))
    em = Image.new('L', (150, sheet.size[1]), 0); ImageDraw.Draw(em).ellipse([0, 0, 150, sheet.size[1]], fill=255)
    im.paste(end, (S - 190, 96), em)
    d = ImageDraw.Draw(im)
    cx, cy = S - 115, 96 + sheet.size[1] // 2
    for r in range(70, 6, -9):
        d.ellipse([cx - r * 0.5, cy - r * 1.9, cx + r * 0.5, cy + r * 1.9], outline=(0, 0, 0, 60), width=1)
    d.ellipse([cx - 9, cy - 22, cx + 9, cy + 22], fill=(120, 90, 60))
    return im
def garment(kind, fab, seed):
    im = Image.new('RGB', (S, S), (246, 241, 232)); d = ImageDraw.Draw(im)
    for y in range(S):
        d.line([(0, y), (S, y)], fill=(246 - y // 30, 241 - y // 30, 232 - y // 28))
    m = Image.new('L', (S, S), 0); md = ImageDraw.Draw(m)
    c = S // 2
    if kind == 'kurta':
        md.polygon([(c - 60, 60), (c - 20, 50), (c, 78), (c + 20, 50), (c + 60, 60), (c + 130, 130), (c + 100, 168), (c + 64, 136), (c + 76, 420), (c - 76, 420), (c - 64, 136), (c - 100, 168), (c - 130, 130)], fill=255)
    elif kind == 'palazzo':
        md.polygon([(c - 80, 60), (c + 80, 60), (c + 150, 430), (c + 12, 430), (c, 170), (c - 12, 430), (c - 150, 430)], fill=255)
    elif kind == 'top':
        md.polygon([(c - 56, 80), (c - 18, 70), (c, 98), (c + 18, 70), (c + 56, 80), (c + 110, 120), (c + 88, 160), (c + 60, 140), (c + 100, 360), (c - 100, 360), (c - 60, 140), (c - 88, 160), (c - 110, 120)], fill=255)
    elif kind == 'anarkali':
        md.polygon([(c - 50, 50), (c - 18, 44), (c, 70), (c + 18, 44), (c + 50, 50), (c + 120, 120), (c + 96, 150), (c + 58, 124), (c + 56, 190), (c + 180, 440), (c - 180, 440), (c - 56, 190), (c - 58, 124), (c - 96, 150), (c - 120, 120)], fill=255)
    elif kind == 'frock':
        md.polygon([(c - 40, 90), (c - 14, 84), (c, 104), (c + 14, 84), (c + 40, 90), (c + 80, 120), (c + 60, 150), (c + 44, 140), (c + 46, 200), (c + 140, 380), (c - 140, 380), (c - 46, 200), (c - 44, 140), (c - 60, 150), (c - 80, 120)], fill=255)
    elif kind == 'coord':
        md.polygon([(c - 60, 40), (c - 20, 34), (c, 56), (c + 20, 34), (c + 60, 40), (c + 116, 92), (c + 92, 126), (c + 62, 104), (c + 64, 220), (c - 64, 220), (c - 62, 104), (c - 92, 126), (c - 116, 92)], fill=255)
        md.polygon([(c - 66, 236), (c + 66, 236), (c + 84, 450), (c + 10, 450), (c, 300), (c - 10, 450), (c - 84, 450)], fill=255)
    sh = m.filter(ImageFilter.GaussianBlur(10)).point(lambda v: v * 0.35)
    im = Image.composite(Image.new('RGB', (S, S), (90, 80, 70)), im, ImageChops.offset(sh, 8, 10))
    im.paste(fab.resize((S, S)), (0, 0), m)
    d = ImageDraw.Draw(im)
    if kind in ('kurta', 'anarkali', 'top', 'coord'):
        for k in range(4):
            d.ellipse([c - 4, 110 + k * 24, c + 4, 118 + k * 24], fill=(212, 175, 55))
    return im
def bundles(fab, n, seed):
    random.seed(seed)
    im = Image.new('RGB', (S, S), (214, 206, 192)); d = ImageDraw.Draw(im)
    for y in range(0, S, 40):
        d.line([(0, y), (S, y)], fill=(200, 192, 178), width=2)
    cols = 3 if n > 4 else 2
    for i in range(n):
        x = 30 + (i % cols) * (420 // cols); y = 50 + (i // cols) * 140
        w, h = 420 // cols - 16, 110
        piece = fab.resize((w, h))
        d.rectangle([x + 6, y + 8, x + w + 6, y + h + 8], fill=(150, 140, 126))
        im.paste(piece, (x, y))
        d = ImageDraw.Draw(im)
        for k in range(1, 6):
            d.line([(x, y + k * h // 6), (x + w, y + k * h // 6)], fill=(0, 0, 0), width=1)
        d.line([(x + w // 2, y - 2), (x + w // 2, y + h + 2)], fill=(240, 230, 210), width=4)
    return im.filter(ImageFilter.GaussianBlur(0.6))
def boxes(seed):
    random.seed(seed); im = Image.new('RGB', (S, S), (226, 222, 214)); d = ImageDraw.Draw(im)
    for r in range(3):
        for c in range(3 - (r == 0)):
            x, y = 40 + c * 140 + (70 if r == 0 else 0), 300 - r * 120
            d.rectangle([x, y, x + 130, y + 110], fill=(196, 150, 100), outline=(150, 108, 70), width=3)
            d.rectangle([x + 55, y, x + 75, y + 110], fill=(214, 186, 140))
            d.rectangle([x + 20, y + 70, x + 50, y + 92], fill=(250, 250, 245))
    return fold_shade(im, freq=1, amp=0.1, seed=seed)
def avatar(skin, hair, shirt, bg, long_hair, seed):
    im = Image.new('RGB', (S, S), bg); d = ImageDraw.Draw(im)
    c = S // 2
    d.ellipse([c - 170, 340, c + 170, 640], fill=shirt)
    d.rectangle([c - 34, 270, c + 34, 350], fill=tuple(int(v * 0.9) for v in skin))
    if long_hair: d.rounded_rectangle([c - 112, 120, c + 112, 380], 90, fill=hair)
    d.ellipse([c - 92, 110, c + 92, 310], fill=skin)
    d.chord([c - 98, 92, c + 98, 250], 180, 360, fill=hair)
    d.ellipse([c - 46, 200, c - 26, 222], fill=(40, 30, 30)); d.ellipse([c + 26, 200, c + 46, 222], fill=(40, 30, 30))
    d.arc([c - 34, 236, c + 34, 274], 20, 160, fill=(150, 60, 60), width=6)
    return fold_shade(im, freq=1, amp=0.08, seed=seed)
out = {}
def save(name, im, q=78, size=360):
    im = im.convert('RGB').resize((size, size), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=q)
    im.save(f'{OUT}/{name}.jpg', quality=90)
    out[name] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
for k, v in fabrics.items():
    save('roll_' + k[2:], roll(v, hash(k) % 100))
G = [('kurta', 'f_maroon_floral'), ('palazzo', 'f_navy_paisley'), ('top', 'f_yellow_dots'), ('anarkali', 'f_pink_floral'), ('frock', 'f_teal_zigzag'), ('coord', 'f_blue_stripe'), ('kurta', 'f_green_paisley'), ('top', 'f_lilac_stripe')]
for i, (k, f) in enumerate(G):
    save(f'design_{i+1}_{k}', garment(k, fabrics[f], i))
for i, f in enumerate(['f_maroon_floral', 'f_blue_stripe', 'f_green_paisley', 'f_pink_floral', 'f_black_check', 'f_yellow_dots']):
    save(f'bundle_{i+1}', bundles(fabrics[f], [6, 4, 5, 6, 3, 4][i], i))
save('boxes_1', boxes(1)); save('boxes_2', boxes(2))
A = [((233, 190, 160), (40, 28, 24), (36, 110, 160), (220, 232, 240), True), ((198, 150, 110), (30, 24, 20), (190, 70, 60), (240, 228, 214), False),
     ((176, 124, 90), (24, 20, 18), (60, 140, 90), (226, 236, 222), False), ((222, 178, 140), (50, 34, 26), (150, 80, 160), (238, 226, 238), True),
     ((160, 112, 80), (20, 18, 16), (210, 150, 40), (240, 236, 220), False)]
for i, a in enumerate(A):
    save(f'avatar_{i+1}', avatar(*a, i))
json.dump(out, open(f'{OUT}/images.json', 'w'))
print(len(out), 'images', sum(len(v) for v in out.values()) // 1024, 'KB')
