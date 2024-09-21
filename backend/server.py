from fastapi import FastAPI
from service.content_processor_service import ContentProcessorService
from models.request import RecallRequest, QnABySearchQuery

app = FastAPI()
content_service = ContentProcessorService()

@app.post("/data")
async def read_root(request: RecallRequest):
    # raw_body = await request.body()
    # print(raw_body.decode())
    content_service.upsert(request)
    return {"message": "Data received successfully"}

@app.get("/tags")
async def get_tags(count: int = 10):
    if(count > 100 or count < 0): count = 100
    return content_service.get_tags(count)


@app.post("/questionsBySearchQuery")
async def get_questions_by_search_query(request: QnABySearchQuery):
    questions = content_service.questions_by_search_query(request)
    return questions