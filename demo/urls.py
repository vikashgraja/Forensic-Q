from django.urls import path
from . import views

urlpatterns = [
    path('', views.component_test_view, name='home'),
    path('components_test/', views.component_test_view, name='test_dashboard'),
    path('tabulator-demo/', views.tabulator_demo_view, name='tabulator_demo'),
]
