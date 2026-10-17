
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq()

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Explain Python in two simple sentences."
        }
    ]
)

print(response.choices[0].message.content)
