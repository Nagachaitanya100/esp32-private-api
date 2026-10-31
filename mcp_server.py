
import os
import httpx
import uvicorn
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


# Create the MCP HTTP application
mcp_app = mcp.http_app(path="/mcp")


# Add a separate health endpoint
async def app(scope, receive, send):
    if scope["type"] == "http" and scope["path"] == "/health":
        body = b'{"status":"ok"}'

        await send({
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode())
            ]
        })

        await send({
            "type": "http.response.body",
            "body": body
        })
    else:
        await mcp_app(scope, receive, send)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000"))
    )
