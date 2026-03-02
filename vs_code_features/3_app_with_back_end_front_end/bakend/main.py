from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from prime_checker import is_prime

app = FastAPI(title="Prime Validator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|\d+\.\d+\.\d+\.\d+):5173",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PrimeRequest(BaseModel):
    number: int = Field(..., ge=0, le=10**12, description="Whole number between 0 and 1e12")


class PrimeResponse(BaseModel):
    number: int
    is_prime: bool
    message: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/prime", response_model=PrimeResponse)
def validate_prime(payload: PrimeRequest) -> PrimeResponse:
    result = is_prime(payload.number)
    message = "Yes, It's prime" if result else "No, It's not prime"
    return PrimeResponse(number=payload.number, is_prime=result, message=message)
