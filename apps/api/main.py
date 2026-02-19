from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import redis
import time
from sqlalchemy.exc import OperationalError

from db import engine, Base, SessionLocal
from models import Job
from schemas import JobCreate, JobResponse

app = FastAPI(title="DocuMind API")

@app.on_event("startup")
def on_startup():
    retries = 10
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            print("Database connected and tables created")
            break
        except OperationalError:
            retries -= 1
            print("Waiting for database to be ready...")
            time.sleep(3)
    else:
        raise RuntimeError("Could not connect to the database")

REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

QUEUE_NAME = "documind:jobs"

@app.post("/jobs", response_model=JobResponse)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = Job(repo_url=payload.repo_url, status="pending", progress="0%")
    db.add(job)
    db.commit()
    db.refresh(job)

    redis_client.lpush(QUEUE_NAME, job.id)

    return job

@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/health")
def health_check():
    return {"status": "ok"}
