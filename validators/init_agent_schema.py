from pydantic import BaseModel, ValidationInfo, Field, field_validator
from typing import Optional

class InitAgentSchema(BaseModel):
    gemini_api_key: Optional[str] = Field(default=None)
    gemini_model_name: Optional[str] = Field(default=None)
    template: Optional[str] = Field(default=None)

    @field_validator('gemini_api_key', 'gemini_model_name', 'template')
    @classmethod
    def validate_field(cls, value: Optional[str], info: ValidationInfo) -> str:
        if not value:
            field_name = str(info.field_name)
            raise ValueError(f'\'{field_name.upper()}\' is not specified')

        return value