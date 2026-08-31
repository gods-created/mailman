from pydantic import BaseModel, Field 

class TemporaryFileSchema(BaseModel):
    path_to_file: str = Field(description='Path to the file, which was uploaded')