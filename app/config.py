from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_password: str
    database_name: str
    database_username: str
    database_ssl: bool = False
    secret_key: str
    algorithm: str
    email_code:str
    access_token_expire_days: int
    groq_api_key:str
    class Config:
        env_file = ".env"  # Updated path to .env
        case_sensitive = False

settings = Settings()
