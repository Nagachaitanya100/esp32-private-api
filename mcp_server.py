import os
import httpx
from fastmcp import FastMCP

mcp = FastMCP("ESP32 Cloud Light Controller")

WORKER_URL = "https://esp32-public-api.nagachaitanyathatipamula.workers.dev"

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

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
