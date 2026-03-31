from openai import OpenAI
from config import AI_BASE_URL,AI_API_KEY
default_llm = OpenAI(
    api_key=AI_API_KEY,
    base_url=AI_BASE_URL, 
)
    
