from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def register(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        return redirect('fitbit-login')
    else:
        # Return an 'invalid login' error message.
        return render(request, 'tracker-register')