import responses
import unittest
import urllib.parse
from collections import namedtuple
from unittest.mock import patch

from airport_watcher.wikipedia_scrapper import downloader, ScrapError


class DownloaderTest(unittest.TestCase):
    def test_choose_airport_page_section(self):
        TestData = namedtuple('TestData', 'airport_name sections correct_section')
        test_set = (
            TestData(
                airport_name='Innsbruck Airport',
                sections=[
                    {'index': 0, 'line': 'Facilities'},
                    {'index': 1, 'line': 'Airlines and destinations'},
                    {'index': 2, 'line': 'Statistics'},
                    {'index': 3, 'line': 'Ground transportation'},
                ],
                correct_section=1),
            TestData(
                airport_name='Valencia Airport',
                sections=[
                    {'index': 0, 'line': 'Facilities'},
                    {'index': 1, 'line': 'Airlines and destinations'},
                    {'index': 2, 'line': 'Passenger'},
                    {'index': 3, 'line': 'Cargo'},
                ],
                correct_section=2),
            TestData(
                airport_name='Berlin Schönefeld Airport',
                sections=[
                    {'index': 0, 'line': 'History'},
                    {'index': 1, 'line': 'Terminals'},
                    {'index': 2, 'line': 'Passenger'},
                    {'index': 3, 'line': 'Airlines and destinations'},
                    {'index': 4, 'line': 'Cargo'},
                ],
                correct_section=2),
        )

        for test_data in test_set:
            with self.subTest(test_data=test_data._asdict()):
                with patch('airport_watcher.wikipedia_scrapper.downloader._fetch_page_sections') as mock:
                    mock.return_value = test_data.sections
                    section = downloader._choose_airport_page_section(test_data.airport_name)
                    mock.assert_called_once_with(page=test_data.airport_name)
                    self.assertEqual(section, test_data.correct_section)

    def test_choose_airport_page_section_not_found(self):
        with patch('airport_watcher.wikipedia_scrapper.downloader._fetch_page_sections') as mock:
            mock.return_value = [
                {'index': 0, 'line': 'History'},
                {'index': 1, 'line': 'Architecture'},
                {'index': 2, 'line': 'Geography'},
            ]
            with self.assertRaises(ScrapError):
                downloader._choose_airport_page_section('Naples')
            mock.assert_called_once_with(page='Naples')

    @responses.activate
    def test_fetch_destinations_section_wikitext(self):
        query_string = urllib.parse.urlencode({
            'action': 'parse',
            'page': 'Athens International Airport',
            'redirects': True,
            'prop': 'sections',
            'format': 'json',
        })
        responses.add(
            responses.GET,
            f'{downloader.WIKIPEDIA_API_URL}?{query_string}',
            json={
                'parse': {
                    'sections': [
                        {'index': 0, 'line': 'History'},
                        {'index': 1, 'line': 'Future development'},
                        {'index': 2, 'line': 'Terminals'},
                        {'index': 3, 'line': 'Airlines and destinations'},
                        {'index': 4, 'line': 'Passenger'},
                        {'index': 5, 'line': 'Cargo'},
                    ]
                }
            }
        )

        query_string = urllib.parse.urlencode({
            'action': 'parse',
            'page': 'Athens International Airport',
            'redirects': True,
            'section': 4,
            'prop': 'wikitext',
            'format': 'json',
        })
        responses.add(
            responses.GET,
            f'{downloader.WIKIPEDIA_API_URL}?{query_string}',
            json={
                'parse': {
                    'wikitext': {
                        '*': 'MOCKED DATA'
                    }
                }
            }
        )

        expected_wikitext = 'MOCKED DATA'
        wikitext = downloader.fetch_destinations_section_wikitext('Athens International Airport')
        self.assertEqual(wikitext, expected_wikitext)
        self.assertEqual(len(responses.calls), 2)
