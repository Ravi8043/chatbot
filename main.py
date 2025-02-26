from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import requests
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load Config & Responses
try:
    with open("config.json", "r") as f:
        config = json.load(f)
    with open("responses.json", "r") as f:
        responses = json.load(f)
except FileNotFoundError:
    raise ValueError("❌ ERROR: Required JSON files (config.json, responses.json) are missing.")

# API Key
DEEPSEEK_API_KEY = config.get("DEEPSEEK_API_KEY")  # Ensure correct key name
if not DEEPSEEK_API_KEY:
    raise ValueError("❌ ERROR: DeepSeek API key is missing in config.json.")

LLAMA_ENDPOINT = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B"

# Request Model for Queries
class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Algorand AI Chatbot!"}

@app.get("/config")
def get_config():
    return config

@app.post("/ask")
def ask_question(request: QueryRequest):
    query = request.query.lower()
    response = responses.get(query, "Sorry, I don’t have an answer for that.")
    return {"query": query, "response": response}

@app.post("/chat")
def chat_with_bot(request: QueryRequest):
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    payload = {"inputs": request.query}

    try:
        response = requests.post(LLAMA_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")

