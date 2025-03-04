import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Load Groq API Key from Environment Variables
GROQ_API_KEY = "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"

class Query(BaseModel):
    question: str

events = [
    {"name": "Hackathon 2024", "date": "March 15, 2024", "organizer": "Tech Club"},
    {"name": "Cultural Fest", "date": "April 10, 2024", "organizer": "Arts Society"},
    {"name": "Sports Meet", "date": "May 5, 2024", "organizer": "Sports Council"}
]

# Your Info
creator_info = {
    "name": "John Doe",  # Change to your name
    "bio": "I am a software developer with expertise in AI and backend systems. I created this event assistant to help users get event details instantly."
}

@app.post("/ask")
async def ask_question(query: Query):
    url = "https://api.groq.com/openai/v1/chat/completions"  # Ensure this is the correct endpoint
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "system", "content": "You are an AI assistant for a college event management website. Answer queries about upcoming events."},
            {"role": "system", "content": f"Here are the upcoming events: {events}"},
            {"role": "system", "content": f"The creator of this AI is {creator_info['name']}. {creator_info['bio']}"},
            {"role": "user", "content": query.question}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        response_data = response.json()
        print("🔍 Groq API Full Response:", response_data)  # Log response for debugging

        if "choices" in response_data:
            return {"answer": response_data["choices"][0]["message"]["content"]}
        else:
            return {"error": "Groq API did not return 'choices'. Full response: " + str(response_data)}
    except Exception as e:
        return {"error": "Exception occurred: " + str(e)}
