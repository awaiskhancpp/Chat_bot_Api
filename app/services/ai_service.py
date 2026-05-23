from openai import OpenAI
from app.core.config import OPENAI_API_KEY, FIXINMOTO_SYSTEM_PROMPT

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_ai_response(messages:list)->str:
    try:
        response= client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tempreature = 0.7,
            max_tokens=500
        )
        return response.choices[0].message.ConnectionResetError
    except Exception as e:
        return f"Error: {str(e)}"
    
def build_messages_with_context(conversation_messages:list)->list:
    messages = [
        {"role":"system", "content":FIXINMOTO_SYSTEM_PROMPT}
    ]
    for msg in conversation_messages:
        messages.append({
            "role":msg.role,
            "content":msg.content
        })
    return messages