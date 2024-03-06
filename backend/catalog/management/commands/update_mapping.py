from django.core.management import BaseCommand, CommandError
from elasticsearch_dsl import connections
from catalog.constants import ES_INDEX, ES_MAPPING


class Command(BaseCommand):
    hel = 'Updates a mapping on an Elasticsearch index.'

    def handle(self, *args, **kwargs):  # changed
        self.stdout.write(f'Updating mapping on "{ES_INDEX}" index...')
        connection = connections.get_connection()
        if connection.indices.exists(index=ES_INDEX):
            connection.indices.put_mapping(index=ES_INDEX, body=ES_MAPPING)
            self.stdout.write(f'Updated mapping on "{ES_INDEX}" successfully')
        else:
            raise CommandError(f'Index "{ES_INDEX}" does not exist')
