import requests


def get_destinations_section_wikitext(airport_name):
    section = _choose_airport_page_section(airport_name)
    return _get_section_wikitext(page=airport_name, section=section)


def _choose_airport_page_section(airport_name):
    airlines_destinations_section = None
    for section in _get_page_sections(page=airport_name):
        if section['line'] == 'Airlines and destinations':
            airlines_destinations_section = section['index']
        elif section['line'] == 'Passenger':
            return section['index']

    if airlines_destinations_section:
        return airlines_destinations_section
    else:
        raise ValueError(f'"Airlines and destinations" section not found in the wikipedia page for {airport_name}.')


def _get_page_sections(page):
    query_params = {
        'action': 'parse',
        'page': page,
        'redirects': True,
        'prop': 'sections',
    }
    r = _query_wikipedia(query_params)
    return r['parse']['sections']


def _get_section_wikitext(page, section):
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
    r = requests.get('https://en.wikipedia.org/w/api.php', params=params, timeout=60)
    r.raise_for_status()
    return r.json()
