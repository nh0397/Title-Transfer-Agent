"""
Author: Naisarg H.
File: main.py
Description: This is the primary entry point for the Title Transfer Agent backend. 
It initializes the FastAPI framework, configures cross-origin resource sharing (CORS) 
to allow the frontend to communicate with it, and wires up the modular routes 
for the AI agent and the file management system.
"""
import os
from dotenv import load_dotenv

# MUST be called before importing routers
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from routes import agent, files

load_dotenv()

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
        "version": "1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
