from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

logger = logging.getLogger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting application lifespan context")
        yield
    except Exception as e:
        logger.error(f"An error occurred during lifespan: {e}")
        raise
    finally:
        logger.info("Ending application lifespan context")


app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

