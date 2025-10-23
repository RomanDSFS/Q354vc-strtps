from fastapi import APIRouter
import requests

router = APIRouter()

EXIT_SERVICE_URL = "http://localhost:8006/exit"

@router.post("/request")
async def request_exit(data: dict):
    response = requests.post(f"{EXIT_SERVICE_URL}/request", json=data)
    return response.json()

@router.get("/calculate")
async def calculate_roi():
    response = requests.get(f"{EXIT_SERVICE_URL}/calculate")
    return response.json()
