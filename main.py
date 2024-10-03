from init_app import init_app
from logging_config import setup_logging

# import sys
# sys.setrecursionlimit(15000)  # 将递归深度限制增加到15000

init_app()
setup_logging()
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.apis import (partition_router,
                      admin_router,
                      user_router,
                      file_router,
                      document_router,
                      rag_cache_router,
                      conversation_router,
                      response_record_router,
                      chunk_router,
                      image_router,
                      rag_router)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rag_router)
app.include_router(partition_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(file_router)
app.include_router(document_router)
app.include_router(rag_cache_router)
app.include_router(conversation_router)
app.include_router(response_record_router)
app.include_router(chunk_router)
app.include_router(image_router)


@app.get("/", response_class=HTMLResponse)
def read_root():
    return "Hello World"


@app.get("/robots.txt")
def get_robots_txt():
    return FileResponse(Path("app/templates/robots.txt"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
