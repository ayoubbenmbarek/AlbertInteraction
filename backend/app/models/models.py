"""Represent models responses"""
from enum import Enum
from typing import List, Optional, Literal, Union
from pydantic import BaseModel
from uuid import UUID
# from googletrans import LANGUAGES


class AlbertModelResponse(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    id: str
    created: int
    object: str
    owned_by: str
    max_context_length: int
    type: str
    status: str
    aliases: List[str]

# class ChatRequest(BaseModel):
#     """_summary_

#     Args:
#         BaseModel (_type_): _description_
#     """
#     model: str
#     messages: list
#     max_tokens: int = 100
#     temperature: float = 0.7


class FunctionCall(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    arguments: str
    name: str


class ToolCall(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    id: str
    function: FunctionCall
    type: str


class Message(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    content: str
    role: Literal["system", "user", "assistant", "tool", "function"]
    name: str
    audio: Optional[dict] = None
    function_call: Optional[FunctionCall] = None
    refusal: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


class SearchArgs(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    # collections: List[Union[UUID, Literal["internet"]]]
    collections: List[str]
    rff_k: int
    k: int
    method: Literal["hybrid", "lexical", "semantic"]
    score_threshold: int
    template: str


class ChatRequest(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    messages: List[Message]
    model: str
    stream: bool = False
    frequency_penalty: float = 0
    max_tokens: int = 0
    n: int = 1
    presence_penalty: float = 0
    temperature: float = 0.7
    top_p: float = 1
    user: str
    seed: int = 0
    stop: Optional[str] = None
    best_of: int = 0
    top_k: int = -1
    min_p: int = 0
    search: bool = False
    search_args: Optional[SearchArgs] = None
    additionalProp1: Optional[dict] = None


class CompletionRequest(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    prompt: str
    model: str
    best_of: Optional[int] = 0
    echo: Optional[bool] = False
    frequency_penalty: Optional[float] = 0
    logit_bias: Optional[dict] = {
        "additionalProp1": 0,
        "additionalProp2": 0,
        "additionalProp3": 0
    }
    logprobs: Optional[int] = 0
    max_tokens: Optional[int] = 16
    n: Optional[int] = 1
    presence_penalty: Optional[float] = 0
    seed: Optional[int] = 0
    stop: Optional[str] = "string"
    stream: Optional[bool] = False
    # suffix: Optional[str] = "string"
    temperature: Optional[float] = 1
    top_p: Optional[float] = 1
    user: Optional[str] = "string"


class Language(str, Enum):
    """_summary_

    Args:
        str (_type_): _description_
        Enum (_type_): _description_
    """
    english = "en"
    french = "fr"
    spanish = "es"
    german = "de"
    italian = "it"
    # locals().update({name.replace(" ", "_"): code for code, name in LANGUAGES.items()})


class TranscriptionRequest(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    model: str = "openai/whisper-large-v3"
    language: str
    prompt: Optional[str] = None
    response_format: str = "json"
    temperature: float = 0.0
    timestamp_granularities: Optional[List[str]] = None
