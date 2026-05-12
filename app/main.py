from fastapi import FastAPI
from app.routers.bot_router import router
from app.core.logger import logger

app = FastAPI(title="Teams Defender Bot")
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Teams Defender Bot application...")

@app.get("/health")
def health():
    logger.info("Health check endpoint called")
    return {"status": "ok"}