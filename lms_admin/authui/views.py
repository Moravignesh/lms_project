from django.shortcuts import render


def login(request):
    return render(request, "authui/login.html")


def signup(request):
    return render(request, "authui/signup.html")
