import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not configured.")


client = Groq(api_key=api_key)


def ask_llm(prompt: str, conversation=None) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI-powered virtual assistant. "
                "Give clear, concise and accurate answers."
            )
        }
    ]

    if conversation:
        messages.extend(conversation)

    messages.append({
        "role": "user",
        "content": prompt
    })

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content