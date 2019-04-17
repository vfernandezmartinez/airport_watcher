import requests


class NotificationError(Exception):
    pass


def send_to_telegram_bot(text, bot_token, chat_id):
    try:
        requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage',
                      data={'chat_id': chat_id, 'text': text}, timeout=30)
    except requests.RequestException as e:
        raise NotificationError(f'Error while sending notification to Telegram bot: {str(e)}')
