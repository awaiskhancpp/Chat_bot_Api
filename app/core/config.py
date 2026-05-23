import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

FIXINMOTO_SYSTEM_PROMPT = "You are the AI assistant for FixinMoto, a motorcycle and car repair and maintenance service."