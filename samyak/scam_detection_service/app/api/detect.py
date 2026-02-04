from fastapi import APIRouter, Header, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel

from app.models.baseline import analyze_message
from app.core.config import API_KEY

router = APIRouter(prefix="/detect", tags=["Scam Detection"])


class DetectRequest(BaseModel):
    message: str


class DetectResponse(BaseModel):
    risk_score: int
    decision: str
    features: dict


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@router.post("", response_model=DetectResponse, dependencies=[Depends(verify_api_key)])
def detect_scam(payload: DetectRequest):
    return analyze_message(payload.message)
