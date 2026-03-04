from django.urls import path
from .views import dashboard

urlpatterns = [
    path("analytics/dashboard/", dashboard, name="analytics_dashboard"),
]
