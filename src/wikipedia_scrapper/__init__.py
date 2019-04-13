from .downloader import fetch_destinations_section_wikitext
from .wikitext_parser import get_airlines_destinations_from_wikitext


def fetch_airlines_destinations(airport_name):
    wikitext = fetch_destinations_section_wikitext(airport_name)
    return get_airlines_destinations_from_wikitext(wikitext)


def get_details_url(airport_name):
    encoded_airport = airport_name.replace(' ', '_')
    return f'https://en.wikipedia.org/wiki/{encoded_airport}#Airlines_and_destinations'
