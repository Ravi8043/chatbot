from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import InferenceClient

# Initialize FastAPI App
app = FastAPI()

# Enable CORS for frontend communication
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
    raise ValueError("ERROR: Required JSON files (config.json, responses.json) are missing.")

# API Key & Model Setup
DEEPSEEK_API_KEY = config.get("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("ERROR: DeepSeek API key is missing in config.json.")

# Initialize Hugging Face InferenceClient for DeepSeek-R1
client = InferenceClient(
    provider="together",
    api_key=DEEPSEEK_API_KEY
)

# Request Model for Queries
class QueryRequest(BaseModel):
    query: str


def get_account_balance(address: str):
    url = f"https://algoexplorerapi.io/v2/accounts/{address}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return {"address": address, "balance": data.get("amount", "Balance not found")}
    
    return {"error": "Failed to fetch account balance"}


def get_transaction_history(address: str, limit=5):
    url = f"https://algoexplorerapi.io/v2/accounts/{address}/transactions?limit={limit}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return {"address": address, "transactions": data.get("transactions", [])}
    
    return {"error": "Failed to fetch transactions"}


def get_block_info(block_num: int):
    url = f"https://algoexplorerapi.io/v2/blocks/{block_num}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    
    return {"error": "Failed to fetch block info"}

@app.get("/")
def read_root():
    return {"message": "Welcome to Algorand AI Chatbot!"}

@app.get("/config")
def get_config():
    return config

@app.post("/ask")
def ask_question(request: QueryRequest):
    """Return predefined responses from responses.json if available."""
    query = request.query.lower()
    response = responses.get(query, "Sorry, I don’t have an answer for that.")
    return {"query": query, "response": response}

@app.post("/chat")
def chat_with_bot(request: QueryRequest):
    """Use DeepSeek-R1 via Hugging Face InferenceClient for AI responses."""
    try:
        messages = [{"role": "user", "content": request.query}]

        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1",
            messages=messages,
            max_tokens=500,
            temperature = 0.7,
            top_p=0.9
        )

        ai_response = completion.choices[0].message if completion.choices else "No response received."
        return {"query": request.query, "response": ai_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")

@app.get("/account/{address}")
def account_balance(address: str):
    return get_account_balance(address)

@app.get("/transactions/{address}")
def transaction_history(address: str, limit: int = 5):
    return get_transaction_history(address, limit)

@app.get("/block/{block_num}")
def block_info(block_num: int):
    return get_block_info(block_num)