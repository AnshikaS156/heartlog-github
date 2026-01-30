from django.db import models
from django.contrib.auth.models import User

class EmotionEntry(models.Model):

    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('calm', 'Calm'),
        ('anxious', 'Anxious'),
        ('neutral', 'Neutral'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    diary_text = models.TextField()

    emotion = models.CharField(
        max_length=20,
        choices=EMOTION_CHOICES
    )

    confidence = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.emotion}"


# Create your models here.
