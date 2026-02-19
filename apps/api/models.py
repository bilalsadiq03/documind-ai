import uuid
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_url = Column(Text, nullable=False)
    status = Column(String, default="pending")
    progress = Column(String, default="0%")
    result_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())