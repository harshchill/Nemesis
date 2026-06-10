import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def getLLM():
    return ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=0.1,
        api_key=GROQ_API_KEY 
              )