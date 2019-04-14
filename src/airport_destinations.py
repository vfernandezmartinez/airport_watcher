from collections import defaultdict
import json

from wikipedia_scrapper import fetch_airlines_destinations, get_details_url


class AirportDestinations:
    class DestinationsUnknown(Exception):
        pass

    def __init__(self, airport_name, destinations):
        self.airport_name = airport_name
        self.destinations = destinations

    @staticmethod
    def _filename(airport_name):
        return f'{airport_name}.json'

    @property
    def filename(self):
        return self._filename(self.airport_name)

    @classmethod
    def fetch(cls, airport_name):
        return cls(airport_name,
                   fetch_airlines_destinations(airport_name))

    @classmethod
    def last_known(cls, airport_name):
        try:
            with open(cls._filename(airport_name), 'r') as f:
                return cls(airport_name, json.load(f))
        except (FileNotFoundError, json.decoder.JSONDecodeError,):
            raise cls.DestinationsUnknown()

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.destinations, f)


class AirportDestinationsDiff:
    def __init__(self, before, after):
        if before.airport_name != after.airport_name:
            raise ValueError("Computing the difference between distinct airports doesn't make sense.")

        self.airport_name = before.airport_name
        self.added = defaultdict(set)
        self.removed = defaultdict(set)
        self._compute_diff(before, after)

    def _compute_diff(self, before, after):
        destinations_before = {k: set(v) for k, v in before.destinations.items()}
        destinations_after = {k: set(v) for k, v in after.destinations.items()}

        for airline, airline_destinations_after in destinations_after.items():
            try:
                airline_destinations_before = destinations_before[airline]
                self.added[airline] |= airline_destinations_after - airline_destinations_before
                self.removed[airline] |= airline_destinations_before - airline_destinations_after
            except KeyError:
                self.added[airline] |= airline_destinations_after

        for airline, airline_destinations_before in destinations_before.items():
            if airline not in destinations_after:
                self.removed[airline] |= airline_destinations_before

    def render_plaintext(self):
        contents = self._render_airlines_diff()
        if contents:
            return '{}\n\n{}\n\nCheck here for more details: {}'.format(
                self.airport_name, contents, get_details_url(self.airport_name)
            )

    def _render_airlines_diff(self):
        rendered_lines = []

        all_keys = self.added.keys() | self.removed.keys()
        for airline in all_keys:
            rendered_lines.extend(
                self._render_destinations(f'{airline} offers new destinations:',
                                          self.added.get(airline)))
            rendered_lines.extend(
                self._render_destinations(f'{airline} discontinues these destinations:',
                                          self.removed.get(airline)))

        return '\n'.join(rendered_lines)

    @staticmethod
    def _render_destinations(title, destinations):
        lines = []

        if destinations:
            lines.append(title)
            for destination in sorted(destinations):
                lines.append(f"  - {destination}")
            lines.append('')

        return lines
