from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from prime_check import is_prime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Number(BaseModel):
    n: int


@app.get("/is_prime")
def get_is_prime(n: int):
    return {"n": n, "is_prime": is_prime(n)}


@app.post("/is_prime")
def post_is_prime(payload: Number):
    return {"n": payload.n, "is_prime": is_prime(payload.n)}
