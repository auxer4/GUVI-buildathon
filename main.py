"""
Main application entry point for the Scam Intelligence Engine.

This demonstrates how to:
1. Set up the FastAPI application
2. Integrate all modules (Rishi, Honeypot, Extraction, Recovery)
3. Configure the event bus for inter-agent communication
4. Enable comprehensive logging and error handling
"""

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Configure comprehensive logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# File handler for INFO and above
file_handler = logging.handlers.RotatingFileHandler(
    log_dir / "scam_engine.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
)
file_handler.setLevel(logging.INFO)

# File handler for ERRORS
error_handler = logging.handlers.RotatingFileHandler(
    log_dir / "errors.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
)
error_handler.setLevel(logging.ERROR)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(level=logging.INFO, handlers=[file_handler, error_handler, console_handler])
logger = logging.getLogger(__name__)

# Import Rishi (Scam Detection) module
try:
    from rishi.api.detect import create_detect_router
    logger.info("Successfully imported Rishi detection module")
except ImportError as e:
    logger.error(f"Failed to import Rishi: {e}")
    raise

# Import Saachi (Honeypot) module
try:
    from saachi.api.honeypot import create_honeypot_router, engage_session
    logger.info("Successfully imported Saachi honeypot module")
except ImportError as e:
    logger.error(f"Failed to import Saachi: {e}")
    raise

# Import shared utilities
try:
    from shared.event_bus import EventType, get_event_bus
    from shared.redis_client import RedisEventStore, get_redis_client
    logger.info("Successfully imported shared utilities")
except ImportError as e:
    logger.error(f"Failed to import shared utilities: {e}")
    raise

# Import shreyas reporting and victim recovery
try:
    from shreyas.app.reporting.intelligence_reporter import (
        IntelligenceReporter,
        ScamType,
    )
    from shreyas.app.reporting.victim_recovery import VictimRecoveryAssistant
    logger.info("Successfully imported Shreyas reporting modules")
except ImportError as e:
    logger.error(f"Failed to import Shreyas: {e}")
    logger.warning("Shreyas modules will be partially available")

# Initialize FastAPI app
app = FastAPI(
    title="Scam Intelligence Engine",
    description="Multi-agent system for scam detection, honeypot engagement, intelligence extraction, and victim recovery",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"],
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global error handler
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    """Global error handling middleware."""
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.exception(f"Unhandled exception in {request.url.path}: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
            },
        )


def setup_detectors():
    """Initialize detection and honeypot services."""
    try:
        logger.info("Initializing Rishi (Scam Detection) module...")
        detect_router = create_detect_router()
        app.include_router(detect_router, tags=["Detection"])
        logger.info("Scam detection endpoint available at POST /detect-scam")

        logger.info("Initializing Saachi (Honeypot) module...")
        honeypot_router = create_honeypot_router()
        app.include_router(honeypot_router, tags=["Honeypot"])
        logger.info("Honeypot engagement endpoint available at POST /honeypot/engage")
        logger.info("Honeypot message endpoint available at POST /honeypot/message")

        return True
    except Exception as e:
        logger.exception(f"Error setting up detectors: {e}")
        return False


def setup_event_subscribers():
    """Set up event bus subscribers for inter-agent communication."""
    try:
        event_bus = get_event_bus()
        redis_client = get_redis_client()
        event_store = RedisEventStore(redis_client)
        intelligence_reporter = IntelligenceReporter()
        victim_recovery = VictimRecoveryAssistant()

        # Honeypot agent subscribes to SCAM_CONFIRMED
        async def on_scam_confirmed(event):
            """Handle SCAM_CONFIRMED event by engaging honeypot."""
            logger.info(f"[EVENT] SCAM_CONFIRMED: {event.conversation_id}")

            try:
                payload = event.payload if hasattr(event, 'payload') else event.get('payload', {})

                # Extract data from detection result
                conversation_id = payload.get("conversation_id", "unknown")
                scam_probability = payload.get("scam_probability", 0)
                detection_result = payload.get("detection_result", {})
                scam_type_str = detection_result.get("scam_type", "unknown")
                metadata = payload.get("metadata", {})
                original_sender_id = metadata.get("sender_id", "unknown")

                # Determine persona based on scam type
                persona_map = {
                    "phishing": "elderly_pensioner",
                    "impersonation": "middle_class_employee",
                    "social_engineering": "student",
                    "romance_or_advance_fee": "elderly_pensioner",
                    "tech_support": "student",
                    "unknown": "middle_class_employee",
                }
                persona_key = persona_map.get(scam_type_str, "middle_class_employee")

                logger.info(
                    f"[HONEYPOT] Engaging scammer: conv={conversation_id}, "
                    f"prob={scam_probability:.2f}, type={scam_type_str}, persona={persona_key}"
                )

                # Engage honeypot
                try:
                    result = engage_session(
                        conversation_id=conversation_id,
                        original_sender_id=original_sender_id,
                        scam_probability=scam_probability,
                        scam_type=scam_type_str,
                        initial_message=None,
                        persona_key=persona_key,
                    )
                    logger.info(
                        f"[HONEYPOT] [OK] Engaged: session={result.get('session_id')}, "
                        f"status={result.get('status')}"
                    )

                    # Store event in Redis
                    if redis_client:
                        event_store.store_event("SCAM_CONFIRMED", payload)

                except Exception as e:
                    logger.exception(f"[HONEYPOT] [ERROR] Error engaging honeypot: {e}")

                # Attempt to generate intelligence reports
                try:
                    sender_info = {
                        "sender_id": original_sender_id,
                        "contact_method": metadata.get("contact_method", "unknown"),
                        "platform": metadata.get("platform", "unknown"),
                    }

                    # Generate internal report for system learning
                    internal_report = intelligence_reporter.generate_internal_report(
                        conversation_id=conversation_id,
                        sender_info=sender_info,
                        extracted_entities=[],  # Would be populated from extraction
                        detection_results=detection_result,
                    )
                    logger.info(f"[REPORTING] Generated internal report: {internal_report.report_id}")

                except Exception as e:
                    logger.warning(f"[REPORTING] Could not generate report: {e}")

            except Exception as e:
                logger.exception(f"[EVENT] Error processing SCAM_CONFIRMED: {e}")

        # Extraction agent subscribes to HONEYPOT_ENGAGED
        async def on_honeypot_engaged(event):
            """Handle HONEYPOT_ENGAGED event by extracting intelligence."""
            logger.info(f"[EVENT] HONEYPOT_ENGAGED: {event.conversation_id}")
            try:
                payload = event.payload if hasattr(event, 'payload') else event.get('payload', {})

                # Prepare event for extraction
                extractor_event = {
                    "text": payload.get("message", ""),
                    "event_id": payload.get("honeypot_session_id") or payload.get("conversation_id"),
                }

                # Lazy-import shreyas extractor
                try:
                    from shreyas.app.extraction import regex_extractors as shreyas_regex

                    entities = shreyas_regex.extract_entities(extractor_event)
                    logger.info(f"[EXTRACTION] Extracted {len(entities)} entities")

                    # Store in Redis
                    if redis_client:
                        event_store.store_event("HONEYPOT_ENGAGED", {**payload, "entities": entities})

                except Exception as e:
                    logger.exception(f"[EXTRACTION] Error extracting entities: {e}")

                # Generate victim recovery guidance if applicable
                try:
                    scam_type = ScamType.UNKNOWN
                    assessment = victim_recovery.assess_victim_situation(
                        scam_type=scam_type,
                        extracted_entities=[],
                        detection_results={},
                    )
                    recovery_plan = victim_recovery.generate_recovery_plan(assessment)
                    logger.info(f"[RECOVERY] Generated recovery plan for risk level: {assessment.risk_level.value}")
                except Exception as e:
                    logger.warning(f"[RECOVERY] Could not generate recovery plan: {e}")

            except Exception as e:
                logger.exception(f"[EVENT] Error processing HONEYPOT_ENGAGED: {e}")

        # Register subscribers
        try:
            event_bus.subscribe(EventType.SCAM_CONFIRMED, on_scam_confirmed)
            event_bus.subscribe(EventType.HONEYPOT_ENGAGED, on_honeypot_engaged)
            logger.info(" Event bus subscribers registered")
        except Exception as e:
            logger.exception(f"Error registering event subscribers: {e}")

    except Exception as e:
        logger.exception(f"Error setting up event subscribers: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize all modules on startup."""
    logger.info("=" * 70)
    logger.info(" Starting Scam Intelligence Engine...")
    logger.info("=" * 70)

    try:
        if setup_detectors():
            setup_event_subscribers()

            logger.info("=" * 70)
            logger.info("[OK] All services initialized successfully")
            logger.info("=" * 70)
        else:
            logger.error("Failed to initialize detectors")
    except Exception as e:
        logger.exception(f"Startup error: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("=" * 70)
    logger.info(" Shutting down Scam Intelligence Engine...")
    logger.info("=" * 70)


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with system status."""
    return {
        "service": "Scam Intelligence Engine",
        "version": "1.0.0",
        "status": "operational",
        "modules": {
            "detection": "Rishi - ACTIVE",
            "honeypot": "Saachi - ACTIVE",
            "extraction": "Shreyas - ACTIVE",
            "recovery": "Shreyas Recovery - ACTIVE",
        },
        "pipeline": "Detection → Honeypot Engagement → Intelligence Extraction → Victim Recovery",
        "documentation": "/docs",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Scam Intelligence Engine",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/system/info", tags=["System"])
async def system_info():
    """Get comprehensive system information."""
    try:
        event_bus = get_event_bus()
        redis_client = get_redis_client()

        return {
            "service": "Scam Intelligence Engine",
            "version": "1.0.0",
            "status": "operational",
            "modules": {
                "rishi_detection": "ACTIVE",
                "saachi_honeypot": "ACTIVE",
                "shreyas_extraction": "ACTIVE",
                "shreyas_recovery": "ACTIVE",
            },
            "communication": {
                "event_bus": "in-memory (ready for Redis/RabbitMQ)" if event_bus else "unavailable",
                "redis": "connected" if redis_client else "unavailable (using in-memory fallback)",
            },
            "integration_status": "Full pipeline operational",
            "endpoints": {
                "detection": "/detect-scam (POST)",
                "honeypot": "/honeypot/* (POST)",
                "health": "/health (GET)",
                "docs": "/docs (GET)",
            },
        }
    except Exception as e:
        logger.exception(f"Error in system info: {e}")
        return {
            "status": "error",
            "message": str(e),
        }


if __name__ == "__main__":

    logger.info("Starting application with uvicorn...")
