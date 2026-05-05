from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_URL: str = "postgresql+asyncpg://ims_user:ims_password@localhost:5432/ims_db"
    MONGODB_URL: str = "mongodb://ims_root:ims_password@localhost:27017/"
    REDIS_URL: str = "redis://localhost:6379/0"

settings = Settings()
