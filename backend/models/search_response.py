from pydantic import BaseModel, Field

class Question(BaseModel):
    question: str = Field(description="Question to be asked from the content")
    options: list[str] = Field(description="A list of options associated with the questions. One of them is the correct answer")
    correct_option: str = Field(description="The correct answer from options")
    explanation: str = Field(description="Explanation why correct_option is correct")

class SearchResponse(BaseModel):
    questions: list[Question] = Field(description="list of questions")