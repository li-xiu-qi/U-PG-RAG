from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class EmbeddingInput(BaseModel):
    name: str = "BAAI/bge-m3"
    input_content: List[str]
    set_params: Optional[Dict[str, float]] = {}


class EmbeddingOutput(BaseModel):
    output: List[List[float]]
    total_tokens: int


class LLMInput(BaseModel):
    name: str
    input_content: List[dict]
    set_param: Dict[str, Any] = {
        "max_tokens": 4096,
        "temperature": 0.7,
    }


class LLMOutput(BaseModel):
    output: str
    total_tokens: int
