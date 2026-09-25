from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.portal_login_view, name='portal_login'),
    path('logout/', views.portal_logout_view, name='portal_logout'),
]
