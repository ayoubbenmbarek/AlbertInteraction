"""Authorize requests"""
import os
import httpx
from dotenv import load_dotenv


load_dotenv()

ALBERT_API_KEY = os.getenv("ALBERT_API_KEY")


def get_albert_client() -> httpx.AsyncClient:
    """Returns client with desired api key.

    Returns:
        httpx.AsyncClient: _description_
    """
    headers = {
        "Authorization": f"Bearer {ALBERT_API_KEY}"
    }
    return httpx.AsyncClient(headers=headers)
