from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nightshift"

    # OANDA
    oanda_api_key: str = ""
    oanda_account_id: str = ""
    oanda_api_url: str = "https://api-fxpractice.oanda.com"

    # Ingestion
    watchlist: str = "EUR_USD,GBP_USD,USD_JPY"
    ingest_interval: int = 60
    ingest_timeframes: str = "M5,M15,H1,H4,D"

    # App
    debug: bool = False

    @property
    def watchlist_symbols(self) -> list[str]:
        return [s.strip() for s in self.watchlist.split(",") if s.strip()]

    @property
    def timeframes_list(self) -> list[str]:
        return [t.strip() for t in self.ingest_timeframes.split(",") if t.strip()]


settings = Settings()
