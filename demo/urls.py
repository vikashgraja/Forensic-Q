from django.urls import path

from . import views

urlpatterns = [
    path("", views.tabulator_demo_view, name="demo_index"),
    path("tabulator/", views.tabulator_demo_view, name="tabulator_demo"),
    path("tabulator-demo/", views.tabulator_demo_view, name="tabulator_demo_legacy"),
    path("sandbox/", views.component_test_view, name="component_sandbox"),
    path("components_test/", views.component_test_view, name="test_dashboard_legacy"),
]
