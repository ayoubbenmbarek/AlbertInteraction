"""Routes for Core tag"""
import os
import httpx
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from typing import Optional
from dotenv import load_dotenv
from app.functions.login_function import get_albert_client
from app.models.models import ChatRequest
from app.services.app_services import fetch_models, fetch_model_by_id
from app.models.models import AlbertModelResponse

load_dotenv()


ALBERT_API_BASE_URL = os.getenv("ALBERT_BASE_URL")

router = APIRouter()


@router.get("/models", summary="Fetch Albert models", tags=["Models"])
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
        # async with httpx.AsyncClient() as client:
        response = await client.post(f"{ALBERT_API_BASE_URL}/chat/completions",
                                     json=request.model_dump())

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


# @router.post("/upload")
# async def upload_file(
#     file: UploadFile = File(...),
#     collection: str = Form(...),
#     chunk_size: int = Form(512),
#     chunk_overlap: int = Form(0),
#     length_function: str = Form("len"),
#     is_separator_regex: bool = Form(False),
#     separators: Optional[str] = Form("\n\n,\n,. , "),
#     chunk_min_size: int = Form(0),
#     client: httpx.AsyncClient = Depends(get_albert_client)
# ):
#     """
#     Upload a file to be processed, chunked, and stored into a vector database.
#     """
#     separators_list = separators.split(",")

#     request_payload = {
#         "collection": collection,
#         "chunker": {
#             "name": "LangchainRecursiveCharacterTextSplitter",
#             "args": {
#                 "chunk_size": chunk_size,
#                 "chunk_overlap": chunk_overlap,
#                 "length_function": length_function,
#                 "is_separator_regex": is_separator_regex,
#                 "separators": separators_list,
#                 "chunk_min_size": chunk_min_size,
#             },
#         },
#     }

#     # async with httpx.AsyncClient() as client:
#     try:
#         response = await client.post(
#             f"{ALBERT_API_BASE_URL}",
#             files={"file": (file.filename, await file.read(), file.content_type)},
#             data={"request": request_payload},
#         )
#         response.raise_for_status()
#         return response.json()
#     except httpx.RequestError as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Request to origin API failed: {e}"
#         ) from e
#     except httpx.HTTPStatusError as e:
#         raise HTTPException(
#             status_code=response.status_code,
#             detail=f"Error response from origin API: {e.response.text}"
#         ) from e


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
    # except httpx.RequestError as exc:
    #     raise HTTPException(status_code=500, detail=f"Request error: {exc}")
    # except httpx.HTTPStatusError as exc:
    #     raise HTTPException(status_code=response.status_code, detail=f"HTTP error: {exc}")
