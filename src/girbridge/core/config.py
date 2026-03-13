from pydantic import BaseModel


class AppConfig(BaseModel):
    draft_mapping_prompt_file: str
