from django.shortcuts import render
from django.shortcuts import HttpResponse
# Create your views here.

def about(request):
    return render(request, 'finder/about.html')

def contact(request):
    return render(request, 'finder/contact.html')

def signUp(request):
    return render(request, 'finder/signUp.html')

def login(request):
    return render(request, 'finder/login.html')

def home(request):
    return render(request, 'finder/home.html')