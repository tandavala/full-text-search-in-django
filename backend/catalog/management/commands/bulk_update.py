from django.core.management.base import BaseCommand
from elasticsearch_dsl import connections
from elasticsearch.helpers import bulk

from catalog.models import Wine


class Command(BaseCommand):
    help = 'Updates the Elasticsearch index.'

    def _documento_generator(self):
        for wine in Wine.objects.iterator():
            yield {
                '_index': 'wine',
                '_id': wine.id,
                'variety': wine.variety,
                'winery': wine.winery,
                'description': wine.description,
                'country': wine.country,
                'price': wine.price,
                'points': wine.points
            }

    def handle(self, *args, **kwargs):
        index = 'wine'
        self.stdout.write(f'Bulk updating documents on "{index}" index...')
        connection = connections.get_connection()
        succeeded, _ = bulk(
            connection, actions=self._documento_generator(), stats_only=True)
        self.stdout.write(
            f'Updated {succeeded} documents on "{index}" successfully')
