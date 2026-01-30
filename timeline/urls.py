from django.urls import path
from . import views

app_name = "timeline"

urlpatterns = [
    # Write diary entry with AI emotion detection
    path("write/", views.write_diary, name="write"),
    
    # Dashboard with statistics and weekly trends
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # Emotion timeline calendar view
    path("emotion_timeline/", views.emotion_timeline, name="timeline"),
]