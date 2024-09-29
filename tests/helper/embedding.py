import os

from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI

load_dotenv()

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
client = OpenAI(api_key=api_key, base_url=base_url)

aclient = AsyncOpenAI(api_key=api_key, base_url=base_url)


def embedding(chunk, model_name="BAAI/bge-large-zh-v1.5", ):
    response = client.embeddings.create(
        model=model_name,
        input=chunk,
    )
    output = [data.embedding for data in response.data][0]
    # total_tokens = response.usage.prompt_tokens
    return output


if __name__ == '__main__':
    chunk = "我爱北京天安门"
    response = embedding(chunk)
    print(response[0])
    print(len(response[0]))
