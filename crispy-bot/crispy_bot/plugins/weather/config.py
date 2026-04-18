from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_provider: str = ""
    llm_model_name: str = ""
    private_key_qweather_path: str = ""
    project_id: str = ""
    key_id: str = ""
    api_host: str = ""
