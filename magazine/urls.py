from django.urls import path
from . import views
from .feeds import LatestArticlesFeed

app_name = 'magazine'

urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('tag/<slug:tag_slug>/', views.article_list, name='article_list_tagged'),
    path('<int:article_id>/<slug:slug>/', views.article_detail, name='article_detail'),
    path('<int:article_id>/share/', views.article_share, name='article_share'),
    path('<int:article_id>/comment/', views.article_comment, name='article_comment'),
    path('feed/', LatestArticlesFeed(), name='article_feed'),
    path('search/', views.article_search, name='article_search'),
]