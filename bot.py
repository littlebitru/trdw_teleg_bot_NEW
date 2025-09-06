"""Simple Flask application that forwards TradingView webhooks to Telegram.

The app exposes a single POST endpoint at ``/``. Incoming JSON payloads are
optionally validated using a shared secret and then forwarded to a Telegram
channel or chat using the Bot API. Credentials and configuration are supplied
via environment variables to avoid hard‑coding sensitive values in the source
code.

Required environment variables
------------------------------
``TELEGRAM_TOKEN``
    API token of the Telegram bot.

``TELEGRAM_CHAT_ID``
    Username (prefixed with ``@``) or numeric ID of the target channel/chat.

Optional environment variables
------------------------------
``WEBHOOK_SECRET``
    If set, requests must include this secret either in the JSON body under
    the ``"secret"`` field or in the ``X-Webhook-Secret`` HTTP header.

``HOST`` / ``PORT``
    Network interface and port for the Flask app. Defaults are ``0.0.0.0`` and
    ``5000`` respectively.
"""

from __future__ import annotations

import html
import json
import logging
import os
from typing import Any, Dict

import requests
from flask import Flask, abort, jsonify, request

logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TELEGRAM_TOKEN: str | None = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID: str | None = os.getenv("TELEGRAM_CHAT_ID")
WEBHOOK_SECRET: str | None = os.getenv("WEBHOOK_SECRET")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise RuntimeError("Set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID environment variables")


app = Flask(__name__)


def send_to_telegram(text: str) -> Dict[str, Any]:
    """Send ``text`` to the configured Telegram chat."""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


@app.route("/", methods=["POST"])
def tradingview_webhook():
    """Endpoint receiving webhook alerts from TradingView."""

    data = request.get_json(silent=True)
    if not data:
        abort(400, "Request body must be JSON")

    if WEBHOOK_SECRET:
        provided = data.get("secret") or request.headers.get("X-Webhook-Secret")
        if provided != WEBHOOK_SECRET:
            abort(403, "Invalid webhook secret")

    pretty = html.escape(json.dumps(data, ensure_ascii=False, indent=2))
    message = f"<b>TradingView alert</b>\n<pre>{pretty}</pre>"
    if len(message) > 4000:
        message = message[:3990] + "\n\n[truncated]"

    try:
        send_to_telegram(message)
    except requests.RequestException:
        logging.exception("Failed to send message to Telegram")
        abort(500, "Failed to send")

    return jsonify(ok=True), 200


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    logging.info("Starting on %s:%s", host, port)
    app.run(host=host, port=port)

