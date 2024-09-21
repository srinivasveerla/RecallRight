from pydantic import BaseModel

class RecallRequest(BaseModel):
    source: str
    content: str 

class QnABySearchQuery(BaseModel):
    query: str 
    questions: int