from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login, name="authui_login"),
    path("signup/", views.signup, name="authui_signup"),
]
