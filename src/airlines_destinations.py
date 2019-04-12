from collections import defaultdict
import json

from wikipedia_scrapper import get_airlines_destinations


class AirlinesDestinations:
    def __init__(self, airport_name, value=None):
        self.airport_name = airport_name
        self.value = value

    def fetch(self):
        self.value = get_airlines_destinations(self.airport_name)

    def compare(self, other):
        added = defaultdict(dict)
        changed = defaultdict(dict)
        removed = defaultdict(dict)

        for airline, destinations in self.value.items():
            try:
                other_destinations = other.value[airline]
                added_destinations, removed_destinations, changed_destinations = (
                    self._compare_destinations(destinations, other_destinations)
                )
                added[airline].update(added_destinations)
                changed[airline].update(changed_destinations)
                removed[airline].update(removed_destinations)
            except KeyError:
                added[airline].update(destinations)

        for airline, destinations in other.value.items():
            if airline not in self.value:
                removed[airline].update(destinations)

        return added, changed, removed,

    @staticmethod
    def _compare_destinations(a, b):
        added = {}
        changed = {}
        removed = {}
        for destination_name, a_attributes in a.items():
            try:
                if a_attributes != b[destination_name]:
                    changed[destination_name] = a_attributes
            except KeyError:
                added[destination_name] = a_attributes

        for destination_name, b_attributes in b.items():
            if destination_name not in a:
                removed[destination_name] = b_attributes

        return added, changed, removed,


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
