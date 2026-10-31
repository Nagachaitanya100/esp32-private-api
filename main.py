
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Literal
import os

app = FastAPI(
    title="ESP32 Private API",
    version="1.1.0"
)

# Render environment variables
PUBLIC_API_TOKEN = os.environ["PUBLIC_API_TOKEN"]
DEVICE_TOKEN = os.environ["DEVICE_TOKEN"]

# In-memory command queue
pending_command = None


class Command(BaseModel):
    action: Literal["on", "off"]


def verify_public_token(authorization: str | None):
    if authorization != f"Bearer {PUBLIC_API_TOKEN}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


def verify_device_token(authorization: str | None):
    if authorization != f"Bearer {DEVICE_TOKEN}":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )


# --------------------------------
# Health endpoints
# --------------------------------

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


# --------------------------------
# Authentication test
# --------------------------------

@app.get("/auth-test")
def auth_test(
    authorization: str | None = Header(default=None)
):
    verify_public_token(authorization)

    return {
        "status": "authenticated",
        "service": "ESP32 Private API"
    }


# --------------------------------
# Queue a light command
# --------------------------------

@app.post("/commands")
def receive_command(
    command: Command,
    authorization: str | None = Header(default=None)
):
    global pending_command

    verify_public_token(authorization)

    pending_command = command.action

    return {
        "success": True,
        "status": "queued",
        "command": pending_command,
        "device_execution": "not_confirmed"
    }


# --------------------------------
# Safe queue status
# Does NOT consume the command
# --------------------------------

@app.get("/commands/status")
def command_status(
    authorization: str | None = Header(default=None)
):
    verify_public_token(authorization)

    return {
        "queue_status": (
            "pending" if pending_command is not None
            else "empty"
        ),
        "has_pending_command": pending_command is not None
    }


# --------------------------------
# ESP32 retrieves next command
# This consumes the pending command
# --------------------------------

@app.get("/device/next")
def get_command(
    authorization: str | None = Header(default=None)
):
    global pending_command

    verify_device_token(authorization)

    command = pending_command
    pending_command = None

    return {
        "command": command
    }
