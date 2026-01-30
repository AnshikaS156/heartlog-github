from django.shortcuts import render

from django.contrib.auth.decorators import login_required
import requests

api_key = "AIzaSyB8tg_h-W4i8xOycDuqR6jzSCBomWwKj6g"


def home(request):
    return render(request, 'home/index.html')
def wellness(request):
    return render(request,"home/wellness.html")
def your_diary(request):
    if request.method == "POST":
        query = request.POST.get("query")
        print("User Query:", query)  # DEBUG
        response = generate_response(query)
        print("AI Response:", response)  # DEBUG
        parameters = {
            'response': response
        }
        return render(request, 'home/yourdiary.html', parameters)
    return render (request,"home/yourdiary.html")

def generate_response(query):
    prompt = (
    "You are Dr. Aarav Mehta, the Chief Medical Officer of Call4Care. "
    "Tum ek professional doctor ho jo sirf patient ki emotional state ko samajhkar "
    "ek single word mein answer karta hai. "
    "Tumhara jawab sirf in 5 words me se ek hoga: Happy, Calm, Sad, Loved, Anxious. "
    "Koi explanation ya extra text nahi doge, sirf ek word output karna hai.\n\n"
    "User ka emotional journal entry hai: " + query
    )





    api = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    url = f"{api}?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if "candidates" in data:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"API Error: {data}"
    
    
def guided_journaling(request):
    return render (request,"home/guided.html")
