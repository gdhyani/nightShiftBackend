from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/nightshift"
    )

    # Upstox API
    upstox_client_id: str = ""
    upstox_client_secret: str = ""
    upstox_redirect_uri: str = (
        "http://localhost:8000/api/auth/upstox/callback"
    )
    upstox_notifier_url: str = (
        "http://localhost:8000/api/webhooks/upstox/token"
    )
    upstox_postback_url: str = (
        "http://localhost:8000/api/webhooks/upstox/orders"
    )
    upstox_sandbox_token: str = ""
    upstox_api_base_url: str = "https://api.upstox.com"

    # Trading
    default_trading_mode: str = "paper"
    token_encryption_key: str = ""

    # Ingestion
    watchlist: str = (
        "NSE_EQ|INE848E01016,NSE_EQ|INE669E01016,NSE_EQ|INE002A01018"
    )
    ingest_interval: int = 60
    ingest_timeframes: str = "1,5,15,60,day"

    # LLM
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
