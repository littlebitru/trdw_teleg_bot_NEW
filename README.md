# TradingView ➜ Telegram Webhook Bot

This repository contains a simple Python application that relays TradingView alert webhooks to a Telegram channel. It uses the Flask web framework to expose an HTTP endpoint which accepts JSON payloads from TradingView and forwards them to Telegram using the Bot API.

## Features

* Listens for POST requests at the root path (`/`) and expects a JSON payload from TradingView.
* Formats the received JSON as a Markdown code block and sends it to a specified Telegram chat.
* Uses environment variables to store sensitive credentials (Telegram bot token and channel ID).
* Optionally validates requests with a shared `WEBHOOK_SECRET` value.
* Runs on port `5000` by default; you can override the host and port with `HOST` and `PORT` environment variables.

## Prerequisites

1. **Python 3.7+** installed on your system.
2. A **Telegram bot token**. Create a new bot by messaging [@BotFather](https://t.me/BotFather) on Telegram and follow the instructions. Copy the token provided.
3. A **Telegram channel** where alerts will be sent. You can use a public or private channel:
   - **Public channel:** If you have a public channel (e.g. `@mychannel`), the `chat_id` is simply `@mychannel`.
   - **Private channel:** For private channels, you need to obtain the numeric chat ID. Add your bot to the channel as an administrator, then use the @getmyid_bot or a similar bot to retrieve the channel ID.
4. A server or computer with a public IP or a tunnelling service like **ngrok** to receive webhooks from TradingView.

## Installation

Clone or copy this repository to your machine and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install flask requests
```

## Configuration

Set the following environment variables before running the bot:

- `TELEGRAM_TOKEN`: the API token for your Telegram bot.
- `TELEGRAM_CHAT_ID`: the channel username (prefixed with `@`) or numeric ID of your channel.
- Optional `WEBHOOK_SECRET`: shared token required from TradingView requests.
- Optional `HOST` and `PORT`: network interface and port for Flask to bind (defaults are `0.0.0.0` and `5000`).

Example on Unix-like systems:

```bash
export TELEGRAM_TOKEN="123456789:ABCDE_FGHIJKLMNOPQRSTUVWXYZ"
export TELEGRAM_CHAT_ID="@mychannel"
# Optional: require this secret from TradingView
export WEBHOOK_SECRET="my_secret"
python bot.py
```

On Windows PowerShell:

```powershell
$env:TELEGRAM_TOKEN = '123456789:ABCDE_FGHIJKLMNOPQRSTUVWXYZ'
$env:TELEGRAM_CHAT_ID = '@mychannel'
# Optional: require this secret from TradingView
$env:WEBHOOK_SECRET = 'my_secret'
python bot.py
```

## Running

Start the Flask app:

```bash
python bot.py
```

The application will start listening on `0.0.0.0:5000` (or whatever you set via `HOST` and `PORT`). You should see a line similar to:

```
Starting TradingView Telegram bot on 0.0.0.0:5000
 * Serving Flask app 'bot' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
```

To make your local server accessible to TradingView, you can use a tunnelling service like [ngrok](https://ngrok.com/):

```bash
ngrok http 5000
```

Ngrok will provide a public URL (e.g. `https://abcd1234.ngrok.io`) which you can use as the webhook URL in TradingView.

## Configuring TradingView Alerts

1. In TradingView, open the *Alerts* pane and create a new alert.
2. For the **webhook URL**, use your public URL from ngrok or your server, e.g. `https://abcd1234.ngrok.io/`.
3. In the **Message** field, enter any JSON you want forwarded. Example:

```json
{
  "symbol": "BTCUSDT",
  "price": 45000,
  "action": "buy",
  "time": "2025-08-09T12:34:56Z"
}
```

When the alert triggers, TradingView will send this JSON to your bot and it will appear in your Telegram channel.

## Notes

* The provided Flask app is for demonstration and quick setups. For a production deployment, consider using a WSGI server (e.g. Gunicorn) and HTTPS via a reverse proxy (e.g. Nginx).
* Adjust the message formatting in `bot.py` to suit your needs. You can extract specific fields from TradingView’s payload instead of forwarding the full JSON.
* Do **not** share your bot token publicly; treat it like a password. If compromised, revoke it via @BotFather and obtain a new one.

## License

This project is released under the MIT License. See the [LICENSE](LICENSE) file for details.