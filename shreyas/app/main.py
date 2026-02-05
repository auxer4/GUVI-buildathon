import logging
from fastapi import FastAPI
from app.listener.event_listener import start_event_listener
from threading import Thread

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Hackathon Backend")


@app.on_event("startup")
def startup_event():
    listener_thread = Thread(target=start_event_listener, daemon=True)
    listener_thread.start()


@app.get("/health")
def health_check():
    return {"status": "ok"}
