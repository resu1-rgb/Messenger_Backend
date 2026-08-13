from fastapi import FastAPI, Depends
from authorization import router as authorization_router, auth
from database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/me", dependencies=[Depends(auth.access_token_required)])
async def read_me():
    return {"message": "Hello, World!"}

app.include_router(authorization_router)
