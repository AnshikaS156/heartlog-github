from django.shortcuts import render
# Create your views here.
def home(request):
    return render (request,"home.html"),
def your_diary(request):
    return render (request,"home/yourdiary.html")
def guided_journaling(request):
    return render (request,"home/guided.html")

