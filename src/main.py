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
    query_params = dict(request.query_params)
    token = query_params.pop("access_token", None)
    if not token:
        raise HTTPException(status_code=401, detail="No token")
    url = f"{CANVAS_BASE_URL}/{path}"
    params = {**query_params, "access_token": token}
    async with httpx.AsyncClient() as client:
        response = await client.request(
            request.method,
            url,
            params=params,
            content=await request.body(),
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
