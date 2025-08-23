from fastapi import FastAPI

app = FastAPI(title="Syria GPT API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Syria GPT!"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}! Welcome to Syria GPT."}
