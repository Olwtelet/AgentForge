import pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict


# Use pydantic base settings for basic settings read from a .env file.
# All fields have defaults so the module can be imported without a .env file;
# agents check for the presence of the keys they need before using a provider.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    openai_api_key: pydantic.SecretStr = pydantic.SecretStr("")
    openai_model_name: str = "gpt-4o-mini"
    azure_endpoint: str = ""
    azure_deployment_name: str = "gpt-4o-mini"
    azure_api_version: str = "2024-10-21"
    azure_api_key: pydantic.SecretStr = pydantic.SecretStr("")
    open_source_model_name: str = "watt-ai/watt-tool-70B"
    tavily_api_key: pydantic.SecretStr = pydantic.SecretStr("")
    embeddings_model_name: str = "text-embedding-ada-002"
    embeddings_api_version: str = "2023-05-15"
    local_embeddings_model_name: str = "all-MiniLM-L6-v2"
    metro_api_token: pydantic.SecretStr = pydantic.SecretStr("")
    # Shared sampling temperature. Kept at 0.0 so cross-framework benchmark
    # runs are comparable instead of depending on each framework's default.
    temperature: float = 0.0


settings: Settings = Settings()
