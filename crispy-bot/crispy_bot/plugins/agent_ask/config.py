from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model_name: str = ""
    exa_api_key: str = ""
    exa_url: str = ""
    tool_timeout: int = 120
