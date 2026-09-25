from django.contrib import admin
from django.urls import include, path
from core.views import root_redirect_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect_view, name='root'),
    path('', include('core.urls')),
    path('demo/', include('demo.urls')),
]
