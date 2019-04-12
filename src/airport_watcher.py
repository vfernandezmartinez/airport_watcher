import argparse
import requests
import sys

from airlines_destinations import AirlinesDestinations, AirlinesDestinationsSerializer
from wikipedia_scrapper import get_details_url


def airport_watch(airport_name, bot_token, chat_id):
    new = AirlinesDestinations(airport_name)
    new.fetch()

    serializer = AirlinesDestinationsSerializer(airport_name)
    try:
        old = serializer.read_last_known()
        added, changed, removed = new.compare(old)
        notification_text = render_notification(airport_name, added, changed, removed)
        if notification_text:
            send_to_telegram_bot(bot_token, chat_id, notification_text)
            print(notification_text)
    except FileNotFoundError:
        pass
    serializer.save(new)


def render_notification(airport_name, added, changed, removed):
    contents = render_diff(added, changed, removed)

    return (
        '{}\n\n{}\n\nCheck here for more details: {}'.format(
            airport_name, contents, get_details_url(airport_name)
        )
        if contents else None
    )


def render_destinations(title, destinations_dict):
    lines = []
    if destinations_dict:
        lines.append(title)
        for destination, attributes in destinations_dict.items():
            lines.append(f"  - {destination} ({attributes['schedule']})")
        lines.append('')
    return lines


def render_diff(added, changed, removed):
    all_airlines = added.keys() | changed.keys() | removed.keys()
    rendered_lines = []

    for airline in all_airlines:
        rendered_lines.extend(render_destinations(f'{airline} offers new destinations:', added.get(airline)))
        rendered_lines.extend(render_destinations(f'Destinations with {airline} changed:', changed.get(airline)))
        rendered_lines.extend(render_destinations(f'{airline} removed destinations:', removed.get(airline)))

    return '\n'.join(rendered_lines)


def send_to_telegram_bot(bot_token, chat_id, text):
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage',
                  data={'chat_id': chat_id, 'text': text})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check for new/removed destinations from your airport.')
    parser.add_argument('--bot_token', required=True, help='Telegram bot token')
    parser.add_argument('--chat_id', required=True, help='Telegram chat id')
    parser.add_argument('--airport', required=True, help='Airport name')
    args = parser.parse_args()
    airport_watch(args.airport, args.bot_token, args.chat_id)

