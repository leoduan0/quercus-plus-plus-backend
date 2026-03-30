from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException, Response
import os
import httpx

app = FastAPI()

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


@app.get("/")
async def root():
    return {"message": "Stop poking around."}


@app.get("/canvas/{path:path}")
async def canvas(path: str, request: Request):
    # Get Authorization header from incoming request
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401, detail="No Bearer token in Authorization header"
        )
    token = auth_header.split(" ", 1)[1]
    url = f"{CANVAS_BASE_URL}/{path}"
    # Forward all query params except access_token (if present)
    query_params = dict(request.query_params)
    query_params.pop("access_token", None)
    async with httpx.AsyncClient() as client:
        response = await client.request(
            request.method,
            url,
            params=query_params,
            content=await request.body(),
            headers={"Authorization": f"Bearer {token}"},
        )
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )


@app.post("/ai/{path:path}")
async def ai(path: str, request: Request):
    url = f"{AI_BASE_URL}/{path}"
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
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers),
    )
