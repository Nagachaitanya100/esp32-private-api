
import os
import httpx
import uvicorn

from fastmcp import FastMCP
from main import app as rest_app

mcp = FastMCP("ESP32 Cloud Light Controller")

WORKER_URL = (
    "https://esp32-public-api.nagachaitanyathatipamula.workers.dev"
)


async def call_worker(path: str, method: str = "GET"):
    token = os.environ["GPT_API_TOKEN"]

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.request(
            method,
            f"{WORKER_URL}{path}",
            headers={"Authorization": f"Bearer {token}"}
        )

        return {
            "http_status": response.status_code,
            "response": response.text
        }


@mcp.tool()
async def check_connection():
    """Check Cloudflare-to-Render connectivity."""
    return await call_worker("/connection-test")


@mcp.tool()
async def check_authentication():
    """Check Cloudflare-to-Render authentication."""
    return await call_worker("/auth-test")


@mcp.tool()
async def turn_light_on():
    """Queue a command to turn the light on."""
    return await call_worker("/light/on", "POST")


@mcp.tool()
async def turn_light_off():
    """Queue a command to turn the light off."""
    return await call_worker("/light/off", "POST")


mcp_app = mcp.http_app(path="/mcp")


# REST endpoints handled by main.py
REST_PATHS = {
    "/",
    "/health",
    "/auth-test",
    "/commands",
    "/device/next",
    "/docs",
    "/openapi.json",
    "/redoc"
}


async def app(scope, receive, send):
    if scope["type"] == "http" and scope["path"] in REST_PATHS:
        await rest_app(scope, receive, send)
    else:
        await mcp_app(scope, receive, send)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000"))
    )
