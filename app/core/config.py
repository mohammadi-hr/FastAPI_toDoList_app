from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    PROJECT_NAME: str = "FastAPI Base To_Do_List Project"
    VERSION: str = "1.0.0"

    REDIS_URL: str
    # add API KEY Authentication into the project
    API_KEY: str
    JWT_SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
