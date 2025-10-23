from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

SOURCING_SERVICE_URL = "http://127.0.0.1:8002"

@router.get("/profile/{investor_id}", tags=["Investors"])
async def proxy_get_investor_profile(investor_id: str):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{SOURCING_SERVICE_URL}/investors/profile/{investor_id}")
            resp.raise_for_status()
        except httpx.ReadTimeout:
            raise HTTPException(status_code=504, detail="Gateway Timeout: sourcing service did not respond")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"Proxy error: {str(e)}")
        return resp.json()
