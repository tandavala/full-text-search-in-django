from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Match
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog import constants

from .models import Wine, WineSearchWord
from .serializers import WineSerializer, WineSearchWordSerializer
from .filters import WineFilterSet, WineSearchWordFilterSet


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
    def get(self, request, *args, **kwargs):
        query = self.request.query_params.get('query')

        # Build Elasticsearch query.
        search = Search(index=constants.ES_INDEX)  # changed
        response = search.query('bool', should=[
            Match(variety=query),
            Match(winery=query),
            Match(description=query)
        ]).params(size=100).execute()

        return Response(data={
            'count': response.hits.total.value,
            'next': None,
            'previous': None,
            'results': [{
                'id': hit.meta.id,
                'country': hit.country,
                'description': hit.description,
                'points': hit.points,
                'price': hit.price,
                'variety': hit.variety,
                'winery': hit.winery,
            } for hit in response],
        })
