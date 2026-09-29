import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{bot_token}/sendMessage"


def send_telegram_message(text: str) -> bool:
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not bot_token or not chat_id:
        logger.warning(
            "Telegram credentials are not configured; skipping notification."
        )
        return False

    url = TELEGRAM_API_URL.format(token=bot_token)
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, data=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException:
        logger.exception("Failed to send Telegram notification.")
        return False
