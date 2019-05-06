from django.shortcuts import render

def index(request):
    return render(request, 'privacy_policy/privacy_policy')
