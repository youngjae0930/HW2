from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Object Detective API"
    MODEL_ID: str = "microsoft/Florence-2-base"
    DEBUG: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
