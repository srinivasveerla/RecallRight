from pydantic import BaseModel, Field

class Metadata(BaseModel):
    tags: list[str] = Field(description="A list of tags associated with the content")