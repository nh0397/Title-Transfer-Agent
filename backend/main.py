"""
Author: Naisarg H.
File: main.py
Description: This is the entry point of the backend server. It loads the
environment variables, starts the FastAPI application, sets up CORS so the
frontend can talk to it, and connects all the route modules together.
"""
import os
from dotenv import load_dotenv

# MUST be called before importing routers so env vars are available
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import agent, files

app = FastAPI(title="Harmony Title Transfer Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(agent.router)
app.include_router(files.router)


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Harmony Title Transfer Agent",
        "version": "1.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
