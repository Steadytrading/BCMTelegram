
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
<html>
<head>
<meta charset="utf-8">
<title>BCM Trading Generator</title>
<style>
body { font-family: Arial; background:#0b1020; color:white; padding:40px; }
.box { max-width:500px; margin:auto; background:#131a2e; padding:30px; border-radius:15px; }
input,button { width:100%; padding:14px; margin-top:10px; border-radius:10px; border:none; }
button { background:#2d6cdf; color:white; font-weight:bold; cursor:pointer; }
</style>
</head>
<body>
<div class="box">
<h2>BCM Trading Telegram Generator</h2>
<form method="post" action="/generate">
<input name="result" placeholder="Example: 3.74 or -1.20" required>
<button type="submit">Generate Image</button>
</form>
</div>
</body>
</html>
"""

def load_font(size):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except:
        return ImageFont.load_default()

def draw_center(draw, text, y, font):
    w = draw.textlength(text, font=font)
    x = (WIDTH - w) / 2
    draw.text((x, y), text, fill=(255,255,255), font=font)

def background():
    img = Image.new("RGB", (WIDTH, HEIGHT), (10,15,30))
    draw = ImageDraw.Draw(img)

    for x in range(0, WIDTH, 60):
        draw.line((x,0,x,HEIGHT), fill=(30,60,90))

    for y in range(0, HEIGHT, 60):
        draw.line((0,y,WIDTH,y), fill=(30,60,90))

    return img

def generate_image(result):
    profit = result >= 0
    percent = f"{result:+.2f}%"

    text = random.choice(PROFIT_TEXTS if profit else LOSS_TEXTS)
    badge = random.choice(PROFIT_BADGES if profit else LOSS_BADGES)

    img = background()
    draw = ImageDraw.Draw(img)

    title_font = load_font(60)
    result_font = load_font(150)
    body_font = load_font(40)
    badge_font = load_font(35)

    draw_center(draw, "BCM TRADING", 120, title_font)
    draw_center(draw, "TODAY'S RESULT", 360, body_font)

    color = (40,220,120) if profit else (255,80,80)
    w = draw.textlength(percent, font=result_font)
    x = (WIDTH - w) / 2
    draw.text((x,500), percent, fill=color, font=result_font)

    draw_center(draw, text, 720, body_font)
    draw_center(draw, "BCM Trading focuses on disciplined entries", 780, body_font)
    draw_center(draw, "and strict risk management.", 840, body_font)

    draw_center(draw, badge, 980, badge_font)
    draw_center(draw, "Copy trading available on Vantage", 1120, body_font)

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)

    return output

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/generate", methods=["POST"])
def generate():
    raw = request.form.get("result","").replace(",",".")
    try:
        value = float(raw)
    except:
        return "Invalid number", 400

    image = generate_image(value)
    return send_file(image, mimetype="image/png", as_attachment=True, download_name="bcm_result.png")

if __name__ == "__main__":
    app.run()
