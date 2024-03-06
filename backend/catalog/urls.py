from django.urls import path
from .views import WinesView, WineSearchWordsView, ESWinesView

urlpatterns = [
    path('wines/', WinesView.as_view()),
    path('wine-search-words/', WineSearchWordsView.as_view()),
    path('es-wines/', ESWinesView.as_view()),
]
