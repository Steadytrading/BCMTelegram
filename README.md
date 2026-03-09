# BCM Trading Telegram Generator V3 Fix

Fixar 500-felet i /generate.

Orsak:
Förra versionen skickade multiline-caption i HTTP headers, vilket Flask/Werkzeug inte tillåter.

Fix:
- inga multiline headers
- generatorn returnerar bara PNG-filen
