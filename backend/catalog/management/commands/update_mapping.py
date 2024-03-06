from django.core.management import BaseCommand, CommandError
from elasticsearch_dsl import connections


class Command(BaseCommand):
    hel = 'Updates a mapping on an Elasticsearch index.'

    def handle(self, *args, **kwargs):
        index = 'wine'
        self.stdout.write(f'Updating mapping on "{index}" index...')
        connection = connections.get_connection()

        if connection.indices.exists(index=index):
            connection.indices.put_mapping(index=index, body={
                'properties': {
                    'varieties': {
                        'type': 'text',
                        'analyzer': 'english'
                    },
                    'winery': {
                        'type': 'text',
                        'analyzer': 'english'
                    },
                    'description': {
                        'type': 'text',
                        'analyzer': 'english'
                    }
                }
            })
            self.stdout.write(f'Updated mapping on "{index}" successfully')
        else:
            raise CommandError(f'Index "{index}" does not exists')
