"""Represent models responses"""
from typing import List, Optional
from pydantic import BaseModel

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
    role: str
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
    """
    collections: List[str]
    rff_k: int
    k: int
    method: str
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
