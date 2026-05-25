from groq import AsyncGroq
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

_BASE_SYSTEM_PROMPT = """You are the AI assistant for {company_name}, an automotive repair and maintenance company.

STRICT RULES:
1. Only answer questions related to {company_name} — this includes services, pricing, locations, hours, bookings, appointments, blog posts, FAQs, car makes/models, and general automotive topics.
2. Use ONLY the company context provided below — never invent information.
3. If a question is completely unrelated to the company or automotive topics, politely decline: "I can only help with {company_name} related questions. Is there something specific I can help you with?"
4. Be concise, helpful, and professional.
5. ALWAYS include the relevant page link when answering:
   - Service questions → include the direct link to that service page
   - Appointment questions → include the appointment page link
   - Blog questions → include the direct link to that blog post
   - Contact/location questions → include the contact page link
6. For appointment/booking questions, explain what information is needed and provide the booking link.
7. When relevant, suggest booking an appointment or contacting the team and provide the link.

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
