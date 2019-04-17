import unittest

from airport_watcher import wikipedia_scrapper


class WikitextScrapperTest(unittest.TestCase):
    def test_details_url(self):
        expected_result = 'https://en.wikipedia.org/wiki/Ibiza_Airport#Airlines_and_destinations'
        result = wikipedia_scrapper.details_url('Ibiza Airport')
        self.assertEqual(result, expected_result)
