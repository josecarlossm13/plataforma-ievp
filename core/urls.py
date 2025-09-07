# core/urls.py
from django.urls import path
from .views import TermListView, TermDetailView, AreaListView, SubAreaListView, poster_view, thesis_view, documentation_view, contacts_view, home
from . import views


urlpatterns = [
    path('terms/', TermListView.as_view(), name='term-list'),
    path('terms/subarea/<str:ref>/', TermListView.as_view(), name='term-list-by-subarea'),  # termos filtrados por subarea
    path('terms/<str:ref>/', TermDetailView.as_view(), name='term_detail'),

    path('areas/', AreaListView.as_view(), name='area-list'),
    path('subareas/', SubAreaListView.as_view(), name='subarea-list'),                         # todas as subareas
    path('subareas/<int:area_id>/', SubAreaListView.as_view(), name='subarea-list-by-area'),

    path('tutorial/', views.tutorial_view, name='tutorial'),
    path('poster/', poster_view, name="poster"),
    path('thesis/', thesis_view, name="thesis"),
    path('documentation/', documentation_view, name="documentation"),
    path('contacts/', contacts_view, name="contacts"),
]