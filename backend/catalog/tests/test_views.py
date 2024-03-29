import json
import pathlib
from unittest.mock import patch
import uuid

from django.conf import settings
from django.contrib.postgres.search import SearchVector

from elasticsearch_dsl import connections
from rest_framework.test import APIClient, APITestCase

from catalog.constants import ES_MAPPING
from catalog.models import Wine, WineSearchWord
from catalog.serializers import WineSerializer
from urllib.parse import parse_qs, urlencode, urlsplit


class ViewTests(APITestCase):

    fixtures = ['test_wines.json']

    def setUp(self):
        Wine.objects.all().update(search_vector=(
            SearchVector('variety', weight='A') +
            SearchVector('winery', weight='A') +
            SearchVector('description', weight='B')
        ))
        self.client = APIClient()

    # def test_empty_query_returns_everything(self):
    #     response = self.client.get('/api/v1/catalog/pg-wines/')
    #     wines = Wine.objects.all()
    #     self.assertJSONEqual(
    #         response.content, WineSerializer(wines, many=True).data)

    def test_query_matches_variety(self):
        response = self.client.get('/api/v1/catalog/wines/', {
            'query': 'Cabernet'
        })
        self.assertEqual(1, response.data['count'])
        self.assertEqual("58ba903f-85ff-45c2-9bac-6d0732544841",
                         response.data['results'][0]['id'])

    def test_query_matches_winery(self):
        response = self.client.get('/api/v1/catalog/wines/', {
            'query': 'Barnard'
        })
        self.assertEqual(1, response.data['count'])
        self.assertEqual("21e40285-cec8-417c-9a26-4f6748b7fa3a",
                         response.data['results'][0]['id'])

    def test_query_matches_description(self):
        response = self.client.get('/api/v1/catalog/wines/', {
            'query': 'wine'
        })

        self.assertEqual(4, len(response.data))
        self.assertEqual([
            "58ba903f-85ff-45c2-9bac-6d0732544841",
            "21e40285-cec8-417c-9a26-4f6748b7fa3a",
            "0082f217-3300-405b-abc6-3adcbecffd67"
        ], [item['id'] for item in response.data['results']])

    def test_can_filter_on_country(self):
        response = self.client.get('/api/v1/catalog/wines/', {
            'country': 'France'
        })
        self.assertEquals(
            "0082f217-3300-405b-abc6-3adcbecffd67", response.data['results'][0]['id'])

    def test_can_filter_on_points(self):
        response = self.client.get('/api/v1/catalog/wines/', {
            'points': 87
        })
        self.assertEquals(1, response.data['count'])
        self.assertEquals(
            "21e40285-cec8-417c-9a26-4f6748b7fa3a", response.data['results'][0]['id'])

    def test_query_matches_description(self):
        response = self.client.get('/api/v1/catalog/wines/', {
            'query': 'wine',
        })
        self.assertEquals(4, response.data['count'])
        self.assertCountEqual([
            "58ba903f-85ff-45c2-9bac-6d0732544841",
            "21e40285-cec8-417c-9a26-4f6748b7fa3a",
            "0082f217-3300-405b-abc6-3adcbecffd67",
            "000bbdff-30fc-4897-81c1-7947e11e6d1a"],
            [item['id'] for item in response.data['results']])

    def test_country_must_be_exact_match(self):
        response = self.client.get('/api/v1/catalog/wines/', {
            'country': 'Frances',
        })
        self.assertEquals(0, response.data['count'])
        # self.assertJSONEqual(response.data['results'], [])

    def test_search_can_be_paginated(self):
        response = self.client.get('/api/v1/catalog/wines/', {
            'limit': 1,
            'offset': 1,
        })

        self.assertEqual(4, response.data['count'])
        self.assertEqual(1, len(response.data['results']))
        self.assertIsNotNone(response.data['previous'])
        self.assertIsNotNone(response.data['next'])

    def test_search_vector_populated_on_save(self):
        wine = Wine.objects.create(
            country='US', points=80, price=1.99, variety='Pinot Grigio', winery='Charles Shaw')
        wine = Wine.objects.get(id=wine.id)
        self.assertEqual(
            "'charl':3A 'grigio':2A 'pinot':1A 'shaw':4A", wine.search_vector)

    def test_wine_search_words_populated_on_save(self):
        WineSearchWord.objects.all().delete()
        Wine.objects.create(
            country='US',
            description='A cheap, but inoffensive wine.',
            points=80,
            price=1.99,
            variety='Pinot Grigio',
            winery='Charles Shaw'
        )
        wine_search_words = WineSearchWord.objects.all().order_by(
            'word').values_list('word', flat=True)
        self.assertListEqual([
            'a',
            'but',
            'charles',
            'cheap',
            'inoffensive',
            'shaw',
            'wine'
        ], list(wine_search_words))

    def test_suggests_words_for_spelling_mistakes(self):
        WineSearchWord.objects.bulk_create([
            WineSearchWord(word='pinot'),
            WineSearchWord(word='grigio'),
            WineSearchWord(word='noir'),
            WineSearchWord(word='merlot'),
        ])
        response = self.client.get('/api/v1/catalog/wine-search-words/', {
            'query': 'greegio'
        })
        self.assertEqual(2, len(response.data))

        self.assertEqual('grigio', response.data[0]['word'])


class ESViewTests(APITestCase):
    def setUp(self):
        self.index = f'test-wine-{uuid.uuid4()}'
        self.connection = connections.get_connection()
        self.connection.indices.create(index=self.index, body={
            'settings': {
                'number_of_shards': 1,
                'number_of_replicas': 0,
            },
            'mappings': ES_MAPPING,
        })

        # Load fixture data
        fixture_path = pathlib.Path(
            settings.BASE_DIR / 'catalog' / 'fixtures' / 'test_wines.json')
        with open(fixture_path, 'rt') as fixture_file:
            fixture_data = json.loads(fixture_file.read())
            for wine in fixture_data:
                fields = wine['fields']
                self.connection.create(index=self.index, id=fields['id'], body={
                    'country': fields['country'],
                    'description': fields['description'],
                    'points': fields['points'],
                    'price': fields['price'],
                    'variety': fields['variety'],
                    'winery': fields['winery'],
                }, refresh=True)

        self.mock_constants = patch('catalog.views.constants').start()
        self.mock_constants.ES_INDEX = self.index

    def test_query_matches_variety(self):
        response = self.client.get('/api/v1/catalog/es-wines/', {
            'query': 'Cabernet',
        })
        results = response.data['results']
        self.assertEquals(1, len(results))
        self.assertEquals(
            "58ba903f-85ff-45c2-9bac-6d0732544841", results[0]['id'])

    def test_no_previous_page_for_first_page_of_results(self):
        response = self.client.get('/api/v1/catalog/es-wines/', {
            'limit': 1,
            'offset': 0,
            'query': 'wine',
        })
        self.assertIsNone(response.data['previous'])

    def test_previous_page(self):
        response = self.client.get('/api/v1/catalog/es-wines/', {
            'limit': 1,
            'offset': 1,
            'query': 'wine',
        })

        previous = urlsplit(response.data['previous'])
        query_params = parse_qs(previous.query)
        offset = int(query_params['offset'][0])

        self.assertEquals(0, offset)

    def test_no_next_page_for_last_page_of_results(self):
        response = self.client.get('/api/v1/catalog/es-wines/', {
            'limit': 1,
            'offset': 3,
            'query': 'wine',
        })
        self.assertIsNone(response.data['next'])

    def test_next_page(self):
        response = self.client.get('/api/v1/catalog/es-wines/', {
            'limit': 1,
            'offset': 1,
            'query': 'wine',
        })

        next = urlsplit(response.data['next'])
        query_params = parse_qs(next.query)
        offset = int(query_params['offset'][0])

        self.assertEquals(2, offset)

    def test_search_results_returned_in_correct_order(self):
        response = self.client.get('/api/v1/catalog/es-wines/', {
            'query': 'Chardonnay',
        })
        results = response.data['results']
        self.assertEquals(2, len(results))
        self.assertListEqual([
            "0082f217-3300-405b-abc6-3adcbecffd67",
            "000bbdff-30fc-4897-81c1-7947e11e6d1a",
        ], [item['id'] for item in results])

    def test_description_highlights_matched_words(self):
        response = self.client.get('/api/v1/catalog/es-wines/', {
            'query': 'wine',
        })
        results = response.data['results']
        self.assertEquals('A delicious bottle of <mark>wine</mark>.',
                          results[0]['description'])

    def test_suggests_words_for_spelling_mistakes(self):
        response = self.client.get('/api/v1/catalog/es-wine-search-words/', {
            'query': 'greegio',
        })

        self.assertEqual(2, len(response.data))
        self.assertEqual('grigio', response.data[0]['word'])
        self.assertEqual('grego', response.data[1]['word'])

    def tearDown(self):

        self.mock_constants.stop()

        self.connection.indices.delete(index=self.index)
