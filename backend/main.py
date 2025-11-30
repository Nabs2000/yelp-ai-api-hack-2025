from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase_init import supabase
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


class UserLoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    firstName: str
    lastName: str
    email: str
    password: str


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handle user authentication


@app.post("/api/auth/login")
async def login(user_login: UserLoginRequest):
    try:
        print("Logging with email:", user_login.email)
        # Sign in user
        response = supabase.auth.sign_in_with_password(
            {
                "email": user_login.email,
                "password": user_login.password,
            }
        )
        if response.user and response.session:
            return {"user": response.user.model_dump(), "session": response.session.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/api/auth/register")
async def register_user(register_request: RegisterRequest):
    try:
        response = supabase.auth.sign_up(
            {
                "email": register_request.email,
                "password": register_request.password,
                "options": {
                    "email_redirect_to": "http://localhost:8080/",
                    "data": {
                        "first_name": register_request.firstName,
                        "last_name": register_request.lastName,
                    }
                },
            }
        )
        print("Response:", response)
        if response.user:
            return {"user": response.user.model_dump()}
    except Exception as e:
        print("Exception:", e)
        raise HTTPException(status_code=401, detail=str(e))
