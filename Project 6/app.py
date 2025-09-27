import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],  # this reads the environment variable
)

completion = client.chat.completions.create(
    model="moonshotai/Kimi-K2-Instruct-0905",
    messages=[
        {
            "role": "user",
            "content": "Write a dialogue between two characters meeting for the first time."
        }
    ],
)

print(completion.choices[0].message)
