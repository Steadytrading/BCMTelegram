
# BCM Trading Telegram Generator V3

V3 är en mer premium version av generatorn, byggd för Telegram.

## Nytt i V3
- större resultatsiffra
- renare layout med central panel
- förbättrad badge-design
- färdig Telegram-caption genereras i response headers
- BCM-logga via `assets/logo.png`
- premium bakgrund med candlesticks och glow

## Deploy på Render
Build:
`pip install -r requirements.txt`

Start:
`gunicorn --bind 0.0.0.0:$PORT app:app`

## Filer
- `app.py`
- `requirements.txt`
- `render.yaml`
- `assets/logo.png`

## Input
- `3.74`
- `-1.20`
