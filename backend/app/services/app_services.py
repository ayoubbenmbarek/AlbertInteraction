"""Module to interact with Albert Api Services"""
import os

from urllib.parse import quote
import httpx
from dotenv import load_dotenv
from fastapi import HTTPException


load_dotenv()


ALBERT_API_BASE_URL = os.getenv("ALBERT_BASE_URL")

async def fetch_models(client: httpx.AsyncClient):
    """Fetches the list of models from the Albert API.

    Returns:
        _type_: _description_
    """
    response = await client.get(f"{ALBERT_API_BASE_URL}/v1/models")
    response.raise_for_status()
    return response.json()

async def fetch_model_by_id(model_id: str, client: httpx.AsyncClient):
    """_summary_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    encoded_model_id = quote(model_id)
    print(encoded_model_id)
    url = f"{ALBERT_API_BASE_URL}/v1/models/{encoded_model_id}"

    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Request to origin API failed: {e}"
        ) from e
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error response from origin API: {e.response.text}"
        ) from e

    model_data = response.json()
    return model_data
