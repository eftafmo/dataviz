from django.shortcuts import render


def home(request):
    return render(request, 'homepage.html')

def grants(request):
    return render(request, 'grants.html')

def partners(request):
    return render(request, 'partners.html')

def projects(request):
    return render(request, 'projects.html')

def search(request):
    return render(request, 'search.html')

def sandbox(request):
    return render(request, 'sandbox.html')
