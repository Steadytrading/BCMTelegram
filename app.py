
from flask import Flask, render_template_string, request, send_file
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os
import io

app = Flask(__name__)

WIDTH = 1080
HEIGHT = 1350

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

PROFIT_BADGES = [
    "LOW RISK STRATEGY",
    "CONSISTENT GAINS",
    "DISCIPLINED EXECUTION",
]

LOSS_BADGES = [
    "CAPITAL PROTECTION",
    "RISK MANAGED DAY",
    "DEFENSIVE SESSION",
]

HTML = """
<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <title>BCM Trading Telegram Generator V2</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: linear-gradient(135deg, #08101e, #131a2e);
      color: #fff;
      padding: 40px;
    }
    .box {
      max-width: 560px;
      margin: auto;
      background: rgba(19,26,46,.95);
      padding: 32px;
      border-radius: 20px;
      box-shadow: 0 18px 50px rgba(0,0,0,.35);
      border: 1px solid rgba(255,255,255,.06);
    }
    h1 {
      margin-top: 0;
      font-size: 32px;
    }
    p {
      color: #c5cee4;
      line-height: 1.5;
    }
    input, button {
      width: 100%;
      padding: 14px;
      border-radius: 12px;
      border: none;
      font-size: 16px;
      box-sizing: border-box;
    }
    input {
      margin: 14px 0;
      background: #eef2ff;
    }
    button {
      background: #2d6cdf;
      color: white;
      cursor: pointer;
      font-weight: 700;
    }
    .hint {
      color: #b7bfd6;
      font-size: 14px;
      margin-top: 14px;
    }
  </style>
</head>
<body>
  <div class="box">
    <h1>BCM Trading Generator V2</h1>
    <p>Premium Telegram-resultatbild med glow-effekt, candlestick-bakgrund, slumpad vinst/förlusttext och integrerad BCM-logga.</p>
    <form method="post" action="/generate">
      <label>Dagens resultat i %</label>
      <input name="result" placeholder="t.ex. 3.74 eller -1.20" required>
      <button type="submit">Generera Telegram-bild</button>
    </form>
    <p class="hint">Output: 1080x1350 PNG</p>
  </div>
</body>
</html>
"""

def load_font(size, bold=False):
    candidates = []
    if bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def draw_centered(draw, text, y, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (WIDTH - w) / 2
    draw.text((x, y), text, font=font, fill=fill)

def add_glow_text(base, text, y, font, text_fill, glow_fill, blur_radius=18):
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    bbox = gdraw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = int((WIDTH - w) / 2)
    gdraw.text((x, y), text, font=font, fill=glow_fill)
    glow = glow.filter(ImageFilter.GaussianBlur(blur_radius))
    base.alpha_composite(glow)
    draw = ImageDraw.Draw(base)
    draw.text((x, y), text, font=font, fill=text_fill)

def draw_candles(draw):
    baseline = 980
    start_x = 80
    candle_w = 18
    gap = 14
    for i in range(26):
        x = start_x + i * (candle_w + gap)
        body_h = random.randint(40, 180)
        wick_top = random.randint(20, 70)
        wick_bottom = random.randint(20, 70)
        green = random.choice([True, False, True])
        color = (37, 211, 102, 130) if green else (255, 82, 82, 130)
        top = baseline - body_h - random.randint(-120, 120)
        bottom = top + body_h
        center_x = x + candle_w // 2
        draw.line((center_x, top - wick_top, center_x, bottom + wick_bottom), fill=color, width=3)
        draw.rounded_rectangle((x, top, x + candle_w, bottom), radius=4, fill=color)

def add_gradient_background():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 12, 24, 255))
    px = img.load()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r = 8
            g = 12 + int(20 * y / HEIGHT)
            b = 24 + int(40 * y / HEIGHT)
            px[x, y] = (r, g, b, 255)
    return img

def add_vignette(base):
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for i in range(120):
        alpha = int(2.2 * i)
        odraw.rounded_rectangle((i, i, WIDTH - i, HEIGHT - i), radius=40, outline=(0, 0, 0, alpha))
    base.alpha_composite(overlay)

def try_add_logo(base):
    logo_paths = [
        os.path.join("assets", "logo.png"),
        "logo.png",
    ]
    for path in logo_paths:
        if os.path.exists(path):
            logo = Image.open(path).convert("RGBA")
            logo.thumbnail((520, 300))
            x = (WIDTH - logo.width) // 2
            base.alpha_composite(logo, (x, 70))
            return True
    return False

def generate_image(result_value):
    is_profit = result_value >= 0
    result_text = f"{result_value:+.2f}%"
    body_text = random.choice(PROFIT_TEXTS if is_profit else LOSS_TEXTS)
    badge_text = random.choice(PROFIT_BADGES if is_profit else LOSS_BADGES)

    base = add_gradient_background()
    draw = ImageDraw.Draw(base)

    for x in range(0, WIDTH, 60):
        draw.line((x, 0, x, HEIGHT), fill=(40, 70, 110, 40), width=1)
    for y in range(0, HEIGHT, 60):
        draw.line((0, y, WIDTH, y), fill=(40, 70, 110, 40), width=1)

    light = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(light)
    ldraw.ellipse((160, 260, 920, 1020), fill=(40, 120, 255, 28))
    light = light.filter(ImageFilter.GaussianBlur(60))
    base.alpha_composite(light)

    draw_candles(draw)
    add_vignette(base)

    added_logo = try_add_logo(base)
    draw = ImageDraw.Draw(base)

    title_font = load_font(42, bold=True)
    result_font = load_font(140, bold=True)
    body_font = load_font(42, bold=False)
    badge_font = load_font(34, bold=True)
    brand_font = load_font(36, bold=True)

    if not added_logo:
        draw_centered(draw, "BCM TRADING", 110, load_font(64, bold=True), (235, 240, 255, 255))

    draw_centered(draw, "TODAY'S RESULT", 410, title_font, (210, 220, 245, 230))

    if is_profit:
        add_glow_text(base, result_text, 510, result_font, (255, 255, 255, 255), (40, 210, 110, 150))
    else:
        add_glow_text(base, result_text, 510, result_font, (255, 255, 255, 255), (255, 70, 70, 150))

    body_lines = [
        body_text,
        "BCM Trading focuses on disciplined entries",
        "and strict risk management.",
    ]
    y = 730
    for line in body_lines:
        draw_centered(draw, line, y, body_font, (228, 234, 246, 220))
        y += 54

    badge_y = 940
    badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    badge_w = badge_bbox[2] - badge_bbox[0]
    pad_x = 34
    pad_y = 20
    bx1 = (WIDTH - badge_w) // 2 - pad_x
    bx2 = (WIDTH + badge_w) // 2 + pad_x
    by1 = badge_y - pad_y
    by2 = badge_y + (badge_bbox[3] - badge_bbox[1]) + pad_y
    badge_color = (32, 190, 100, 210) if is_profit else (210, 70, 70, 210)
    draw.rounded_rectangle((bx1, by1, bx2, by2), radius=24, fill=badge_color)
    draw_centered(draw, badge_text, badge_y, badge_font, (255, 255, 255, 255))

    draw_centered(draw, "Copy trading available on Vantage", 1110, load_font(28), (188, 198, 222, 200))
    draw_centered(draw, "BCM Trading", 1160, brand_font, (255, 255, 255, 235))

    output = io.BytesIO()
    base.convert("RGB").save(output, format="PNG")
    output.seek(0)
    return output

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)

@app.route("/generate", methods=["POST"])
def generate():
    raw = request.form.get("result", "").strip().replace(",", ".")
    try:
        result_value = float(raw)
    except ValueError:
        return "Ogiltigt värde. Skriv t.ex. 3.74 eller -1.20", 400

    image_bytes = generate_image(result_value)
    filename = f"bcm_result_{result_value:+.2f}.png".replace("+", "plus_").replace("-", "minus_")
    return send_file(image_bytes, mimetype="image/png", as_attachment=True, download_name=filename)

if __name__ == "__main__":
    app.run(debug=True)
