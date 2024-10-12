import diskcache
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fetch_web_resource import HTMLFetcher, ZhiPuWebSearch

app = FastAPI()


@app.post("/search")
async def search(query: str):
    # 获取搜索结果
    search_engine = ZhiPuWebSearch()
    results = search_engine.search(query)

    # 实例化 HTMLFetcher 进行批量抓取并完善结果
    cache = diskcache.Cache('./html_cache')
    fetcher = HTMLFetcher(cache=cache)

    enriched_results = fetcher.fetch_html_batch(results, timeout=5)

    async def streaming_data_generator():
        async for result in enriched_results:
            yield "data: " + result.model_dump_json() + "\n"

    return StreamingResponse(streaming_data_generator(), media_type="text/event-stream")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8888)
