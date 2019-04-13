from collections import defaultdict
import json

from wikipedia_scrapper import fetch_airlines_destinations


class AirlinesDestinations:
    def __init__(self, airport_name, value=None):
        self.airport_name = airport_name
        self.value = value

    def fetch(self):
        self.value = fetch_airlines_destinations(self.airport_name)

    def compare(self, other):
        added = defaultdict(set)
        removed = defaultdict(set)

        these_destinations_set = {k: set(v) for k, v in self.value.items()}
        other_destinations_set = {k: set(v) for k, v in other.value.items()}

        for airline, destinations in these_destinations_set.items():
            try:
                other_destinations = other_destinations_set[airline]
                added[airline] |= destinations - other_destinations
                removed[airline] |= other_destinations - destinations
            except KeyError:
                added[airline] |= destinations

        for airline, destinations in other_destinations_set.items():
            if airline not in self.value:
                removed[airline] |= destinations

        return added, removed,


class AirlinesDestinationsSerializer:
    def __init__(self, airport_name):
        self.airport_name = airport_name

    @property
    def filename(self):
        return f'{self.airport_name}.json'

    def serialize(self, airlines_destinations):
        return airlines_destinations.value

    def unserialize(self, value):
        return AirlinesDestinations(self.airport_name, value)

    def read_last_known(self):
        with open(self.filename, 'r') as f:
            return self.unserialize(json.load(f))

    def save(self, airlines_destinations):
        value = self.serialize(airlines_destinations)
        with open(self.filename, 'w') as f:
            json.dump(value, f)
