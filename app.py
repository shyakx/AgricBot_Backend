from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import os

app = FastAPI(title="Agriculture Assistant API", description="API for agriculture-related questions based on FAQ dataset.")

# CORS configuration
origins = ["*"]  # Allow all origins; adjust in production to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File path for loading the FAQ dataset
FAQ_DATA_PATH = "faq_data.joblib"

# Load FAQ dataset
if os.path.exists(FAQ_DATA_PATH):
    faq_df = joblib.load(FAQ_DATA_PATH)
else:
    try:
        faq_df = pd.read_csv("Farming_FAQ_Assistant_Dataset.csv")
        joblib.dump(faq_df, FAQ_DATA_PATH)
    except Exception as e:
        raise Exception(f"Error loading FAQ dataset: {e}")

# Simple keyword-based topic detection for agriculture
agriculture_keywords = [
    "crop", "farm", "farming", "soil", "fertilizer", "pest", "pesticide", "irrigation",
    "plant", "seed", "harvest", "agriculture", "maize", "tomato", "potato", "rice",
    "wheat", "vegetable", "fruit", "orchard", "greenhouse", "compost", "manure",
    "nitrogen", "phosphorus", "potassium", "ph", "rainfall", "humidity", "temperature"
]

def is_agriculture_related(query):
    query = query.lower()
    return any(keyword in query for keyword in agriculture_keywords)

# Chatbot response function (FAQ lookup)
def generate_response(prompt):
    if not is_agriculture_related(prompt):
        return {"response": "🌱 Sorry, I'm designed to assist with agriculture-related questions only. Please ask about crops, farming, soil, or related topics!"}
    
    if faq_df is not None:
        prompt = prompt.lower().strip()
        for index, row in faq_df.iterrows():
            if prompt in row["Question"].lower():
                return {"response": row["Answer"]}
        return {"response": "🌱 I couldn't find a specific answer for your question. Please try rephrasing or check if it's agriculture-related!"}
    else:
        return {"response": "❌ FAQ dataset not loaded. Please ensure the dataset file is available."}

# Pydantic model for request body
class QueryRequest(BaseModel):
    query: str

# POST endpoint for agriculture questions
@app.post("/ask")
async def ask_question(request: QueryRequest):
    return generate_response(request.query)