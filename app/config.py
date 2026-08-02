from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_username: str
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    log_level: str = "INFO"
    valkey_host: str
    valkey_port: str
    kafka_bootstrap_servers: str = "localhost:9092"

    model_config = SettingsConfigDict(env_file=".env")


    # class Config:
    #     env_file = ".env"


settings = Settings()