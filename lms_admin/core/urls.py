from django.urls import path
from django.views.generic import RedirectView
from .views import dashboard

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('', RedirectView.as_view(url='/dashboard/', permanent=True)),
]
