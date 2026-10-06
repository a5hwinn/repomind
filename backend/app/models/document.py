from pydantic import BaseModel, Field

class Document(BaseModel):
    id: str
    content: str
    source_type: str
    source_url: str
    repo_name: str
    repo_url: str
    metadata: dict = Field(default_factory=dict)
