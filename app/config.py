from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Birth Map Agent Demo"
    environment: str = "dev"
    # Azure AD / Azure OpenAI settings (hard-coded for quick demo / POC)
    TENANT_ID: str | None = "fed95e69-8d73-43fe-affb-a7d85ede36fb"
    CLIENT_ID: str | None = "dc78e8c9-4de2-4c3d-819f-f14a8fef034b"
    # CLIENT_SECRET has been removed from source for push protection.
    # For local runs place the secret in .env as CLIENT_SECRET or set the env var.
    CLIENT_SECRET: str | None = None
    OPENAI_APP_API_ID: str | None = "api://e689b268-e7d0-4fb5-bb85-b29ce44fb4b0"
    # Use the base OpenAI Azure endpoint (without /responses)
    AZURE_OPENAI_ENDPOINT: str | None = "https://ext.api.insim.biz/t/nn.nl/openaiservices/v1.0.0/openai/v1"
    AZURE_OPENAI_DEPLOYMENT: str | None = "gpt-4.1"
    AZURE_OPENAI_VERSION: str | None = "preview"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
