from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    DATABASE_URL: str
    PROJECT_NAME: str = "FastAPI Base To_Do_List Project"
    VERSION: str = "1.0.0"

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    # add API KEY Authentication into the project
    API_KEY: str
    JWT_SECRET_KEY: str
    ALGORITHM: str
    SQLALCHEMY_TEST_DATABASE_URL: str = "sqlite:///:memory:"

    RABBITMQ_HOST: str
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_PORT: int

    ELASTICSEARCH_HOST: str

    class Config:
        env_file = (
            ".env.test" if "PYTEST_CURRENT_TEST" in os.environ else ".env"
        )
        env_file_encoding = "utf-8"


settings = Settings()
