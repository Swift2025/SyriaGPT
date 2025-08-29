from fastapi import FastAPI
from requests.authentication.registeration import router as auth_router
from requests.authentication.authentication import router as authentication_router 
from requests.authentication.forgot_password import router as forgot_password_router
from requests.authentication.two_factor import router as two_factor_router
from requests.questions import router as questions_router
from requests.answers import router as answers_router
from requests.intelligent_qa import router as intelligent_qa_router

app = FastAPI(
    title="Syria GPT API", 
    version="1.0.0",
    description="Intelligent Q&A system for Syria-related questions powered by Google Gemini AI"
)

app.include_router(auth_router)
app.include_router(authentication_router)
app.include_router(two_factor_router) 
app.include_router(forgot_password_router)
app.include_router(questions_router)
app.include_router(answers_router)
app.include_router(intelligent_qa_router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Syria GPT!", 
        "version": "1.0.0",
        "ai_provider": "Google Gemini",
        "features": ["Intelligent Q&A", "Vector Search", "Redis Caching", "Multilingual Support"]
    }

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}! Welcome to Syria GPT."}
