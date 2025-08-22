import os, json, html, logging, requests
from flask import Flask, request, abort, jsonify
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv('8269813489:AAHlPFDB1M6S9fU1XcFW7ZxZcoI9fN_fZgE')
TELEGRAM_CHAT_ID = os.getenv('-1002818839209')  # @channel или -100...
WEBHOOK_SECRET = os.getenv('my_secret_2025')      # опционально

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("Set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID")

app = Flask(__name__)

def send_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    r = requests.post(url, json=payload, timeout=10); r.raise_for_status(); return r.json()

@app.route('/', methods=['POST'])
def tradingview_webhook():
    data = request.get_json(silent=True)
    if not data: abort(400, "Request body must be JSON")
    if WEBHOOK_SECRET:
        provided = data.get('secret') or request.headers.get('X-Webhook-Secret')
        if provided != WEBHOOK_SECRET: abort(403, "Invalid webhook secret")
    pretty = html.escape(json.dumps(data, ensure_ascii=False, indent=2))
    msg = f"<b>TradingView alert</b>\n<pre>{pretty}</pre>"
    if len(msg) > 4000: msg = msg[:3990] + "\n\n[truncated]"
    try: send_to_telegram(msg)
    except requests.exceptions.RequestException: logging.exception("TG error"); abort(500, "Failed to send")
    return jsonify(ok=True), 200

if name == '__main__':
    host = os.getenv('HOST', '0.0.0.0'); port = int(os.getenv('PORT', '5000'))
    logging.info(f"Starting on {host}:{port}"); app.run(host=host, port=port)