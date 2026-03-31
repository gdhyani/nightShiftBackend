from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nightshift"

    # OANDA
    oanda_api_key: str = ""
    oanda_account_id: str = ""
    oanda_api_url: str = "https://api-fxpractice.oanda.com"

    # App
    debug: bool = False


settings = Settings()
