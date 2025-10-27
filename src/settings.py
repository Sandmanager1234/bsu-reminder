from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramSettings(BaseSettings):
    token: str
    admin: int

class DatabaseSettings(BaseSettings):
    db_url: str

class CelerySettings(BaseSettings):
    broker_url: str
    backend_url: str

class BsuSettings(BaseSettings):
    api_url: str

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_nested_delimiter='__', extra='ignore')

    telegram: TelegramSettings
    database: DatabaseSettings
    bsu_client: BsuSettings
    celery: CelerySettings