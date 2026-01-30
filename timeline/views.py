from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils.timezone import now, localdate
from datetime import timedelta, date
from calendar import monthrange, day_name
import json

from .models import EmotionEntry
from .ai import detect_emotion


# Emotion emoji mapping
EMOTION_EMOJIS = {
    'happy': '😊',
    'sad': '😢',
    'anxious': '😰',
    'calm': '😌',
    'angry': '😤',
    'grateful': '🤗',
    'neutral': '😐'
}


@login_required
def dashboard(request):
    """
    Dashboard view with statistics and weekly trends
    """
    user = request.user
    
    # Get all entries
    entries = EmotionEntry.objects.filter(user=user)
    total_entries = entries.count()
    
    # Emotion distribution
    emotion_counts = (
        entries
        .values("emotion")
        .annotate(count=Count("emotion"))
        .order_by("-count")
    )
    
    # Add emojis to emotion counts
    emotion_counts_with_emoji = []
    for item in emotion_counts:
        emotion_counts_with_emoji.append({
            'emotion': item['emotion'],
            'count': item['count'],
            'emoji': EMOTION_EMOJIS.get(item['emotion'], '😐')
        })
    
    # Calculate dominant emotion
    dominant_emotion = None
    dominant_emotion_emoji = None
    if emotion_counts_with_emoji:
        dominant_emotion = emotion_counts_with_emoji[0]['emotion']
        dominant_emotion_emoji = emotion_counts_with_emoji[0]['emoji']
    
    # Last 7 days trend
    last_7_days = now() - timedelta(days=7)
    weekly_entries = entries.filter(created_at__gte=last_7_days).order_by("created_at")
    
    # Group by day of week
    weekly_data = {day: [] for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    for entry in weekly_entries:
        day_index = entry.created_at.weekday()
        day = day_names[day_index]
        weekly_data[day].append(entry.emotion)
    
    # Calculate streak
    streak = calculate_streak(user)
    
    # Calculate average mood score
    emotion_scores = {
        'happy': 5,
        'grateful': 4.5,
        'calm': 4,
        'neutral': 3,
        'anxious': 2,
        'sad': 1.5,
        'angry': 1
    }
    
    if total_entries > 0:
        total_score = sum(emotion_scores.get(e.emotion, 3) for e in entries)
        average_mood_score = round(total_score / total_entries, 1)
    else:
        average_mood_score = 0.0
    
    context = {
        "emotion_counts": emotion_counts_with_emoji,
        "weekly_data": weekly_data,
        "weekly_data_json": json.dumps(weekly_data),
        "total_entries": total_entries,
        "streak": streak,
        "dominant_emotion": dominant_emotion,
        "dominant_emotion_emoji": dominant_emotion_emoji,
        "average_mood_score": average_mood_score,
        "today": localdate(),
    }
    
    return render(request, "timeline/dashboard.html", context)


@login_required
def emotion_timeline(request):
    """
    Calendar view of emotional timeline
    """
    user = request.user
    
    # Get month and year from request or use current
    today = localdate()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    # Handle form submission for new emotion entry
    if request.method == "POST":
        selected_date = request.POST.get('date')
        emotion = request.POST.get('emotion')
        note = request.POST.get('note', '')
        
        if selected_date and emotion:
            # Parse the date
            entry_date = date.fromisoformat(selected_date)
            
            # Check if entry already exists for this date
            existing_entry = EmotionEntry.objects.filter(
                user=user,
                created_at__date=entry_date
            ).first()
            
            if existing_entry:
                # Update existing entry
                existing_entry.emotion = emotion
                existing_entry.diary_text = note
                existing_entry.save()
            else:
                # Create new entry
                EmotionEntry.objects.create(
                    user=user,
                    emotion=emotion,
                    diary_text=note,
                    created_at=entry_date
                )
        
        return redirect('timeline:timeline')
    
    # Get entries for the current month
    entries = EmotionEntry.objects.filter(
        user=user,
        created_at__year=year,
        created_at__month=month
    )
    
    # Create emotion map
    emotion_map = {}
    for entry in entries:
        emotion_map[entry.created_at.date()] = {
            'emotion': entry.emotion,
            'emoji': EMOTION_EMOJIS.get(entry.emotion, '😐'),
            'note': entry.diary_text
        }
    
    # Calculate calendar days
    first_day_weekday = date(year, month, 1).weekday()
    first_day_weekday = (first_day_weekday + 1) % 7  # Convert to Sunday = 0
    
    days_in_month = monthrange(year, month)[1]
    
    # Previous month info
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    days_in_prev_month = monthrange(prev_year, prev_month)[1]
    
    # Next month info
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Build calendar days
    calendar_days = []
    
    # Previous month days
    for i in range(first_day_weekday - 1, -1, -1):
        day_num = days_in_prev_month - i
        calendar_days.append({
            'day': day_num,
            'date': date(prev_year, prev_month, day_num).isoformat(),
            'is_other_month': True,
            'is_today': False,
            'emotion': None,
            'emotion_emoji': None,
            'note': None
        })
    
    # Current month days
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        is_today = current_date == today
        
        emotion_data = emotion_map.get(current_date)
        
        calendar_days.append({
            'day': day,
            'date': current_date.isoformat(),
            'is_other_month': False,
            'is_today': is_today,
            'emotion': emotion_data['emotion'] if emotion_data else None,
            'emotion_emoji': emotion_data['emoji'] if emotion_data else None,
            'note': emotion_data['note'] if emotion_data else None
        })
    
    # Next month days to fill the calendar
    remaining_days = 42 - len(calendar_days)  # 6 weeks * 7 days
    for day in range(1, remaining_days + 1):
        calendar_days.append({
            'day': day,
            'date': date(next_year, next_month, day).isoformat(),
            'is_other_month': True,
            'is_today': False,
            'emotion': None,
            'emotion_emoji': None,
            'note': None
        })
    
    # Calculate statistics
    total_entries = entries.count()
    
    emotion_counts = {}
    for emotion in ['happy', 'sad', 'anxious', 'calm', 'angry', 'grateful']:
        emotion_counts[emotion] = entries.filter(emotion=emotion).count()
    
    # Calculate dominant emotion
    dominant_emotion = '😊'
    if emotion_counts:
        max_emotion = max(emotion_counts, key=emotion_counts.get)
        dominant_emotion = EMOTION_EMOJIS.get(max_emotion, '😊')
    
    # Calculate streak
    streak = calculate_streak(user)
    
    # Month name
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    context = {
        'calendar_days': calendar_days,
        'month': month_names[month],
        'year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'emotion_counts': emotion_counts,
        'total_entries': total_entries,
        'dominant_emotion': dominant_emotion,
        'streak': streak,
    }
    
    return render(request, 'timeline/emotion_timeline.html', context)


@login_required
def write_diary(request):
    """
    Diary writing view with AI emotion detection
    """
    if request.method == "POST":
        diary_text = request.POST.get("diary")
        
        # Detect emotion using AI
        emotion, confidence = detect_emotion(diary_text)
        
        # Create entry
        EmotionEntry.objects.create(
            user=request.user,
            diary_text=diary_text,
            emotion=emotion,
            confidence=confidence
        )
        
        return redirect("timeline:timeline")
    
    return render(request, "timeline/diary.html")


def calculate_streak(user):
    """
    Calculate the current streak of consecutive days with entries
    """
    today = localdate()
    streak = 0
    
    for i in range(365):  # Check up to 1 year back
        check_date = today - timedelta(days=i)
        has_entry = EmotionEntry.objects.filter(
            user=user,
            created_at__date=check_date
        ).exists()
        
        if has_entry:
            streak += 1
        else:
            break
    
    return streak


def generate_report(entries):
    """
    Generate emotional analysis report from entries
    """
    total = entries.count()
    
    if total == 0:
        return {}
    
    emotion_score = {
        "happy": 2,
        "calm": 1,
        "neutral": 0,
        "sad": -1,
        "anxious": -2,
        "angry": -2,
    }
    
    score = 0
    emotion_map = {}
    
    for e in entries:
        score += emotion_score.get(e.emotion, 0)
        emotion_map[e.emotion] = emotion_map.get(e.emotion, 0) + 1
    
    avg_score = round(score / total, 2)
    
    dominant = max(emotion_map, key=emotion_map.get) if emotion_map else "neutral"
    
    return {
        "dominant_emotion": dominant,
        "average_mood_score": avg_score,
        "emotion_breakdown": emotion_map,
    }