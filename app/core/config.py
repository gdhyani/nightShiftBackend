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

    # LLM (self-hosted, OpenAI-compatible)
    llm_api_url: str = "http://localhost:8080/v1"
    llm_api_key: str = ""
    llm_model_name: str = "default"

    # News
    finnhub_api_key: str = ""

    # Agent schedules (seconds)
    agent_news_interval: int = 300
    agent_order_flow_interval: int = 60
    agent_session_interval: int = 900
    agent_correlation_interval: int = 1800
    agent_range_interval: int = 3600
    agent_bias_interval: int = 14400
    agent_liquidity_interval: int = 3600
    agent_structure_interval: int = 3600

    # App
    debug: bool = False

    @property
    def watchlist_symbols(self) -> list[str]:
        return [s.strip() for s in self.watchlist.split(",") if s.strip()]

    @property
    def timeframes_list(self) -> list[str]:
        return [t.strip() for t in self.ingest_timeframes.split(",") if t.strip()]


settings = Settings()
