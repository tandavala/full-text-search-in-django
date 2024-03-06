from django.core.management.base import BaseCommand

from elasticsearch_dsl import connections


class Command(BaseCommand):
    help = 'Delete an Elasticsearch index.'

    def handle(self, *args, **kwargs):
        index = 'wine'
        self.stdout.write(f'Deleting index "{index}"...')
        connection = connections.get_connection()
        if connection.indices.exists(index=index):
            connection.indices.delete(index=index)
