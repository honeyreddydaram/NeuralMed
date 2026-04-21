"""Generate NeuralMed logo — PNG with transparent background."""
from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1200, 400
img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# ── Colours ────────────────────────────────────────────────────────────────────
BLUE   = (0, 87, 184)
CYAN   = (0, 180, 220)
WHITE  = (255, 255, 255)
DARK   = (10, 20, 40)

# ── Neural network icon (left side) ───────────────────────────────────────────
cx, cy = 180, 200
nodes = {
    'i1': (cx-110, cy-70), 'i2': (cx-110, cy),    'i3': (cx-110, cy+70),
    'h1': (cx,     cy-90), 'h2': (cx,     cy-30),
    'h3': (cx,     cy+30), 'h4': (cx,     cy+90),
    'o1': (cx+110, cy-45), 'o2': (cx+110, cy+45),
}
edges = [
    ('i1','h1'),('i1','h2'),('i1','h3'),
    ('i2','h1'),('i2','h2'),('i2','h3'),('i2','h4'),
    ('i3','h2'),('i3','h3'),('i3','h4'),
    ('h1','o1'),('h2','o1'),('h2','o2'),
    ('h3','o1'),('h3','o2'),('h4','o2'),
]

# Draw edges
for a, b in edges:
    x1,y1 = nodes[a]; x2,y2 = nodes[b]
    draw.line([(x1,y1),(x2,y2)], fill=(*CYAN, 80), width=2)

# Draw nodes
for key, (x, y) in nodes.items():
    r = 14 if key.startswith('h') else 12
    color = BLUE if key.startswith('o') else CYAN
    draw.ellipse([x-r, y-r, x+r, y+r], fill=(*color, 255),
                 outline=(*WHITE, 200), width=2)

# ── Cross / plus medical symbol ────────────────────────────────────────────────
mx, my, ms = cx+110+55, cy, 28
draw.rectangle([mx-6, my-ms, mx+6, my+ms], fill=(*BLUE, 255))
draw.rectangle([mx-ms, my-6, mx+ms, my+6], fill=(*BLUE, 255))

# ── Text ───────────────────────────────────────────────────────────────────────
try:
    font_bold  = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 110)
    font_light = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 38)
    font_tag   = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 30)
except:
    font_bold  = ImageFont.load_default()
    font_light = font_bold
    font_tag   = font_bold

text_x = cx + 200
# "Neural" in dark blue, "Med" in cyan
draw.text((text_x, 60), 'Neural', font=font_bold, fill=(*DARK, 255))
bbox = draw.textbbox((text_x, 60), 'Neural', font=font_bold)
med_x = bbox[2]
draw.text((med_x, 60), 'Med', font=font_bold, fill=(*BLUE, 255))

# Tagline
draw.text((text_x, 200), 'AI-Powered Clinical Screening Platform', font=font_light, fill=(*DARK, 180))

# Underline accent
line_y = 195
draw.rectangle([text_x, line_y, text_x+530, line_y+3], fill=(*CYAN, 255))

# Pills / tags
tags = ['ML · Deep Learning', 'Gemini AI', 'Flask']
tx = text_x
ty = 255
for tag in tags:
    bb = draw.textbbox((tx, ty), tag, font=font_tag)
    pw, ph = bb[2]-bb[0]+20, bb[3]-bb[1]+10
    draw.rounded_rectangle([tx, ty, tx+pw, ty+ph], radius=12,
                            fill=(*BLUE, 30), outline=(*BLUE, 180), width=2)
    draw.text((tx+10, ty+5), tag, font=font_tag, fill=(*BLUE, 230))
    tx += pw + 16

out = '/Users/honey/Downloads/Deep-Learning-Project/static/images/neuralmed_logo.png'
img.save(out, 'PNG')
print(f'Logo → {out}')

# Also save a white-background version for the poster
img_white = Image.new('RGBA', (W, H), (255, 255, 255, 255))
img_white.paste(img, mask=img.split()[3])
img_white.save(out.replace('.png', '_white.png'), 'PNG')
print(f'Logo (white bg) → {out.replace(".png","_white.png")}')
