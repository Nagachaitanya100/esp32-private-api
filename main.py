
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Literal
import os

app = FastAPI(
    title="ESP32 Private API",
    version="1.0.0"
)

# Environment variables configured in Render
PUBLIC_API_TOKEN = os.environ["PUBLIC_API_TOKEN"]
DEVICE_TOKEN = os.environ["DEVICE_TOKEN"]

# In-memory command queue
pending_command = None


class Command(BaseModel):
    action: Literal["on", "off"]


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ESP32 Private API"
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ESP32 Private API"
    }


@app.get("/auth-test")
def auth_test(
    authorization: str | None = Header(default=None)
):
    if authorization != f"Bearer {PUBLIC_API_TOKEN}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    return {
        "status": "authenticated",
        "service": "ESP32 Private API"
    }


@app.post("/commands")
def receive_command(
    command: Command,
    authorization: str | None = Header(default=None)
):
    global pending_command

    if authorization != f"Bearer {PUBLIC_API_TOKEN}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    pending_command = command.action

    return {
        "success": True,
        "status": "queued",
        "command": pending_command
    }


@app.get("/device/next")
def get_command(
    authorization: str | None = Header(default=None)
):
    global pending_command

    if authorization != f"Bearer {DEVICE_TOKEN}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    command = pending_command
    pending_command = None

    return {
        "command": command
    }
