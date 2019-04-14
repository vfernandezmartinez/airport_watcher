import argparse
import sys

from airport_destinations import AirportDestinations, AirportDestinationsDiff, ScrapError
from notifications import send_to_telegram_bot, NotificationError


def check_destination_changes(airport_name, bot_token, chat_id):
    current_destinations = AirportDestinations.fetch(airport_name)
    try:
        previous_destinations = AirportDestinations.last_known(airport_name)
    finally:
        current_destinations.save()

    diff = AirportDestinationsDiff(previous_destinations, current_destinations)
    notification_text = diff.render_plaintext()
    if notification_text:
        send_to_telegram_bot(notification_text, bot_token, chat_id)
        return notification_text


def airport_watcher(cmd_args):
    airport_name = cmd_args.airport

    try:
        changes = check_destination_changes(airport_name, cmd_args.bot_token, cmd_args.chat_id)
        if changes:
            print(changes)
        else:
            print(f'No changes found in destinations from {airport_name}.')
    except AirportDestinations.DestinationsUnknown:
        print(f'List of destinations from {airport_name} fetched.')
    except (IOError, NotificationError, ScrapError,) as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check for new/removed destinations from your airport.')
    parser.add_argument('--bot_token', required=True, help='Telegram bot token')
    parser.add_argument('--chat_id', required=True, help='Telegram chat id')
    parser.add_argument('--airport', required=True, help='Airport name')
    cmd_args = parser.parse_args()
    airport_watcher(cmd_args)
