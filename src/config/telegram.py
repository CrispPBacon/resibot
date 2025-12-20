import requests
from flask import request
from . import TELEGRAM_BOT_TOKEN, ENV


def on_telegram_init():
    try:
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebHook"

        if ENV:
            ngrok_url = get_ngrok_url()
            print("URL:", ngrok_url)
            if ngrok_url:
                webhook_url = f"{ngrok_url}/api/telegram/webhook"
                response = requests.post(
                    telegram_url, json={"url": webhook_url})
                print(response.json(), "HERE")
            else:
                print("Ngrok URL is not available.")
        else:
            webhook_url = f"{request.host_url}/webhook"
    except requests.exceptions.RequestException as error:
        print(f"Error setting webhook: {error}")


def get_ngrok_url():
    try:
        res = requests.get(f"http://127.0.0.1:4040/api/tunnels")
        res.raise_for_status()  # Will raise an exception for 4xx/5xx status codes
        tunnels = res.json().get('tunnels', [])
        https_tunnel = next(
            (t for t in tunnels if t['proto'] == 'https'), None)

        if not https_tunnel:
            print("No HTTPS tunnel found.")
            return None

        ngrok_url = https_tunnel.get('public_url')
        print(f"Ngrok tunnel set at: {ngrok_url}")
        return ngrok_url
    except requests.exceptions.RequestException as err:
        print(f"Error fetching ngrok URL: {err}")
        return None
