from pydantic import BaseModel

class JobCreate(BaseModel):
    repo_url: str

class JobResponse(BaseModel):
    id: str
    repo_url: str
    status: str
    progress: str
    result_url: str | None

    class Config:
        from_attributes = True