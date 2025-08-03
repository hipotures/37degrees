import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers={
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
        "Content-Type": "application/json"
    },
    json={
        "model": "sonar",
        "messages": [
            {
                "role": "user",
                "content": "Find adaptations of Alice in Wonderland, prioritize sources that come from different countries and written in English and Polish languages"
            }
        ],
        "max_tokens": 2000
    }
)

data = response.json()
print(json.dumps(data, indent=2, ensure_ascii=False))