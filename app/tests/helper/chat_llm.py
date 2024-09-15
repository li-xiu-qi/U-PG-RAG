import os

from openai import OpenAI, AsyncOpenAI

from utils import find_project_root_and_load_dotenv

find_project_root_and_load_dotenv("U-PG-RAG")
api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
client = OpenAI(api_key=api_key, base_url=base_url)

aclient = AsyncOpenAI(api_key=api_key, base_url=base_url)


def chat(messages, model_name="Qwen/Qwen2-7B-Instruct"):
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    message = [
        {
            "role": "user",
            "content": "你好"
        }
    ]
    print(chat(messages=message))
