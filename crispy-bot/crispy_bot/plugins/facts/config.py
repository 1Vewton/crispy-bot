from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    random_fact_url: str = "https://uselessfacts.jsph.pl/api/v2/facts/random"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_provider: str = ""
    llm_model_name: str = ""
