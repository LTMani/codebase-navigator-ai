from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from app.errors.exceptions import ValidationError


@dataclass
class CopilotPromptSchema:
    prompt: str
    conversation_id: Optional[str] = None
    focused_file_path: Optional[str] = None
    focused_symbol_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CopilotPromptSchema":
        if not isinstance(data, dict):
            raise ValidationError("Request payload must be a JSON object.")

        prompt = str(data.get("prompt", data.get("message", ""))).strip()
        if not prompt:
            raise ValidationError("Question or prompt is required.")

        conversation_id = data.get("conversation_id")
        if conversation_id:
            conversation_id = str(conversation_id).strip()

        focused_file_path = data.get("focused_file_path")
        if focused_file_path:
            focused_file_path = str(focused_file_path).strip()

        focused_symbol_name = data.get("focused_symbol_name")
        if focused_symbol_name:
            focused_symbol_name = str(focused_symbol_name).strip()

        return cls(
            prompt=prompt,
            conversation_id=conversation_id,
            focused_file_path=focused_file_path,
            focused_symbol_name=focused_symbol_name,
        )
