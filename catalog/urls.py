from django.urls import include, path, re_path
from . import views
from django.contrib.auth import views as auth_views

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('user/', views.user, name='user'),
    path('register/', views.register, name='register'),
    path('browse/', views.browse_tags, name='browse'),
    path('favorites/', views.favorite, name='favorites'),
    path('post/new/', views.post_new, name='post_new'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('editor/', views.editor, name='editor'),
    path('analyze/', views.analyze, name='analyze'),
    path('browse/<str:tag>/', views.index_tag, name='index_tag'),
    path('profile/<int:id>', views.profile, name='profile'),
    path('profile/<int:id>/edit', views.profile_edit, name='profile_edit'),
    path('feed/', views.feed, name='feed'),
    path('feed/<str:tag>', views.feed_tag, name='feed_tag'),
    re_path(r'^search/$', views.search, name='search'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

