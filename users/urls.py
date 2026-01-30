from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('wellnesstask/',views.wellness,name="wellness"),
    path('your-diary/', views.your_diary, name='your_diary'),
    path('guided-journaling/', views.guided_journaling, name='guided_journaling'),
]