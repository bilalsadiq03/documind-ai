from fastapi import FastAPI

app = FastAPI(title="DocuMind API")

@app.get("/health")
def health_check():
    return {"status": "ok"}
