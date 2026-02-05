"""
Honeypot Test API - FastAPI Application

This is a minimal, self-contained FastAPI application for testing the honeypot endpoint.
It handles authentication, validation, and basic scam detection scoring.
"""

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from .models import HoneypotTestRequest, HoneypotTestResponse, ErrorResponse
from .logic import calculate_scam_probability, should_trigger_handoff, generate_response_message
from .config import HONEYPOT_API_KEY, HONEYPOT_ENABLED, SCAM_THRESHOLD_FOR_HANDOFF, SERVICE_NAME

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Honeypot Test API",
    description="Test endpoint for honeypot prototype submission",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring"""
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "honeypot_enabled": HONEYPOT_ENABLED
    }


@app.post("/honeypot/test", response_model=HoneypotTestResponse)
async def honeypot_test(
    request: HoneypotTestRequest,
    x_api_key: Optional[str] = Header(None)
):
    """
    Honeypot Test Endpoint
    
    Accepts a conversation and returns scam probability with handoff decision.
    
    Args:
        request: HoneypotTestRequest with conversation data
        x_api_key: API key from X-API-Key header (required)
    
    Returns:
        HoneypotTestResponse with scam score and handoff decision
    
    Raises:
        HTTPException 401: Missing or invalid API key
        HTTPException 400: Invalid request format
    """
    
    # ===== AUTHENTICATION =====
    if not x_api_key:
        logger.warning("API request without X-API-Key header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "error": "Missing X-API-Key header"}
        )
    
    if x_api_key != HONEYPOT_API_KEY:
        logger.warning(f"API request with invalid key: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": "error", "error": "Invalid API key"}
        )
    
    # ===== VALIDATION =====
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"status": "error", "error": "Messages list cannot be empty"}
        )
    
    # ===== PROCESSING =====
    try:
        # Convert messages to list of dicts for scoring
        messages_list = [
            {"sender": msg.sender, "text": msg.text}
            for msg in request.messages
        ]
        
        # Calculate scam probability (stub scoring function)
        scam_probability = calculate_scam_probability(messages_list)
        
        # Determine handoff
        handoff = should_trigger_handoff(scam_probability, SCAM_THRESHOLD_FOR_HANDOFF)
        
        # Generate response message
        response_message = generate_response_message(scam_probability, handoff)
        
        logger.info(
            f"Processed conversation {request.conversation_id}: "
            f"score={scam_probability:.1f}, handoff={handoff}"
        )
        
        # ===== RESPONSE =====
        return HoneypotTestResponse(
            status="ok",
            honeypot_active=HONEYPOT_ENABLED,
            scam_probability=scam_probability,
            handoff=handoff,
            message=response_message
        )
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"status": "error", "error": "Internal server error"}
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler for HTTP errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": exc.detail if isinstance(exc.detail, str) else exc.detail.get("error", "Unknown error"),
            "code": exc.status_code
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
