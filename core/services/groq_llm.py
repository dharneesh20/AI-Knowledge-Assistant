from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def groq_answer(query: str, context: str) -> str:
    prompt = f"""
You are an AI assistant. Answer the user's question using ONLY the provided document context.

If the answer is not in the context, reply:
Not found in the uploaded documents.

DOCUMENT CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
""".strip()

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=700,
    )

    return res.choices[0].message.content.strip()
