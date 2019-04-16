import requests

from .exceptions import ScrapError


WIKIPEDIA_API_URL = 'https://en.wikipedia.org/w/api.php'


def fetch_destinations_section_wikitext(airport_name):
    section = _choose_airport_page_section(airport_name)
    return _fetch_section_wikitext(page=airport_name, section=section)


def _choose_airport_page_section(airport_name):
    chosen_section = None
    for section in _fetch_page_sections(page=airport_name):
        if (section['line'] == 'Airlines and destinations'
                and not chosen_section) or section['line'] == 'Passenger':
            chosen_section = section['index']

    if chosen_section:
        return chosen_section
    else:
        raise ScrapError(f'"Airlines and destinations" section not found in the wikipedia page for {airport_name}.')


def _fetch_page_sections(page):
    query_params = {
        'action': 'parse',
        'page': page,
        'redirects': True,
        'prop': 'sections',
    }
    r = _query_wikipedia(query_params)
    return r['parse']['sections']


def _fetch_section_wikitext(page, section):
    query_params = {
        'action': 'parse',
        'page': page,
        'redirects': True,
        'section': section,
        'prop': 'wikitext',
    }
    r = _query_wikipedia(query_params)
    return r['parse']['wikitext']['*']


def _query_wikipedia(query_params):
    params = {
        **query_params,
        'format': 'json',
    }
    try:
        r = requests.get(WIKIPEDIA_API_URL, params=params, timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise ScrapError(f'Request to wikipedia API failed: {str(e)}')
