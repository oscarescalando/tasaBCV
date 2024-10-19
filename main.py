from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"greeting": "SRapido - TechIA!", "message": "Welcome to tasaBCVAPI!"}