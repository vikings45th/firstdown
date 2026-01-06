from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Ranker internal URL (Cloud Run internal ingress service URL)
    RANKER_URL: str = "http://ranker:8080"
    REQUEST_TIMEOUT_SEC: float = 10.0
    RANKER_TIMEOUT_SEC: float = 3.0

    # BigQuery
    BQ_DATASET: str = "firstdown_mvp"
    BQ_TABLE_REQUEST: str = "route_request"
    BQ_TABLE_CANDIDATE: str = "route_candidate"
    BQ_TABLE_PROPOSAL: str = "route_proposal"
    BQ_TABLE_FEEDBACK: str = "route_feedback"

    # Feature/versioning
    FEATURES_VERSION: str = "mvp_v1"


settings = Settings()
