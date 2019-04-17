import unittest
from unittest import mock

from airport_watcher import airport_destinations
from airport_watcher.wikipedia_scrapper import details_url


class AirportDestinationsTest(unittest.TestCase):
    def setUp(self):
        airport_destinations.AirportDestinations.storage_dir = '/tmp'

    def test_filename(self):
        self.assertEqual(airport_destinations.AirportDestinations._filename('Kuala Lumpur Airport'),
                         '/tmp/Kuala Lumpur Airport.json')
        airport = airport_destinations.AirportDestinations('Kuala Lumpur Airport', {})
        self.assertEqual(airport.filename, '/tmp/Kuala Lumpur Airport.json')

    def test_fetch(self):
        with mock.patch('airport_watcher.airport_destinations.fetch_airlines_destinations',
                        return_value={'SilkAir': ['Singapore']}) as fetch_mock:
            airport = airport_destinations.AirportDestinations.fetch('Kuala Lumpur Airport')
            fetch_mock.assert_called_once_with('Kuala Lumpur Airport')
            self.assertIsInstance(airport, airport_destinations.AirportDestinations)
            self.assertEqual(airport.airport_name, 'Kuala Lumpur Airport')
            self.assertEqual(airport.destinations, {'SilkAir': ['Singapore']})

    def test_last_known(self):
        with mock.patch('builtins.open',
                        mock.mock_open(read_data='{"Cathay Pacific": ["Hong Kong"]}')) as open_mock:
            airport = airport_destinations.AirportDestinations.last_known('Cape Town Airport')
            open_mock.assert_called_once_with('/tmp/Cape Town Airport.json', 'r')
            expected_destinations = {'Cathay Pacific': ['Hong Kong']}
            self.assertEqual(airport.airport_name, 'Cape Town Airport')
            self.assertEqual(airport.destinations, expected_destinations)

    def test_save(self):
        open_mock = mock.mock_open()
        with mock.patch('builtins.open', open_mock):
            with mock.patch('json.dump') as dump_mock:
                destinations = {'LATAM Argentina': ['Buenos Aires']}
                airport = airport_destinations.AirportDestinations(
                    'Iguazú Airport', destinations)
                airport.save()
                open_mock.assert_called_once_with('/tmp/Iguazú Airport.json', 'w')
                dump_mock.assert_called_once_with(destinations, open_mock())


class AirportDestinationsDiffTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_cannot_compare_different_airports(self):
        airport1 = airport_destinations.AirportDestinations('Fiumicino Airport', {})
        airport2 = airport_destinations.AirportDestinations('Ciampino Airport', {})

        with self.assertRaises(ValueError):
            airport_destinations.AirportDestinationsDiff(airport1, airport2)

    def test_compute_diff(self):
        before = airport_destinations.AirportDestinations('Darwin Airport', {
            'Donghai Airlines': ['Shenzhen'],
            'Jetstar': ['Bali', 'Brisbane', 'Sydney'],
            'Qantas': ['Adelaide', 'Brisbane', 'Melbourne', 'Sydney'],
            'Virgin Australia': ['Adelaide', 'Alice Springs'],
        })
        after = airport_destinations.AirportDestinations('Darwin Airport', {
            'Jetstar': ['Sydney'],
            'Qantas': ['Adelaide', 'Ayers Rock', 'Brisbane', 'Melbourne', 'Perth', 'Sydney'],
            'SilkAir': ['Singapore'],
            'Virgin Australia': ['Adelaide', 'Alice Springs'],
        })

        expected_added = {
            'Jetstar': set(),
            'Qantas': {'Ayers Rock', 'Perth'},
            'SilkAir': {'Singapore'},
            'Virgin Australia': set(),
        }
        expected_removed = {
            'Donghai Airlines': {'Shenzhen'},
            'Jetstar': {'Bali', 'Brisbane'},
            'Qantas': set(),
            'Virgin Australia': set(),
        }

        diff = airport_destinations.AirportDestinationsDiff(before, after)
        self.assertEqual(diff.added, expected_added)
        self.assertEqual(diff.removed, expected_removed)

    def test_render_plaintext(self):
        before = airport_destinations.AirportDestinations('Gdansk Airport', {})
        after = airport_destinations.AirportDestinations('Gdansk Airport', {})
        diff = airport_destinations.AirportDestinationsDiff(before, after)
        diff.added = {
            'LOT Airlines': {'Lanzarote', 'Malta'},
        }
        diff.removed = {
            'Wizz Air': {'Sofia'}
        }

        expected_plaintext = '\n'.join([
            'Gdansk Airport',
            '',
            'LOT Airlines offers new destinations:',
            '  - Lanzarote',
            '  - Malta',
            '',
            'Wizz Air discontinues these destinations:',
            '  - Sofia',
            '',
            '',
            'Check here for more details: {}'.format(details_url('Gdansk Airport'))
        ])
        plaintext = diff.render_plaintext()
        self.assertEqual(plaintext, expected_plaintext)

    def test_render_plaintext_empty(self):
        before = airport_destinations.AirportDestinations('Gdansk Airport', {})
        after = airport_destinations.AirportDestinations('Gdansk Airport', {})
        diff = airport_destinations.AirportDestinationsDiff(before, after)
        self.assertIsNone(diff.render_plaintext())
