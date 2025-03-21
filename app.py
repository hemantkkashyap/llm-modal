import os
import requests
import re
from fastapi import FastAPI
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Load Groq API Key from Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
GITHUB_USERNAME = "hemantkkashyap"
GITHUB_API_URL = "https://api.github.com/user/repos"

SMTP_SERVER = "smtp.gmail.com"  # Change this if using a different email provider
SMTP_PORT = 587
EMAIL_SENDER = "kashyaphemant2004@gmail.com"  # Change to your email
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

class Query(BaseModel):
    question: str
    type: str


class EmailData(BaseModel):
    to_email: str
    subject: str
    body: str

events = [
    {"name": "Hackathon 2024", "date": "March 15, 2024", "organizer": "Tech Club"},
    {"name": "Cultural Fest", "date": "April 10, 2024", "organizer": "Arts Society"},
    {"name": "Sports Meet", "date": "May 5, 2024", "organizer": "Sports Council"}
]

# Your Info
creator_info = {
    "name": "Hemant",  # Your name
    "bio": "I am a Full Stack Software Engineer intern at Zangoh, currently learning Python for Data Science, AI & Development. My goal is to continuously improve my skills and contribute to projects that help humanity and solve significant problems. I aim to gain additional skills by taking related classes and engaging in professional associations. I also have experience working with React, Next.js, Firebase Authentication, and PostgreSQL."
}

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI app!"}

def send_email(to_email: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()

        return {"message": "Email sent successfully!"}
    except Exception as e:
        return {"error": f"Failed to send email: {str(e)}"}

def create_github_repo(repo_name: str, description: str = "A new repository", is_private: bool = False):
    headers = {
        "Authorization": f"Bearer {GITHUB_API_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": repo_name,
        "description": description,
        "private": is_private
    }
    
    response = requests.post(GITHUB_API_URL, headers=headers, json=data)
    
    if response.status_code == 201:
        return response.json()  # Repository created successfully
    else:
        return response.json()  # Error message from GitHub API
# GitHub repository deletion function
def delete_github_repo(repo_name: str):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
    headers = {
        "Authorization": f"Bearer {GITHUB_API_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.delete(url, headers=headers)
    
    if response.status_code == 204:
        return {"message": f"Repository '{repo_name}' deleted successfully!"}
    else:
        return {"error": f"Error deleting repository: {response.json()}"}

# Endpoint to handle questions and create or delete repos
@app.post("/github")
async def handle_github_action(query: Query):
    # Handle 'create' action
    if "create" in query.question.lower() and ("github repo" in query.question.lower() or "repository" in query.question.lower()):
        # Example input: "Create a GitHub repo named temp" or "create github repository test-repo"
        pattern = r"(?:named|name|called)\s+([a-zA-Z0-9-_]+)"
        match = re.search(pattern, query.question, re.IGNORECASE)

        if match:
            repo_name = match.group(1)
        else:
            # Fallback: Try extracting the last word assuming it's the repo name
            words = query.question.strip().split()
            repo_name = words[-1]  # risky but works if format is known

        description = "A repository created through API."
        is_private = False
        result = create_github_repo(repo_name, description, is_private)

        if "name" in result:
            return {"message": f"✅ GitHub repository '{repo_name}' created successfully!", "repo": result}
        else:
            return {"error": "❌ Error creating repository", "details": result}
    
    # Handle 'delete' action
    elif "delete" in query.question.lower() and "github repo" in query.question.lower():
        # Extract repo name from the query (regex to capture the repo name)
        pattern = r"(?:delete|remove)\s+(?:github\s+)?(?:repo|repository)\s+([a-zA-Z0-9-_]+)"
        match = re.search(pattern, query.question, re.IGNORECASE)

        if match:
            repo_name = match.group(1)
        else:
            # Fallback: Try extracting the last word assuming it's the repo name
            words = query.question.strip().split()
            repo_name = words[-1]  # risky but works if format is known

        result = delete_github_repo(repo_name)

        if result:
            return {"message": f"✅ GitHub repository '{repo_name}' deleted successfully!"}
        else:
            return {"error": "❌ Error deleting repository", "details": result}
    
    return {"error": "❌ No valid GitHub instruction found."}

@app.post("/linkedin/connect")
async def linkedin_connect(query: Query):
    if "connect with" in query.question.lower():
        username = "user"  # Extract username dynamically
        # result = connect_with_linkedin_user(username)
        return {"message": f"Successfully connected with {username} on LinkedIn!"}
    return {"error": "No valid LinkedIn connection instruction found."}

@app.post("/chat/ask")
async def chat_ask(query: Query):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": f"The creator of this AI is {creator_info['name']}. {creator_info['bio']}"},
            {"role": "user", "content": query.question}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    response = requests.post(url, json=payload, headers=headers)

    try:
        response_data = response.json()
        print("🔍 Groq API Full Response:", response_data)  # For Debugging

        if "choices" in response_data:
            return {"answer": response_data["choices"][0]["message"]["content"]}
        else:
            return {"error": "Groq API did not return 'choices'. Full response: " + str(response_data)}
    except Exception as e:
        return {"error": "Exception occurred: " + str(e)}


@app.post("/send-email")
async def send_email_endpoint(email_data: EmailData):
    return send_email(email_data.to_email, email_data.subject, email_data.body)