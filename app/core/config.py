from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/appdb"
    PROJECT_NAME: str = "FastAPI Base To_Do_List Project"
    VERSION: str = "1.0.0"
    # add API KEY Authentication into the project
    API_KEY: str
    SECRET_KEY: str = "secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: str = "30"
    ACCESS_TOKEN_EXPIRE_DAYS: str = "7"
    ALGORITHM: str = "HS256"


settings = Settings()
