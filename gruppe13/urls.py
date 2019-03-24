from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('catalog.urls')),
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path(r'tinymce/', include('tinymce.urls')),
]
