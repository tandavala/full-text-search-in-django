from rest_framework.test import APIClient, APITestCase
from django.contrib.postgres.search import SearchVector
from catalog.models import Wine, WineSearchWord
from catalog.serializers import WineSerializer


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
    #     response = self.client.get('/api/v1/catalog/wines/')

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
        self.assertEqual(4, len(response.data))
        self.assertEqual('grigio', response.data['results'][0]['word'])
