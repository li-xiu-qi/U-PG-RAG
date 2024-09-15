from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class EmbeddingInput:
    input_content: List[str]
    model_parameters: Optional[Dict[str, float]] = None
    model_name: str = "BAAI/bge-m3"


@dataclass
class EmbeddingOutput:
    task_output: List[List[float]]
    total_tokens: int
