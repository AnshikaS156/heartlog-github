from django.shortcuts import render

from django.contrib.auth.models import User

# Create your views here.
def dashboard(request):
    user = User.objects.get(id = request.user.id)
    parameters = {
        'user':user
    }
    return render(request,"dashboard/dashboard.html",parameters)