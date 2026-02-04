"""
Main application entry point for the Scam Intelligence Engine.

This demonstrates how to:
1. Set up the FastAPI application
2. Integrate all modules (Rishi, Honeypot, Extraction, Recovery)
3. Configure the event bus for inter-agent communication
"""

import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import Rishi (Scam Detection) module
from rishi.api.detect import create_detect_router

# Import shared utilities
from shared.event_bus import get_event_bus, EventType

# Initialize FastAPI app
app = FastAPI(
    title="Scam Intelligence Engine",
    description="Multi-agent system for scam detection, honeypot engagement, and victim recovery",
    version="1.0.0",
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def setup_detectors():
    """Initialize detection service."""
    logger.info("Initializing Rishi (Scam Detection) module...")
    detect_router = create_detect_router()
    app.include_router(detect_router, tags=["Detection"])
    logger.info("✓ Scam detection endpoint available at POST /detect-scam")


def setup_event_subscribers():
    """
    Set up event bus subscribers for inter-agent communication.
    
    TODO: These would be implemented by respective agent modules
    """
    event_bus = get_event_bus()

    # Example: Honeypot agent subscribes to SCAM_CONFIRMED
    async def on_scam_confirmed(event):
        logger.info(f"[EVENT] SCAM_CONFIRMED: {event.conversation_id}")
        # TODO: Implement honeypot engagement logic
        # honeypot_agent.engage(event.payload)

    # Example: Extraction agent subscribes to conversation updates
    async def on_honeypot_engaged(event):
        logger.info(f"[EVENT] HONEYPOT_ENGAGED: {event.conversation_id}")
        # TODO: Implement extraction logic
        # extraction_agent.extract(event.payload)

    # Register subscribers (currently commented - would be done by respective agents)
    # event_bus.subscribe(EventType.SCAM_CONFIRMED, on_scam_confirmed)
    # event_bus.subscribe(EventType.HONEYPOT_ENGAGED, on_honeypot_engaged)

    logger.info("Event bus initialized (ready for inter-agent communication)")


@app.on_event("startup")
async def startup_event():
    """Initialize all modules on startup."""
    logger.info("=" * 60)
    logger.info("Starting Scam Intelligence Engine...")
    logger.info("=" * 60)

    setup_detectors()
    setup_event_subscribers()

    logger.info("=" * 60)
    logger.info("✓ All services initialized successfully")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Shutting down Scam Intelligence Engine...")


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with system status."""
    return {
        "service": "Scam Intelligence Engine",
        "status": "operational",
        "modules": [
            "scam_detection (Rishi) - ACTIVE",
            "honeypot (Saachi) - PENDING",
            "extraction (Samyak) - PENDING",
            "recovery (Shreyas) - PENDING",
        ],
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Scam Intelligence Engine",
    }


@app.get("/system/info", tags=["System"])
async def system_info():
    """Get system information."""
    return {
        "engine": "Scam Intelligence Engine",
        "version": "1.0.0",
        "modules": {
            "detection": "rishi (Person 1)",
            "honeypot": "saachi (Person 2) - TODO",
            "extraction": "samyak (Person 3) - TODO",
            "recovery": "shreyas (Person 4) - TODO",
        },
        "communication": "event_bus (in-memory, ready for Redis/RabbitMQ)",
    }


if __name__ == "__main__":
    import uvicorn

    # Run with: python main.py
    # Or: uvicorn main:app --reload
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
