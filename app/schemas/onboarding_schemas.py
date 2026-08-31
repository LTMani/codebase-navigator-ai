from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from app.errors.exceptions import ValidationError


@dataclass
class StepCompletionSchema:
    step_id: str
    is_completed: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StepCompletionSchema":
        if not isinstance(data, dict):
            raise ValidationError("Request payload must be a JSON object.")
        step_id = str(data.get("step_id", "")).strip()
        if not step_id:
            raise ValidationError("step_id is required.")
        return cls(step_id=step_id, is_completed=bool(data.get("is_completed", True)))


@dataclass
class QuizSubmissionSchema:
    answers: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuizSubmissionSchema":
        if not isinstance(data, dict):
            raise ValidationError("Request payload must be a JSON object.")
        answers = data.get("answers")
        if not isinstance(answers, dict):
            raise ValidationError("answers dictionary is required.")
        return cls(answers=answers)
