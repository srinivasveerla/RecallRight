from fastapi import FastAPI, Request
from service.content_processor_service import ContentProcessorService
from pydantic import BaseModel

class RecallRequest(BaseModel):
    source: str
    content: str 

app = FastAPI()
content_service = ContentProcessorService()

@app.post("/data")
async def read_root(request: RecallRequest):
    # raw_body = await request.body()
    # print(raw_body.decode())
    content_service.upsert(request)
    return {"message": "Data received successfully"}

@app.get("/tags")
async def get_tags(count = 10):
    tags = content_service.get_tags(count)
    return {"data": tags}