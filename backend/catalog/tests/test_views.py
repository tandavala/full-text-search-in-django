from rest_framework.test import APIClient, APITestCase

from catalog.models import Wine
from catalog.serializers import WineSerializer


class ViewTests(APITestCase):

    fixtures = ['test_wines.json']

    def setUp(self):
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

        self.assertEqual(3, len(response.data))
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
        self.assertEquals(3, response.data['count'])
        self.assertCountEqual([
            "58ba903f-85ff-45c2-9bac-6d0732544841",
            "21e40285-cec8-417c-9a26-4f6748b7fa3a",
            "0082f217-3300-405b-abc6-3adcbecffd67"],
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
        # Count is equal to total number of results in database
        # We're loading 3 wines into the database via fixtures
        self.assertEqual(3, response.data['count'])
        self.assertEqual(1, len(response.data['results']))
        self.assertIsNotNone(response.data['previous'])
        self.assertIsNotNone(response.data['next'])
