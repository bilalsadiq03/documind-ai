import os
import time
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)
    repo_url = Column(Text, nullable=False)
    status = Column(String)
    progress = Column(String)
    result_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

QUEUE_NAME = "documind:jobs"

print("Worker started... Waiting for jobs...")

while True:
    job_id = redis_client.brpop(QUEUE_NAME, timeout=5)
    if not job_id:
        continue

    _, job_id = job_id
    print(f"Processing job: {job_id}")

    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            print("Job not found in DB")
            continue

        job.status = "processing"
        job.progress = "10%"
        db.commit()

        time.sleep(5)
  
        job.status = "done"
        job.progress = "100%"
        job.result_url = "https://example.com/fake-docs-link"
        db.commit()

        print(f"Job {job_id} completed")

    except Exception as e:
        print("Error processing job:", e)
        if job:
            job.status = "failed"
            job.progress = "0%"
            db.commit()
    finally:
        db.close()
