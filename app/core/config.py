from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv(override=True)


class GoogleSettings(BaseSettings):
    GOOGLE_API_KEY: str 
    GOOGLE_MODEL_PRO: str = "gemini-2.5-pro"
    GOOGLE_MODEL_FLASH: str = "gemini-2.5-flash"