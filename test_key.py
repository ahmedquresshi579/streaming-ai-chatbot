import os
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")
print("Key loaded:", repr(api_key[:8]) + "..." if api_key else "NONE — .env not loading")

if not api_key:
    exit()

client = Mistral(api_key=api_key)

response = client.chat.complete(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": "Say 'API key works' and nothing else."}]
)

print("Full response object:", response)
print("Content:", response.choices[0].message.content)