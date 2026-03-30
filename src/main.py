from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
import os
import httpx

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Stop poking around."}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CANVAS_BASE_URL = "https://q.utoronto.ca/api/v1"
AI_API_KEY = os.getenv("AI_API_KEY")
AI_BASE_URL = "https://api.openai.com/v1"


@app.api_route("/canvas/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def canvas(path: str, request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    url = f"{CANVAS_BASE_URL}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.request(
            request.method,
            url,
            headers={"Authorization": token},
            params=dict(request.query_params),
            content=await request.body(),
        )
    return response.json()


@app.post("/ai/{path:path}")
async def ai(path: str, request: Request):
    url = f"{AI_API_KEY}/{path}"
    async with httpx.AsyncClient() as client:
        response = await client.request(
            request.method,
            url,
            headers={
                "Authorization": f"Bearer {AI_API_KEY}",
                "Content-Type": "application/json",
            },
            params=dict(request.query_params),
            content=await request.body(),
        )
    return response.json()
