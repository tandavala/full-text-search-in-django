ES_INDEX = 'wine'

ES_MAPPING = {
    'dynamic': 'strict',
    'properties': {
        'variety': {
            'type': 'text',
            'analyzer': 'english',
        },
        'country': {
            'type': 'keyword',
        },
        'price': {
            'type': 'keyword',
        },
        'winery': {
            'type': 'text',
            'analyzer': 'english',
        },
        'description': {
            'type': 'text',
            'analyzer': 'english',
        },
        'points': {
            'type': 'float',
        }
    }
}
