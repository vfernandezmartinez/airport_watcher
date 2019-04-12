from collections import defaultdict
from enum import Enum
import mwparserfromhell
import re


class FlightSchedule(Enum):
    REGULAR = 'regular'
    SEASONAL = 'seasonal'
    CHARTER = 'charter'


UNDERSTOOD_TEMPLATE_NAMES = (
    'Airport-dest-list',
    'Airport destination list',
)


NO_TAG = ''


def get_airlines_destinations_from_wikitext(wikitext):
    wikicode = mwparserfromhell.parse(wikitext)
    for template in wikicode.filter_templates():
        for understood_template in UNDERSTOOD_TEMPLATE_NAMES:
            if template.name.startswith(understood_template):
                return _get_airlines_destinations_from_template(template)

    return ValueError('No valid templates found in the wikipedia section.')


def _get_airlines_destinations_from_template(template):
    if len(template.params) % 2 != 0:
        raise ValueError("The wikipedia template doesn't have an even number of fields.")

    iterator = iter(template.params)
    airlines_destinations = {}
    while True:
        try:
            airline = _get_airline_name(next(iterator).value)
            destinations = _get_airline_destinations(next(iterator).value)
            airlines_destinations[airline] = destinations
        except StopIteration:
            return airlines_destinations


def _get_airline_name(wikicode):
    tagged_plaintext = _convert_wikicode_to_tagged_plaintext(wikicode)
    return tagged_plaintext[NO_TAG].strip()


def _get_airline_destinations(wikicode):
    destinations = {}
    for schedule, plaintext_destinations in (
            _get_plaintext_destinations_by_schedule_dict(wikicode).items()):
        destinations.update(_get_destinations_from_plaintext(schedule, plaintext_destinations))
    return destinations


def _get_plaintext_destinations_by_schedule_dict(wikicode):
    tag_schedule_map = {
        NO_TAG: FlightSchedule.REGULAR.value,
        'Seasonal:': FlightSchedule.SEASONAL.value,
        'Charter:': FlightSchedule.CHARTER.value,
    }
    tagged_destinations = _convert_wikicode_to_tagged_plaintext(
        wikicode, allowed_tags=tag_schedule_map.keys())

    return {
        schedule: tagged_destinations[tag]
        for tag, schedule in tag_schedule_map.items()
        if tagged_destinations[tag]
    }


def _get_destinations_from_plaintext(schedule, plaintext):
    plaintext = plaintext.strip()
    if not plaintext:
        return list()

    if '(Services Suspended)' in plaintext:
        return list()

    destinations = {}
    date_extract = r'\((\w+) ([\w \-]+)\)'  # example match: "(begins 3 June 2019)"
    for plaintext_destination in plaintext.split(','):
        destination_name = plaintext_destination.strip()
        begin_date = None
        end_date = None

        match = re.search(date_extract, plaintext_destination)
        if match:
            destination_name = plaintext_destination[:match.start()].strip()
            keyword = match.group(1)
            if keyword in ('begins', 'resumes',):
                begin_date = match.group(2)
            elif keyword == 'ends':
                end_date = match.group(2)

        destinations[destination_name] = {
            'schedule': schedule,
            'begin_date': begin_date,
            'end_date': end_date,
        }

    return destinations


def _convert_wikicode_to_tagged_plaintext(wikicode, allowed_tags=None):
    if allowed_tags is None:
        allowed_tags = []

    tags_dict = defaultdict(str)
    current_tag = NO_TAG

    for node in wikicode.nodes:
        if type(node) == mwparserfromhell.nodes.tag.Tag:
            tag = str(node.contents)
            if tag in allowed_tags:
                current_tag = tag
        elif type(node) == mwparserfromhell.nodes.template.Template:
            for param in node.params:
                tags_dict[current_tag] += _convert_wikicode_to_tagged_plaintext(param.value)[NO_TAG]
        elif type(node) == mwparserfromhell.nodes.text.Text:
            tags_dict[current_tag] += node.value
        elif type(node) == mwparserfromhell.nodes.wikilink.Wikilink:
            if node.text:
                tags_dict[current_tag] += ' '.join([text_node.value for text_node in node.text.filter_text()])
            else:
                tags_dict[current_tag] += str(node.title)

    return tags_dict
