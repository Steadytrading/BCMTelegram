
from flask import Flask, render_template_string, request, send_file
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import os
import io
import textwrap

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
    "PRECISION ENTRIES",
]

LOSS_BADGES = [
    "CAPITAL PROTECTION",
    "RISK MANAGED DAY",
    "DEFENSIVE SESSION",
    "CONTROLLED DRAWDOWN",
]

CAPTIONS_PROFIT = [
    "Today's result: {result}\n\nAnother strong day from BCM Trading.\nDisciplined execution and strict risk management remain the foundation.\n\nCopy trading available on Vantage.",
    "Today's result: {result}\n\nSolid session with controlled risk and high-probability execution.\nBCM Trading stays focused on consistency over hype.\n\nCopy trading available on Vantage.",
    "Today's result: {result}\n\nA clean trading day built on patience, precision and capital protection.\n\nBCM Trading",
]

CAPTIONS_LOSS = [
    "Today's result: {result}\n\nNot every session ends green.\nRisk stayed controlled and capital protection came first.\n\nBCM Trading",
    "Today's result: {result}\n\nA defensive day, but discipline remains intact.\nLong-term consistency is built through strict risk management.\n\nCopy trading available on Vantage.",
    "Today's result: {result}\n\nSmall setback. Strategy and risk plan were respected throughout the session.\n\nBCM Trading",
]

HTML = """
<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <title>BCM Trading Generator V3</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: radial-gradient(circle at top, #13203d, #08101e 55%);
      color: #fff;
      padding: 40px;
      margin: 0;
    }
    .box {
      max-width: 620px;
      margin: auto;
      background: rgba(12,18,34,.96);
      padding: 34px;
      border-radius: 24px;
      box-shadow: 0 20px 60px rgba(0,0,0,.4);
      border: 1px solid rgba(255,255,255,.07);
    }
    h1 { margin: 0 0 10px 0; font-size: 34px; }
    p { color: #c5cee4; line-height: 1.55; }
    label { display:block; margin-top: 18px; margin-bottom: 8px; font-weight: 700; }
    input, button {
      width: 100%;
      padding: 15px 16px;
      border-radius: 14px;
      border: none;
      font-size: 16px;
      box-sizing: border-box;
    }
    input { background: #eef2ff; }
    button {
      background: linear-gradient(135deg, #2d6cdf, #1d9bf0);
      color: white;
      cursor: pointer;
      font-weight: 700;
      margin-top: 18px;
    }
    .hint {
      color: #9fb0d7;
      font-size: 14px;
      margin-top: 14px;
    }
    .tag {
      display:inline-block;
      padding: 7px 12px;
      border-radius: 999px;
      background: rgba(255,255,255,.08);
      font-size: 13px;
      margin-right: 8px;
      margin-bottom: 8px;
    }
  </style>
</head>
<body>
  <div class="box">
    <h1>BCM Trading Generator V3</h1>
    <p>Premium Telegram-resultatbild med starkare layout, större resultatsiffra, förbättrad badge och färdig caption i svaret.</p>
    <div>
      <span class="tag">1080x1350 PNG</span>
      <span class="tag">Premium layout</span>
      <span class="tag">Telegram-ready</span>
    </div>
    <form method="post" action="/generate">
      <label>Dagens resultat i %</label>
      <input name="result" placeholder="t.ex. 3.74 eller -1.20" required>
      <button type="submit">Generera Telegram-bild</button>
    </form>
    <p class="hint">Generatorn slumpas mellan olika texter för både vinst och förlust.</p>
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

def add_glow_text(base, text, y, font, text_fill, glow_fill, blur_radius=22):
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    bbox = gdraw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = int((WIDTH - w) / 2)
    for _ in range(2):
        gdraw.text((x, y), text, font=font, fill=glow_fill)
    glow = glow.filter(ImageFilter.GaussianBlur(blur_radius))
    base.alpha_composite(glow)
    draw = ImageDraw.Draw(base)
    draw.text((x, y), text, font=font, fill=text_fill)

def draw_candles(draw):
    baseline = 960
    start_x = 85
    candle_w = 18
    gap = 14
    for i in range(26):
        x = start_x + i * (candle_w + gap)
        body_h = random.randint(50, 190)
        wick_top = random.randint(18, 65)
        wick_bottom = random.randint(18, 65)
        green = random.choice([True, False, True])
        color = (37, 211, 102, 125) if green else (255, 82, 82, 125)
        top = baseline - body_h - random.randint(-100, 100)
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
            g = 12 + int(26 * y / HEIGHT)
            b = 24 + int(52 * y / HEIGHT)
            px[x, y] = (r, g, b, 255)
    return img

def add_vignette(base):
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for i in range(130):
        alpha = int(2.15 * i)
        odraw.rounded_rectangle((i, i, WIDTH - i, HEIGHT - i), radius=48, outline=(0, 0, 0, alpha))
    base.alpha_composite(overlay)

def try_add_logo(base):
    logo_paths = [
        os.path.join("assets", "logo.png"),
        "logo.png",
    ]
    for path in logo_paths:
        if os.path.exists(path):
            logo = Image.open(path).convert("RGBA")
            logo.thumbnail((500, 250))
            x = (WIDTH - logo.width) // 2
            base.alpha_composite(logo, (x, 66))
            return True
    return False

def wrap_line(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else current + " " + word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def build_caption(is_profit, result_text):
    pool = CAPTIONS_PROFIT if is_profit else CAPTIONS_LOSS
    return random.choice(pool).format(result=result_text)

def generate_image(result_value):
    is_profit = result_value >= 0
    result_text = f"{result_value:+.2f}%"
    body_text = random.choice(PROFIT_TEXTS if is_profit else LOSS_TEXTS)
    badge_text = random.choice(PROFIT_BADGES if is_profit else LOSS_BADGES)

    base = add_gradient_background()
    draw = ImageDraw.Draw(base)

    for x in range(0, WIDTH, 54):
        draw.line((x, 0, x, HEIGHT), fill=(40, 70, 110, 36), width=1)
    for y in range(0, HEIGHT, 54):
        draw.line((0, y, WIDTH, y), fill=(40, 70, 110, 36), width=1)

    light = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ldraw = ImageDraw.Draw(light)
    ldraw.ellipse((140, 220, 940, 1040), fill=(40, 120, 255, 34))
    ldraw.ellipse((250, 420, 830, 900), fill=((45, 180, 255, 26) if is_profit else (255, 80, 80, 24)))
    light = light.filter(ImageFilter.GaussianBlur(75))
    base.alpha_composite(light)

    draw_candles(draw)
    add_vignette(base)

    # subtle panel
    panel = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel)
    pdraw.rounded_rectangle((85, 360, WIDTH - 85, 1210), radius=34, fill=(12, 20, 36, 92), outline=(255, 255, 255, 18), width=2)
    panel = panel.filter(ImageFilter.GaussianBlur(1))
    base.alpha_composite(panel)

    added_logo = try_add_logo(base)
    draw = ImageDraw.Draw(base)

    title_font = load_font(38, bold=True)
    result_font = load_font(168, bold=True)
    body_font = load_font(40, bold=False)
    badge_font = load_font(32, bold=True)
    brand_font = load_font(34, bold=True)
    small_font = load_font(27, bold=False)

    if not added_logo:
        draw_centered(draw, "BCM TRADING", 96, load_font(62, bold=True), (235, 240, 255, 255))

    draw_centered(draw, "TODAY'S RESULT", 410, title_font, (212, 223, 247, 235))

    if is_profit:
        add_glow_text(base, result_text, 485, result_font, (255, 255, 255, 255), (40, 210, 110, 165))
    else:
        add_glow_text(base, result_text, 485, result_font, (255, 255, 255, 255), (255, 70, 70, 165))

    accent = (42, 210, 115, 230) if is_profit else (235, 82, 82, 230)
    draw.rounded_rectangle((300, 690, 780, 696), radius=8, fill=accent)

    max_width = WIDTH - 260
    wrapped = wrap_line(draw, body_text, body_font, max_width)
    y = 748
    for line in wrapped[:2]:
        draw_centered(draw, line, y, body_font, (230, 236, 248, 225))
        y += 50

    fixed_lines = [
        "BCM Trading focuses on disciplined entries",
        "strict risk management and steady execution.",
    ]
    y += 18
    for line in fixed_lines:
        draw_centered(draw, line, y, small_font, (184, 198, 225, 220))
        y += 40

    badge_bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    badge_w = badge_bbox[2] - badge_bbox[0]
    pad_x = 30
    pad_y = 18
    bx1 = (WIDTH - badge_w) // 2 - pad_x
    bx2 = (WIDTH + badge_w) // 2 + pad_x
    by1 = 972
    by2 = by1 + (badge_bbox[3] - badge_bbox[1]) + pad_y * 2
    badge_color = (26, 170, 92, 220) if is_profit else (186, 58, 58, 220)
    draw.rounded_rectangle((bx1, by1, bx2, by2), radius=24, fill=badge_color)
    draw_centered(draw, badge_text, by1 + pad_y - 2, badge_font, (255, 255, 255, 255))

    draw_centered(draw, "Copy trading available on Vantage", 1115, small_font, (192, 203, 228, 210))
    draw_centered(draw, "BCM Trading", 1162, brand_font, (255, 255, 255, 238))

    output = io.BytesIO()
    base.convert("RGB").save(output, format="PNG")
    output.seek(0)

    caption = build_caption(is_profit, result_text)
    return output, caption, badge_text

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

    image_bytes, caption, badge = generate_image(result_value)
    filename = f"bcm_result_{result_value:+.2f}.png".replace("+", "plus_").replace("-", "minus_")
    response = send_file(image_bytes, mimetype="image/png", as_attachment=True, download_name=filename)
    response.headers["X-Generated-Caption"] = caption
    response.headers["X-Generated-Badge"] = badge
    return response

if __name__ == "__main__":
    app.run(debug=True)
