import httpx
import os
from dotenv import load_dotenv

load_dotenv()

CMS_URL = os.getenv("PAYLOAD_CMS_URL", "").rstrip("/")
CMS_API_KEY = os.getenv("PAYLOAD_API_KEY", "")


def _headers() -> dict:
    if CMS_API_KEY:
        return {"Authorization": f"users API-Key {CMS_API_KEY}"}
    return {}


async def _get(endpoint: str, params: dict | None = None) -> dict:
    url = f"{CMS_URL}/api/{endpoint}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=_headers(), params=params or {})
        resp.raise_for_status()
        return resp.json()


async def get_settings() -> dict:
    try:
        return await _get("globals/settings")
    except Exception:
        return {}


async def get_services() -> list[dict]:
    try:
        data = await _get("services", {"limit": 100, "depth": 0})
        return data.get("docs", [])
    except Exception:
        return []


async def get_main_services() -> list[dict]:
    try:
        data = await _get("main-service", {"limit": 50, "depth": 0})
        return data.get("docs", [])
    except Exception:
        return []


async def get_service_packages() -> list[dict]:
    try:
        data = await _get("service-package", {"limit": 100, "depth": 1})
        return data.get("docs", [])
    except Exception:
        return []


async def get_faqs() -> list[dict]:
    try:
        data = await _get("faq", {"limit": 50})
        return data.get("docs", [])
    except Exception:
        return []


async def get_locations() -> list[dict]:
    try:
        data = await _get("location", {"limit": 50})
        return data.get("docs", [])
    except Exception:
        return []
