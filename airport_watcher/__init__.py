from .airport_destinations import AirportDestinations, AirportDestinationsDiff
from .notifications import send_to_telegram_bot


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
