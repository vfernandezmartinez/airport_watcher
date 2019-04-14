import mwparserfromhell

from .exceptions import ScrapError


UNDERSTOOD_TEMPLATE_NAMES = (
    'Airport-dest-list',
    'Airport destination list',
)


def get_airlines_destinations_from_wikitext(wikitext):
    wikicode = mwparserfromhell.parse(wikitext)
    for template in wikicode.filter_templates():
        for understood_template in UNDERSTOOD_TEMPLATE_NAMES:
            if template.name.startswith(understood_template):
                return _get_airlines_destinations_from_template(template)

    return ScrapError('No valid templates found in the wikipedia section.')


def _get_airlines_destinations_from_template(template):
    if len(template.params) % 2 != 0:
        raise ScrapError("The wikipedia template doesn't have an even number of fields.")

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
    return _convert_wikicode_to_plaintext(wikicode)


def _get_airline_destinations(wikicode):
    plaintext = _convert_wikicode_to_plaintext(wikicode)
    destinations = []
    if plaintext and '(Services Suspended)' not in plaintext:
        for destination_name in plaintext.split(','):
            destination_name = destination_name.split('(')[0]
            destination_name = destination_name.strip()
            if destination_name:
                destinations.append(destination_name)

    return destinations


def _convert_wikicode_to_plaintext(wikicode):
    plaintext = ''

    for node in wikicode.nodes:
        if type(node) == mwparserfromhell.nodes.tag.Tag:
            plaintext += ','
        elif type(node) == mwparserfromhell.nodes.template.Template:
            for param in node.params:
                plaintext += _convert_wikicode_to_plaintext(param.value)
        elif type(node) == mwparserfromhell.nodes.text.Text:
            plaintext += node.value
        elif type(node) == mwparserfromhell.nodes.wikilink.Wikilink:
            if node.text:
                plaintext += ' '.join([text_node.value for text_node in node.text.filter_text()])
            else:
                plaintext += str(node.title)

    return plaintext.strip()
