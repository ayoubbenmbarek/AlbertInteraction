"""Main routes"""
from fastapi import FastAPI
from app.routes import core

app = FastAPI(
    title="Test Albert API",
    description="API to interact with Albert Api Services",
    version="1.0.0",
)

app.include_router(core.router)

@app.get("/", include_in_schema=False)
async def root():
    """_summary_

    Returns:
        _type_: _description_
    """
    return {"message": "Welcome to the Albert Services API"}
