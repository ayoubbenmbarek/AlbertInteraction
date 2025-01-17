"""Routes for Core tag"""
import os

import json
import httpx
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Body
from dotenv import load_dotenv
from enum import Enum
from app.functions.login_function import get_albert_client
from app.models.models import ChatRequest
from app.services.app_services import fetch_models, fetch_model_by_id
from app.models.models import AlbertModelResponse, CompletionRequest, Language

load_dotenv()


ALBERT_API_BASE_URL = os.getenv("ALBERT_API_BASE_URL")
ALBERT_API_HEALTH_URL = os.getenv("ALBERT_API_HEALTH_URL")

router = APIRouter()


@router.get("/health", tags=["Health Check"])
async def health_check(client: httpx.AsyncClient = Depends(get_albert_client)):
    """
    Check Albert Health.
    """
    status = {"api": "ok", "albert_api": "ok"}

    try:
        response = await client.get(ALBERT_API_HEALTH_URL, timeout=5.0)
        print(response.status_code)
        if response.status_code != 200:
            status["albert_api"] = "down"
    except Exception:
        status["albert_api"] = "down"

    return status


@router.get("/models", summary="Get Albert models", tags=["Models"])
async def get_albert_models(client: httpx.AsyncClient = Depends(get_albert_client)):
    """
    Endpoint to fetch the list of models from the Albert API.
    """
    try:
        models = await fetch_models(client=client)
        return models
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching models: {e}"
        ) from e


@router.get("/models/{model_id}", response_model=AlbertModelResponse, tags=["Models"])
async def get_model_by_id(model_id: str, client: httpx.AsyncClient = Depends(get_albert_client)):
    """Fetch model data from Albert API based on the model ID.

    Args:
        model_id (str): _description_

    Returns:
        _type_: _description_
    """
    model_data = await fetch_model_by_id(model_id, client=client)
    return model_data


@router.post("/chat-completion/")
async def chat_completion(request: ChatRequest,
                          client: httpx.AsyncClient = Depends(get_albert_client)):
    """_summary_

    Args:
        request (ChatRequest): _description_
        client (httpx.AsyncClient, optional): _description_. Defaults to Depends(get_albert_client).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    try:
        response = await client.post(
            f"{ALBERT_API_BASE_URL}/chat/completions",
            json=request.model_dump()
        )
        response.raise_for_status()
        return response.json()
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


@router.post("/completions")
async def completions(
    request: CompletionRequest,
    client: httpx.AsyncClient = Depends(get_albert_client)
):
    """
    Calls the completions endpoint with the provided parameters.

    Args:
        request (CompletionRequest): The request data.
        client (httpx.AsyncClient): The HTTP client to make the request.

    Returns:
        dict: The response from the completions API.
    """
    # payload = request.dict()
    payload = request.model_dump()

    try:
        response = await client.post(f"{ALBERT_API_BASE_URL}/completions", json=payload)
        response.raise_for_status()
        # response_data = response.json()
        # text = response_data.get("choices", [{}])[0].get("text", "")

        # return text
        return response.json()

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


@router.get("/model-details/{model_id}", tags=["Models"])
async def get_model_details(model_id: str, client: httpx.AsyncClient = Depends(get_albert_client)):
    """_summary_

    Args:
        model_id (str): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    encoded_model_id = model_id.replace("/", "%2F")
    url = f"{ALBERT_API_BASE_URL}/models/{encoded_model_id}"

    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
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


@router.get("/collections")
async def get_collections(client: httpx.AsyncClient = Depends(get_albert_client)):
    """Fetch and return collections from the Albert API.

    Args:
        client (httpx.AsyncClient, optional): _description_. Defaults to Depends(get_albert_client).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    try:
        response = await client.get(
            f"{ALBERT_API_BASE_URL}/collections",
        )
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Request to origin API failed: {ALBERT_API_BASE_URL}/collections {e}"
        ) from e
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error response from origin API: {e.response.text}"
        ) from e


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    collection: str = Form(...),
    chunk_size: int = Form(512),
    chunk_overlap: int = Form(0),
    length_function: str = Form("len"),
    is_separator_regex: bool = Form(False),
    separators: str = Form("\n\n,\n,. , "),
    chunk_min_size: int = Form(0),
    client: httpx.AsyncClient = Depends(get_albert_client),
):
    """
    Upload a file to be processed, chunked, and stored into a vector database. Supported file types : pdf, html, json.

    Supported files types:

        pdf: Portable Document Format file.
        json: JavaScript Object Notation file. For JSON,
        file structure like a list of documents: [{"text": "hello world", "title": "my document", "metadata": {"autor": "me"}}, ...]}
        or [{"text": "hello world", "title": "my document"}, ...]} Each document must have a "text" and "title" keys and "metadata"
        key (optional) with dict type value.
        html: Hypertext Markup Language file.
        markdown: Markdown Language file.
    """
    separators_list = [sep.strip() for sep in separators.split(",") if sep.strip()]

    request_payload = {
        "collection": collection,
        "chunker": {
            "name": "LangchainRecursiveCharacterTextSplitter",
            "args": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "length_function": length_function,
                "is_separator_regex": is_separator_regex,
                "separators": separators_list,
                "chunk_min_size": chunk_min_size,
            },
        },
    }

    try:
        response = await client.post(
            f"{ALBERT_API_BASE_URL}/files",
            files={
                "file": (file.filename, await file.read(), file.content_type),
                "request": (None, json.dumps(request_payload), "application/json"),
            },
        )
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Request to external API failed: {e}",
        ) from e
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error response from external API: {e.response.text}",
        ) from e


@router.post("/transcribe/")
async def transcribe_audio(
    file: UploadFile = File(...),
    model: str = Form("openai/whisper-large-v3"),
    language: str = Form("fr"),
    prompt: Optional[str] = Form(""),
    response_format: str = Form("json"),
    temperature: float = Form(0.0),
    timestamp_granularities: Optional[List[str]] = Form(None),
    client: httpx.AsyncClient = Depends(get_albert_client),
):
    """Send an audio file for transcription"""

    files = {"file": (file.filename, file.file, file.content_type)}
    data = {
        "model": model,
        "language": language,
        "prompt": prompt,
        "response_format": response_format,
        "temperature": str(temperature),
    }

    if timestamp_granularities:
        for i, granularity in enumerate(timestamp_granularities):
            data[f"timestamp_granularities[{i}]"] = granularity
    try:
        response = await client.post(f"{ALBERT_API_BASE_URL}/audio/transcriptions",
                               files=files, data=data)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Request to external API failed: {e}",
        ) from e
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error response from external API: {e.response.text}",
        ) from e

from pydantic import BaseModel
class Message(BaseModel):
    role: str
    content: str
    name: Optional[str] = None  # 'name' can be optional
    tool_call_id: Optional[str] = None

class SearchArgs(BaseModel):
    collections: List[str]
    rff_k: int
    k: int
    method: str
    score_threshold: float
    template: str

class ChatRequesty(BaseModel):
    messages: List[Message]
    model: str
    stream: Optional[bool] = False
    frequency_penalty: Optional[float] = 0
    max_tokens: Optional[int] = 5
    n: Optional[int] = 1
    presence_penalty: Optional[float] = 0
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1
    user: Optional[str] = None  # Make 'user' optional
    seed: Optional[int] = 0
    stop: Optional[str] = None
    best_of: Optional[int] = 0
    top_k: Optional[int] = -1
    min_p: Optional[float] = 0
    search: Optional[bool] = False
    search_args: Optional[SearchArgs] = None

ALBERT_API_CHAT_URL = "https://albert.api.dev.etalab.gouv.fr/v1/chat/completions"

@router.post("/chat")
async def chat(request: ChatRequesty, client: httpx.AsyncClient = Depends(get_albert_client)):
    try:
        response = await client.post(ALBERT_API_CHAT_URL, json=request.dict(exclude_none=True))
        response.raise_for_status()
        api_response = response.json()
        print("API Response:", api_response)  # Log the entire response here
        assistant_message = api_response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not assistant_message:
            print("Assistant message is empty.")
        return {"assistant_reply": assistant_message}
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Request to external API failed: {e}",
        ) from e
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error response from external API: {e.response.text}",
        ) from e