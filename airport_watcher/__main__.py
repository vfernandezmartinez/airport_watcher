import argparse
import sys

from airport_watcher.wikipedia_scrapper import ScrapError
from . import check_destination_changes
from .airport_destinations import AirportDestinations
from .notifications import NotificationError


parser = argparse.ArgumentParser(description='Check for new/removed destinations from your airport.')
parser.add_argument('--bot_token', required=True, help='Telegram bot token')
parser.add_argument('--chat_id', required=True, help='Telegram chat id')
parser.add_argument('--airport', required=True, help='Airport name')
parser.add_argument('--store', help='Path for storing last known airport destinations.')
cmd_args = parser.parse_args()

if cmd_args.store:
    AirportDestinations.storage_dir = cmd_args.store

try:
    changes = check_destination_changes(cmd_args.airport, cmd_args.bot_token, cmd_args.chat_id)
    if changes:
        print(changes)
    else:
        print(f'No changes found in destinations from {cmd_args.airport}.')
except AirportDestinations.DestinationsUnknown:
    print(f'List of destinations from {cmd_args.airport} fetched.')
except (IOError, NotificationError, ScrapError,) as e:
    print(e)
    sys.exit(1)
