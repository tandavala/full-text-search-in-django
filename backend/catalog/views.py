from rest_framework.generics import ListAPIView

from .models import Wine, WineSearchWord
from .serializers import WineSerializer, WineSearchWordSerializer
from .filters import WineFilterSet, WineSearchWordFilterSet


class WinesView(ListAPIView):
    queryset = Wine.objects.all()
    serializer_class = WineSerializer
    filterset_class = WineFilterSet


class WineSearchWordsView(ListAPIView):
    queryset = WineSearchWord.objects.all()
    serializer_class = WineSearchWordSerializer
    filterset_class = WineSearchWordFilterSet
