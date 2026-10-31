from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="ESP32 Private API")

PUBLIC_API_TOKEN = os.environ["PUBLIC_API_TOKEN"]
DEVICE_TOKEN = os.environ["DEVICE_TOKEN"]

pending_command = None


class Command(BaseModel):
    action: str


@app.get("/")
def health():
    return {"status": "online", "service": "ESP32 Private API"}


@app.post("/commands")
def receive_command(
    command: Command,
    authorization: str = Header(None)
):
    global pending_command

    if authorization != f"Bearer {PUBLIC_API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if command.action not in ["on", "off"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    pending_command = command.action
    return {"success": True, "command": command.action}


@app.get("/device/next")
def get_command(authorization: str = Header(None)):
    global pending_command

    if authorization != f"Bearer {DEVICE_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    command = pending_command
    pending_command = None

    return {"command": command}
