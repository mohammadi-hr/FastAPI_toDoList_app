from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Base To_Do_List Project"
    VERSION: str = "1.0.0"
    DATABASE_URL: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
