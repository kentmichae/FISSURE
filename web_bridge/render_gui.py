#!/usr/bin/env python3
"""Generate a clean PNG screenshot of the FISSURE Web GUI."""
from PIL import Image, ImageDraw, ImageFont
import math, os

W, H = 1280, 800
bg = (10, 14, 23)
dark_tab = (17, 24, 39)
dark_card = (26, 35, 50)
dark_input = (13, 19, 32)
cyan = (6, 182, 212)
cyan_dim = (8, 145, 178)
green = (16, 185, 129)
yellow = (245, 158, 11)
red = (239, 68, 68)
white = (226, 232, 240)
gray = (148, 163, 184)
mid_grey = (100, 116, 139)
border = (30, 45, 61)
border_lt = (42, 63, 85)

im = Image.new('RGB', (W, H), bg)
d = ImageDraw.Draw(im)

# Helper: draw filled rounded rect helper
def rr(x0, y0, x1, y1, r=6, fill=dark_input, outline=border, w=1):
    d.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=outline, width=w)

# ==================== TOP BAR ====================
rr(0, 0, W, 42, fill=dark_tab, outline=border, w=1)

# Green status dot (connected)
d.ellipse([15, 15, 30, 30], fill=green)
d.text((40, 14), 'FISSURE', fill=cyan, font=ImageFont.load_default(size=18))

# Stats pills with values
stat_pairs = [
    ('HB:', 490, 15, '142', green),
    ('Messages:', 730, 15, '89', green),
    ('Sessions:', 920, 12, '0', yellow),
    ('Attacks:', 1080, 15, '2', cyan),
]
for txt, sx, sy, val, vc in stat_pairs:
    d.text((sx, sy), txt, fill=mid_grey, font=ImageFont.load_default(size=12))
    d.text((sx + 45, sy), val, fill=vc, font=ImageFont.load_default(size=12))

# Reconnect button
rr(1190, 10, 1230, 30, fill=dark_card, outline=border, w=1)
d.text((1205, 15), '⎈', fill=gray, font=ImageFont.load_default(size=14))

# ==================== LEFT SIDEBAR ====================
rr(0, 42, 220, H, fill=dark_tab, outline=border, w=1)

# Nav items
nav = [
    ('⊞', 'System', 65, True),
    ('◉', 'Signals', 105, False),
    ('◎', 'Attacks', 145, False),
    ('◇', 'SOI Data', 185, False),
    ('▤', 'Console', 225, False),
]
for icon, name, y, active in nav:
    c = cyan if active else border
    f = dark_card if active else dark_tab
    rr(5, y, 215, y + 36, r=4, fill=f, outline=c, w=2 if active else 1)
    d.text((32, y + 12), name, fill=cyan if active else gray, font=ImageFont.load_default(size=12))

# Control panels
# Panel 1: Session Control
pp = 280
d.rectangle([10, pp, 210, pp + 80], fill=dark_card)
rr(10, pp, 210, pp + 80, r=6, fill=dark_card, outline=border)
d.text((20, pp + 8), 'Session Control', fill=gray, font=ImageFont.load_default(size=11))

rr(20, pp + 28, 100, pp + 54, r=4, fill=cyan_dim, outline=cyan)
d.text((36, pp + 38), '▶ Start', fill=white, font=ImageFont.load_default(size=11))

rr(115, pp + 28, 200, pp + 54, r=4, fill=(100,30,30), outline=red)
d.text((128, pp + 38), '⏹ Stop', fill=red, font=ImageFont.load_default(size=11))

# Panel 2: Signal Acquisition
sp = 380
rr(10, sp, 210, sp + 130, r=6, fill=dark_card, outline=border)
d.text((20, sp + 8), 'Signal Acquisition', fill=gray, font=ImageFont.load_default(size=11))

rr(20, sp + 28, 190, sp + 54, r=4, fill=dark_input, outline=border)
d.text((25, sp + 37), '2412', fill=gray, font=ImageFont.load_default(size=11))
d.text((20, sp + 60), 'Center Freq (MHz)', fill=mid_grey, font=ImageFont.load_default(size=10))

rr(20, sp + 68, 190, sp + 94, r=4, fill=dark_input, outline=border)
d.text((25, sp + 77), '20', fill=gray, font=ImageFont.load_default(size=11))
d.text((20, sp + 100), 'Bandwidth (MHz)', fill=mid_grey, font=ImageFont.load_default(size=10))

rr(20, sp + 108, 190, sp + 128, r=4, fill=cyan_dim, outline=cyan)
d.text((40, sp + 113), 'Set Frequency', fill=white, font=ImageFont.load_default(size=11))

# Panel 3: Attack Config
ap = 540
rr(10, ap, 210, ap + 130, r=6, fill=dark_card, outline=border)
d.text((20, ap + 8), 'Attack Configuration', fill=gray, font=ImageFont.load_default(size=11))

rr(20, ap + 28, 190, ap + 54, r=4, fill=dark_input, outline=border)
d.text((25, ap + 37), 'Signal Deception ▾', fill=gray, font=ImageFont.load_default(size=11))
d.text((20, ap + 60), 'Attack Type', fill=mid_grey, font=ImageFont.load_default(size=10))

rr(20, ap + 70, 190, ap + 96, r=4, fill=dark_input, outline=border)
d.text((25, ap + 79), '2412', fill=gray, font=ImageFont.load_default(size=11))
d.text((20, ap + 102), 'Target Freq (MHz)', fill=mid_grey, font=ImageFont.load_default(size=10))

rr(20, ap + 108, 190, ap + 128, r=4, fill=(120,35,35), outline=red)
d.text((50, ap + 113), 'Launch Attack', fill=red, font=ImageFont.load_default(size=11))

# ==================== MAIN VIEW ====================
# View tab headers
rr(60, 57, W + 1, 83, fill=dark_tab, outline=border)
view_tabs = [('System', 85, False), ('Signals', 170, True), ('Attacks', 260, False), ('SOI', 335, False), ('Console', 390, False)]
for name, xs, active in view_tabs:
    d.text((xs, 59), name, fill=cyan if active else mid_grey, font=ImageFont.load_default(size=11))
    if active:
        d.line([(xs, 85), (xs + len(name) * 8 + 10, 85)], fill=cyan, width=2)

# Divider line
d.line([(80, 83), (W, 83)], fill=border, width=1)

# Toolbar
d.text((100, 93), 'Spectrum', fill=cyan, font=ImageFont.load_default(size=10))
d.line([(165, 93), (175, 93)], fill=gray, width=1)
d.text((185, 93), 'Constellation', fill=gray, font=ImageFont.load_default(size=10))
d.line([(300, 93), (310, 93)], fill=gray, width=1)
d.text((320, 93), '2.4 GHz ▾', fill=gray, font=ImageFont.load_default(size=10))

# Spectrum Analyzer
chart_x, chart_y = 95, 120
chart_w, chart_h = 1080, 340

rr(chart_x, chart_y, chart_x + chart_w, chart_y + chart_h, r=8, fill=dark_card, outline=border, w=1)

# Chart title
d.text((chart_x + 15, chart_y + 10), 'Signal Spectrum Analyzer', fill=gray, font=ImageFont.load_default(size=12))
d.text((chart_x + 280, chart_y + 10), 'Center: 2412 MHz  |  BW: 20 MHz  |  RBW: 1 MHz', fill=mid_grey, font=ImageFont.load_default(size=10))

# Grid
for i in range(9):
    gx = chart_x + (i * chart_w // 8)
    d.line([(gx, chart_y + 30), (gx, chart_y + chart_h - 5)], fill=(border_lt[0]//2, border_lt[1]//2, border_lt[2]//2), width=1)

for i in range(7):
    gy = chart_y + (i * (chart_h - 35) // 6)
    d.line([(chart_x + 45, gy), (chart_x + chart_w - 10, gy)], fill=(border_lt[0]//2, border_lt[1]//2, border_lt[2]//2), width=1)
    d.text((chart_x + 5, gy - 3), str(100 - i * 15), fill=mid_grey, font=ImageFont.load_default(size=8))

# Frequency labels
freq_labels = ['0', '250', '500', '750', '1000', '1250', '1500', '1750', '2000', '2250', '2500']
for i, f in enumerate(freq_labels):
    fx = chart_x + (i * chart_w // (len(freq_labels) - 1))
    d.text((fx - 8, chart_y + chart_h - 8), f, fill=mid_grey, font=ImageFont.load_default(size=9))

# Signal peaks (simulate real-looking spectrum)
signal_peaks = [(915, 0.42), (1575, 0.38), (2412, 0.45)]
spectrum_line = []
for i in range(chart_w - 10):
    f = i * 2500 / (chart_w - 10)
    amplitude = 0.02  # noise floor
    for sf, sp in signal_peaks:
        amp = sp * math.exp(-((f - sf) ** 2) / (2 * 200**2))
        amplitude += amp
    y = chart_y + chart_h - 30 - amplitude * (chart_h - 60)
    spectrum_line.append((chart_x + 2 + i, y))

# Draw glow (thick cyan line with blur)
for j in range(-2, 3):
    offset_line = [(x, y + j * 2) for x, y in spectrum_line]
    d.line(offset_line, fill=(6, 182, 212, 40) if len(offset_line[0]) > 0 else (100, 100, 100), width=4)

# Draw main signal line (cyan)
d.line(spectrum_line, fill=cyan, width=2)

# Mark peaks
for sf, sp in signal_peaks:
    px = chart_x + (sf / 2500) * chart_w
    py = chart_y + chart_h - 30 - sp * (chart_h - 60)
    d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=cyan, outline=bg, width=2)
    d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=bg)
    # Label
    d.text((px + 8, py - 8), f'{sf} MHz {sp*100:.0f}%', fill=cyan, font=ImageFont.load_default(size=9))

# Signal data table (right column)
sig_data = [
    ('Freq (MHz)', 'Modulation', 'Power (dBm)', 'Confidence'),
    ('2412.0', 'BPSK', '-45.2', '92.1%'),
    ('1575.4', 'QPSK', '-38.1', '76.3%'),
    ('915.0', 'FSK', '-41.7', '84.5%'),
    ('2412.0', 'BPSK', '-42.5', '89.0%'),
    ('1575.4', 'QPSK', '-35.8', '71.2%'),
]
sig_x, sig_y = 1000, 120
for i, row in enumerate(sig_data):
    row_h = 24 if i > 0 else 26
    bg_c = dark_card if i % 2 == 0 else (30, 42, 56)
    if i == 0:
        bg_c = (20, 30, 42)
    rr(sig_x + 10, sig_y + i * (row_h + 3), sig_x + 230, sig_y + i * (row_h + 3) + row_h, r=4, fill=bg_c, outline=border)
    for j, cell in enumerate(row):
        cx = sig_x + 20 + j * 48
        col_color = cyan if i == 0 else (green if j >= 3 else (cyan if j == 1 else gray))
        d.text((cx, sig_y + i * (row_h + 3) + (row_h - 12) // 2), cell, fill=col_color, font=ImageFont.load_default(size=9))

# ==================== BOTTOM SECTION ====================
bot_y = 485

# Attack Status panel
rr(80, bot_y, 640, bot_y + 180, r=8, fill=dark_card, outline=border, w=1)
d.text((100, bot_y + 12), 'Active Attacks', fill=gray, font=ImageFont.load_default(size=13))

atk_data = [
    ('Signal Deception', '2412 MHz', 'BPSK', 'Active', green),
    ('Jamming', '1575 MHz', 'QPSK', 'Active', green),
    ('Spoofing', '915 MHz', 'FSK', 'Pending', yellow),
]
for i, (name, freq, mod, status, sc) in enumerate(atk_data):
    y = bot_y + 36 + i * 52
    rr(95, y, 625, y + 44, r=4, fill=dark_input, outline=border)
    d.text((110, y + 10), name, fill=white, font=ImageFont.load_default(size=11))
    d.text((110, y + 27), freq, fill=cyan, font=ImageFont.load_default(size=10))
    d.text((250, y + 10), mod, fill=gray, font=ImageFont.load_default(size=10))
    d.ellipse([550, y + 10, 565, y + 25], fill=sc)
    d.text((570, y + 10), status, fill=sc, font=ImageFont.load_default(size=10))

# SOI Data panel
rr(675, bot_y, 1200, bot_y + 180, r=8, fill=dark_card, outline=border, w=1)
d.text((695, bot_y + 12), 'Signal of Interest (SOI)', fill=gray, font=ImageFont.load_default(size=13))
rr(695, bot_y + 32, 750, bot_y + 56, r=4, fill=cyan_dim, outline=cyan)
d.text((698, bot_y + 38), '+ Import', fill=white, font=ImageFont.load_default(size=10))

soi_rows = [
    ('2412 MHz', 'BPSK', '45.2 dBm', '92%', green),
    ('1575 MHz', 'QPSK', '38.1 dBm', '76%', yellow),
    ('915 MHz', 'FSK', '41.7 dBm', '84%', green),
]
for i, (fr, md, pw, cn, cc) in enumerate(soi_rows):
    y = bot_y + 48 + i * 42
    rr(695, y, 1185, y + 34, r=4, fill=dark_input, outline=border)
    d.text((705, y + 8), fr, fill=white, font=ImageFont.load_default(size=10))
    d.text((850, y + 8), md, fill=cyan, font=ImageFont.load_default(size=10))
    d.text((1000, y + 8), pw, fill=gray, font=ImageFont.load_default(size=10))
    d.ellipse([1150, y + 5, 1165, y + 20], fill=cc)
    d.text((1168, y + 5), cn, fill=cc, font=ImageFont.load_default(size=10))

# Bottom status bar
d.rectangle([0, H - 28, W, H], fill=dark_tab, outline=border)
d.text((20, H - 18), 'FISSURE v2.4.0 | HIPRFISR: Connected | ZMQ: OK | DB: postgres://myuser@localhost:5431/postgres', fill=mid_grey, font=ImageFont.load_default(size=10))

# Timestamp
d.text((W - 180, H - 18), '2026-06-26 14:23:47 UTC', fill=mid_grey, font=ImageFont.load_default(size=10))

# Save
out = '/home/nebulaone/spark-dev-workspace/FISSURE/fissure-webgui.png'
im.save(out, 'PNG')
print("Screenshot saved:", out)
