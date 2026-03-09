
# BCM Trading Telegram Generator V2

Premium Telegram result image generator for BCM Trading.

## Features
- 1080x1350 PNG output
- 5 random profit texts
- 5 random loss texts
- profit/loss badge
- dark premium trading design
- candlestick background
- glow effect on result
- integrated logo support via `assets/logo.png`

## Deploy on Render

Build command:
`pip install -r requirements.txt`

Start command:
`gunicorn --bind 0.0.0.0:$PORT app:app`

## Input examples
- `3.74`
- `-1.20`

## Files
- `app.py`
- `requirements.txt`
- `render.yaml`
- `assets/logo.png`
