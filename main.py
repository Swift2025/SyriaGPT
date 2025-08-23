from fastapi import FastAPI
from requests.authentication.registeration import router as auth_router

app = FastAPI(title="Syria GPT API", version="1.0.0")

app.include_router(auth_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Syria GPT!", "version": "1.0.0"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}! Welcome to Syria GPT."}
