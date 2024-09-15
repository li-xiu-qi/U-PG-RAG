from dataclasses import dataclass, field
from typing import List, Union, Literal, Dict, Any


@dataclass
class LLMInput:
    model_name: str
    task_input: List[dict]
    model_parameters: Dict[str, Any] = field(default_factory=lambda: {
        "max_tokens": 4096,
        "temperature": 0.7,
        "top_p": 0.7,
        "frequency_penalty": 0.0,
    })


@dataclass
class LLMOutput:
    task_output: str
    total_tokens: int
