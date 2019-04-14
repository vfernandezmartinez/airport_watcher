import argparse
import requests

from airport_destinations import AirportDestinations, AirportDestinationsDiff


def airport_watch(airport_name, bot_token, chat_id):
    current_destinations = AirportDestinations.fetch(airport_name)

    try:
        previous_destinations = AirportDestinations.last_known(airport_name)
        diff = AirportDestinationsDiff(previous_destinations, current_destinations)
        notification_text = diff.render_plaintext()
        if notification_text:
            send_to_telegram_bot(bot_token, chat_id, notification_text)
            print(notification_text)
        else:
            print(f'No new destinations found in {airport_name}.')
    except AirportDestinations.DestinationsUnknown:
        print(f'{airport_name} destinations initially fetched.')

    current_destinations.save()


def send_to_telegram_bot(bot_token, chat_id, text):
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage',
                  data={'chat_id': chat_id, 'text': text}, timeout=30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check for new/removed destinations from your airport.')
    parser.add_argument('--bot_token', required=True, help='Telegram bot token')
    parser.add_argument('--chat_id', required=True, help='Telegram chat id')
    parser.add_argument('--airport', required=True, help='Airport name')
    args = parser.parse_args()

    airport_watch(args.airport, args.bot_token, args.chat_id)

