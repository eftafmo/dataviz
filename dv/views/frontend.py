from django.shortcuts import render_to_response


def home(request):
    return render_to_response('homepage.html')

def grants(request):
    return render_to_response('grants.html')

def partners(request):
    return render_to_response('partners.html')

def projects(request):
    return render_to_response('projects.html')

def search(request):
    return render_to_response('search.html')

def sandbox(request):
    return render_to_response('sandbox.html')
