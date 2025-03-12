from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Article(BaseModel):
    date: datetime
    title: str
    summary: str
    link: str
    text: Optional[str] = None
    
    
@dataclass
class ChatGPTModel:
    self_hosted: bool
    model: str
    
COMPONENT_MAP = {
    "llm-model.chat-gpt": ChatGPTModel
}

def create_instance_from_dynamic_zone(data: Dict[str, Any]):
    """Creates a dataclass instance based on __component field, ignoring `id` and `__component`."""
    component_type = data.get("__component")
    
    if not component_type or component_type not in COMPONENT_MAP:
        raise ValueError(f"Unknown component type: {component_type}")
    
    cls = COMPONENT_MAP[component_type]  # Get the class
    filtered_data = {k: v for k, v in data.items() if k not in {"__component", "id"}}  # Remove __component & id
    return cls(**filtered_data)

