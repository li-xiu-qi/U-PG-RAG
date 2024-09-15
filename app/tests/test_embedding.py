from app.serves.model_serves import AsyncEmbedding
from app.serves.model_serves import EmbeddingInput

embedding = AsyncEmbedding()
input_ = EmbeddingInput(input_content=["Hello, my name is"])


async def main():
    output = await embedding(input_)
    print(output)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
