from groq import Groq

client = Groq(
    api_key="("Your api key...")"
)

def ask_ai(prompt):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are JARVIS, a helpful and intelligent personal AI assistant. Give clear and concise answers. in 1-2 lines."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content


