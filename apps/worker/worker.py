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
import traceback
from git import Repo
from packages.ai_core.gemini_client import generate_text
from packages.ai_core.repo_analyzer import collect_files, build_prompt
from packages.shared.cloudinary_client import upload_markdown

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
WORKDIR = "/tmp/documind_repos"

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

        # 1. clone repo
        repo_path = os.path.join(WORKDIR, job_id)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        
        Repo.clone_from(job.repo_url, repo_path)
        job.progress = "30%"
        db.commit()

        # 2. Collect files
        files = collect_files(repo_path)
        job.progress = "50%"
        db.commit()

        # 3. Build Prompt
        prompt = build_prompt(files)

        # 4. Call Gemini
        docs = generate_text(prompt)
        job.progress = "80%"
        db.commit()

        # 5. Upload to Cloudinary
        filename = f"documind/{job_id}/README.md"
        url = upload_markdown(docs, filename)

        # 6. Save result
        job.status = "done"
        job.progress = "100%"
        job.result_url = url
        db.commit()
        
        print(f"Job {job_id} completed")

    except Exception as e:
        print("Error processing job:", e)
        traceback.print_exc()
        if job:
            job.status = "failed"
            job.progress = "0%"
            db.commit()
    finally:
        db.close()
