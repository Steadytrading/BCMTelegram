
from flask import Flask, render_template_string, request, send_file
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random, os, io

app = Flask(__name__)
WIDTH, HEIGHT = 1080, 1350

PROFIT_TEXTS = [
    "Disciplined execution. Strong result today.",
    "Another solid session with controlled risk.",
    "High probability entries delivered today.",
    "Steady performance with capital protection first.",
    "Clean execution and a strong finish for the day.",
]
LOSS_TEXTS = [
    "Small setback. Risk stayed controlled.",
    "Capital protection comes before aggression.",
    "A defensive day with discipline intact.",
    "Not every day is green. Risk management held.",
    "Protected the account and stayed focused.",
]
PROFIT_BADGES = ["LOW RISK STRATEGY","CONSISTENT GAINS","DISCIPLINED EXECUTION","PRECISION ENTRIES"]
LOSS_BADGES = ["CAPITAL PROTECTION","RISK MANAGED DAY","DEFENSIVE SESSION","CONTROLLED DRAWDOWN"]

HTML = """
<!doctype html>
<html lang="sv"><head><meta charset="utf-8"><title>BCM Trading Generator V3</title>
<style>
body{font-family:Arial,sans-serif;background:radial-gradient(circle at top,#13203d,#08101e 55%);color:#fff;padding:40px;margin:0}
.box{max-width:620px;margin:auto;background:rgba(12,18,34,.96);padding:34px;border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,.4);border:1px solid rgba(255,255,255,.07)}
h1{margin:0 0 10px 0;font-size:34px}p{color:#c5cee4;line-height:1.55}
label{display:block;margin-top:18px;margin-bottom:8px;font-weight:700}
input,button{width:100%;padding:15px 16px;border-radius:14px;border:none;font-size:16px;box-sizing:border-box}
input{background:#eef2ff}button{background:linear-gradient(135deg,#2d6cdf,#1d9bf0);color:white;cursor:pointer;font-weight:700;margin-top:18px}
</style></head><body><div class="box"><h1>BCM Trading Generator V3</h1>
<p>Premium Telegram-resultatbild. Den här versionen fixar 500-felet i /generate.</p>
<form method="post" action="/generate"><label>Dagens resultat i %</label>
<input name="result" placeholder="t.ex. 3.74 eller -1.20" required>
<button type="submit">Generera Telegram-bild</button></form></div></body></html>
"""

def load_font(size, bold=False):
    paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def draw_centered(draw, text, y, font, fill):
    bbox = draw.textbbox((0,0), text, font=font)
    x = (WIDTH - (bbox[2]-bbox[0])) / 2
    draw.text((x,y), text, font=font, fill=fill)

def add_glow_text(base, text, y, font, text_fill, glow_fill, blur_radius=22):
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    gdraw = ImageDraw.Draw(glow)
    bbox = gdraw.textbbox((0,0), text, font=font)
    x = int((WIDTH - (bbox[2]-bbox[0])) / 2)
    gdraw.text((x,y), text, font=font, fill=glow_fill)
    glow = glow.filter(ImageFilter.GaussianBlur(blur_radius))
    base.alpha_composite(glow)
    ImageDraw.Draw(base).text((x,y), text, font=font, fill=text_fill)

def draw_candles(draw):
    baseline, start_x, candle_w, gap = 960, 85, 18, 14
    for i in range(26):
        x = start_x + i * (candle_w + gap)
        body_h = random.randint(50,190)
        wick_top = random.randint(18,65)
        wick_bottom = random.randint(18,65)
        green = random.choice([True,False,True])
        color = (37,211,102,125) if green else (255,82,82,125)
        top = baseline - body_h - random.randint(-100,100)
        bottom = top + body_h
        center_x = x + candle_w // 2
        draw.line((center_x, top-wick_top, center_x, bottom+wick_bottom), fill=color, width=3)
        draw.rounded_rectangle((x, top, x+candle_w, bottom), radius=4, fill=color)

def background():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8,12,24,255))
    px = img.load()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            px[x,y] = (8, 12 + int(26*y/HEIGHT), 24 + int(52*y/HEIGHT), 255)
    return img

def vignette(base):
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    odraw = ImageDraw.Draw(overlay)
    for i in range(130):
        odraw.rounded_rectangle((i,i,WIDTH-i,HEIGHT-i), radius=48, outline=(0,0,0,int(2.15*i)))
    base.alpha_composite(overlay)

def try_add_logo(base):
    for path in [os.path.join("assets","logo.png"),"logo.png"]:
        if os.path.exists(path):
            logo = Image.open(path).convert("RGBA")
            logo.thumbnail((500,250))
            base.alpha_composite(logo, ((WIDTH-logo.width)//2, 66))
            return True
    return False

def wrap_line(draw, text, font, max_width):
    words, lines, current = text.split(), [], ""
    for word in words:
        test = word if not current else current + " " + word
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2]-bbox[0] <= max_width:
            current = test
        else:
            if current: lines.append(current)
            current = word
    if current: lines.append(current)
    return lines

def generate_image(result_value):
    is_profit = result_value >= 0
    result_text = f"{result_value:+.2f}%"
    body_text = random.choice(PROFIT_TEXTS if is_profit else LOSS_TEXTS)
    badge_text = random.choice(PROFIT_BADGES if is_profit else LOSS_BADGES)

    base = background()
    draw = ImageDraw.Draw(base)
    for x in range(0, WIDTH, 54):
        draw.line((x,0,x,HEIGHT), fill=(40,70,110,36), width=1)
    for y in range(0, HEIGHT, 54):
        draw.line((0,y,WIDTH,y), fill=(40,70,110,36), width=1)

    light = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    ldraw = ImageDraw.Draw(light)
    ldraw.ellipse((140,220,940,1040), fill=(40,120,255,34))
    ldraw.ellipse((250,420,830,900), fill=((45,180,255,26) if is_profit else (255,80,80,24)))
    light = light.filter(ImageFilter.GaussianBlur(75))
    base.alpha_composite(light)

    draw_candles(draw)
    vignette(base)

    panel = Image.new("RGBA", (WIDTH, HEIGHT), (0,0,0,0))
    pdraw = ImageDraw.Draw(panel)
    pdraw.rounded_rectangle((85,360,WIDTH-85,1210), radius=34, fill=(12,20,36,92), outline=(255,255,255,18), width=2)
    base.alpha_composite(panel)

    added_logo = try_add_logo(base)
    draw = ImageDraw.Draw(base)
    title_font = load_font(38, True)
    result_font = load_font(168, True)
    body_font = load_font(40, False)
    badge_font = load_font(32, True)
    brand_font = load_font(34, True)
    small_font = load_font(27, False)

    if not added_logo:
        draw_centered(draw, "BCM TRADING", 96, load_font(62, True), (235,240,255,255))
    draw_centered(draw, "TODAY'S RESULT", 410, title_font, (212,223,247,235))
    add_glow_text(base, result_text, 485, result_font, (255,255,255,255), (40,210,110,165) if is_profit else (255,70,70,165))
    draw.rounded_rectangle((300,690,780,696), radius=8, fill=(42,210,115,230) if is_profit else (235,82,82,230))

    y = 748
    for line in wrap_line(draw, body_text, body_font, WIDTH-260)[:2]:
        draw_centered(draw, line, y, body_font, (230,236,248,225))
        y += 50
    y += 18
    for line in ["BCM Trading focuses on disciplined entries","strict risk management and steady execution."]:
        draw_centered(draw, line, y, small_font, (184,198,225,220))
        y += 40

    badge_bbox = draw.textbbox((0,0), badge_text, font=badge_font)
    badge_w = badge_bbox[2]-badge_bbox[0]
    bx1 = (WIDTH - badge_w)//2 - 30
    bx2 = (WIDTH + badge_w)//2 + 30
    by1 = 972
    by2 = by1 + (badge_bbox[3]-badge_bbox[1]) + 36
    draw.rounded_rectangle((bx1,by1,bx2,by2), radius=24, fill=(26,170,92,220) if is_profit else (186,58,58,220))
    draw_centered(draw, badge_text, by1+16, badge_font, (255,255,255,255))

    draw_centered(draw, "Copy trading available on Vantage", 1115, small_font, (192,203,228,210))
    draw_centered(draw, "BCM Trading", 1162, brand_font, (255,255,255,238))

    output = io.BytesIO()
    base.convert("RGB").save(output, format="PNG")
    output.seek(0)
    return output

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/generate", methods=["POST"])
def generate():
    raw = request.form.get("result", "").strip().replace(",", ".")
    try:
        value = float(raw)
    except ValueError:
        return "Ogiltigt värde. Skriv t.ex. 3.74 eller -1.20", 400
    return send_file(generate_image(value), mimetype="image/png", as_attachment=True, download_name="bcm_result.png")

if __name__ == "__main__":
    app.run(debug=True)
