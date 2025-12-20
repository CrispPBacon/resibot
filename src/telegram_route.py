from flask import Blueprint, request
from .config import TELEGRAM_BOT_TOKEN
from .receipt_reader import process_receipt_image
from .utils import root_dir

import requests
import os

telegram_bp = Blueprint("telegram_bp", __name__)

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}"


@telegram_bp.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update and "photo" in update["message"]:
        # Telegram sends photos with multiple sizes → take the largest one
        file_id = update["message"]["photo"][-1]["file_id"]
        chat_id = update["message"]["chat"]["id"]
        send_message(chat_id, "Processing image...")

        # Full path to save the file
        download_path = os.path.join(root_dir, "downloads", str(chat_id))
        os.makedirs(download_path, exist_ok=True)

        # SAVE FILE
        save_path = os.path.join(
            root_dir, "downloads", str(chat_id), f"{file_id}.jpg")
        saved_file = download_telegram_file(file_id, save_path)

        image_path = os.path.abspath(os.path.join(
            root_dir, saved_file))

        extracted_text = process_receipt_image(image_path)
        converted_text = ""
        for key, val in extracted_text.items():
            if (key == "name"):
                val = val.replace("•", "*")
            converted_text += f"{key}: {val}\n"

        send_message(chat_id, converted_text)
        return {"status": "image_saved", "file": saved_file}

    elif "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        message = update["message"]["text"]
        send_message(chat_id, f"You said: {message}")
    return "OK", 200


def send_message(chat_id: int, text: str):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    return response.json()


def download_telegram_file(file_id: str, save_path: str):
    if os.path.exists(save_path):
        print("File already exist..")
        return save_path

    # 1. Get file info (file_path)
    url = f"{BASE_URL}/getFile?file_id={file_id}"
    res = requests.get(url).json()

    if not res["ok"]:
        raise Exception("Failed to get file info")

    file_path = res["result"]["file_path"]
    # 2. Download the file using file_path
    download_url = f"{FILE_URL}/{file_path}"
    file_bytes = requests.get(download_url).content

    # 3. Save file
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    return save_path
