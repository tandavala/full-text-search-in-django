from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from elasticsearch_dsl import Q

from catalog import constants

from .models import Wine, WineSearchWord
from .serializers import WineSerializer, WineSearchWordSerializer
from .filters import WineFilterSet, WineSearchWordFilterSet

from urllib.parse import SplitResult, urlencode, urlsplit
from elasticsearch_dsl.query import Match, Term


class WinesView(ListAPIView):
    queryset = Wine.objects.all()
    serializer_class = WineSerializer
    filterset_class = WineFilterSet

    def filter_queryset(self, request):
        return super().filter_queryset(request)[:100]


class WineSearchWordsView(ListAPIView):
    queryset = WineSearchWord.objects.all()
    serializer_class = WineSearchWordSerializer
    filterset_class = WineSearchWordFilterSet


class ESWinesView(APIView):
    def _build_url(self, params, new_offset):
        url = self.request.build_absolute_uri()
        old_result = urlsplit(url)
        new_result = SplitResult(
            old_result.scheme,
            old_result.netloc,
            old_result.path,
            query=urlencode({
                **params,
                'offset': new_offset,
            }, doseq=True),
            fragment='',
        )
        return new_result.geturl()

    def _get_previous_page(self, params):
        limit, offset = params.get('limit'), params.get('offset')
        if offset > 0:
            return self._build_url(params, offset - limit)
        else:
            return None

    def _get_next_page(self, params, count):
        limit, offset = params.get('limit'), params.get('offset')
        if (offset + limit) < count:
            return self._build_url(params, offset + limit)
        else:
            return None

    def get(self, request, *args, **kwargs):
        query = self.request.query_params.get('query')
        country = self.request.query_params.get('country')
        points = self.request.query_params.get('points')
        limit = int(self.request.query_params.get('limit', 10))
        offset = int(self.request.query_params.get('offset', 0))

        # Build Elasticsearch query.
        search = Search(index=constants.ES_INDEX)
        q = {'should': [], 'filter': []}

        # Build should clause.
        if query:
            q['should'] = [
                Match(variety={'query': query, 'boost': 3.0}),
                Match(winery={'query': query, 'boost': 2.0}),
                Match(description={'query': query, 'boost': 1.0})
            ]
            q['minimum_should_match'] = 1
            search = search.highlight_options(
                number_of_fragments=0,
                pre_tags=['<mark>'],
                post_tags=['</mark>']
            )
            search = search.highlight('variety', 'winery', 'description')

        # Build filter clause.
        if country:
            q['filter'].append(Term(country=country))
        if points:
            q['filter'].append(Term(points=points))

        search = search.query('bool', **q)[offset: offset + limit]

        response = search.execute()

        return Response(data={
            'count': response.hits.total.value,
            'next': self._get_next_page({
                'limit': limit,
                'offset': offset,
                'query': query,
            }, count=response.hits.total.value),
            'previous': self._get_previous_page({
                'limit': limit,
                'offset': offset,
                'query': query,
            }),
            'results': [{
                'id': hit.meta.id,
                'country': hit.country,
                'description': (
                    hit.meta.highlight.description[0]
                    if 'highlight' in hit.meta and 'description' in hit.meta.highlight
                    else hit.description
                ),
                'points': hit.points,
                'price': hit.price,
                'variety': (
                    hit.meta.highlight.variety[0]
                    if 'highlight' in hit.meta and 'variety' in hit.meta.highlight
                    else hit.variety
                ),
                'winery': (
                    hit.meta.highlight.winery[0]
                    if 'highlight' in hit.meta and 'winery' in hit.meta.highlight
                    else hit.winery
                ),
            } for hit in response],
        })


class ESWineSearchWordsView(APIView):
    def get(self, request, *args, **kwargs):
        query = self.request.query_params.get('query')

        # Build Elasticsearch query.
        search = Search().suggest('result', query, term={
            'field': 'all_text'
        })

        response = search.execute()

        # Extract words.
        options = response.suggest.result[0]['options']
        words = [{'word': option['text']} for option in options]

        return Response(data=words)
