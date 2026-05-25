from groq import AsyncGroq
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

_BASE_SYSTEM_PROMPT = """You are the AI assistant for {company_name}, an automotive repair and maintenance company.

STRICT RULES:
1. Only answer questions about {company_name}'s services, pricing, locations, hours, bookings, and general automotive maintenance topics.
2. Use ONLY the company context provided below — never invent information.
3. If a question is unrelated to the company or automotive services, respond: "I can only help with {company_name} services and automotive questions. Is there something specific I can help you with?"
4. Be concise, helpful, and professional.
5. When relevant, suggest booking an appointment or contacting the team.

{context}
"""


async def generate_ai_response(messages: list[dict], company_name: str, context: str) -> str:
    system_prompt = _BASE_SYSTEM_PROMPT.format(
        company_name=company_name,
        context=context,
    )

    formatted = [{"role": "system", "content": system_prompt}] + messages

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=formatted,
        max_tokens=500,
        temperature=0.3,
    )

    return response.choices[0].message.content
