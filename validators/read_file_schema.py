from pydantic import BaseModel, Field

class ReadFileSchema(BaseModel):
    path_to_file: str = Field(description='Path to the uploaded CSV or XLSX file')