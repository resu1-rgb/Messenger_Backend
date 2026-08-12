from fastapi import FastAPI
from authorization import router as authorization_router
from database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/me")
async def read_me():
    return {"message": "Hello, World!"}

app.include_router(authorization_router)
