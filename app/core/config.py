from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    # Bot credentials
    APP_ID: str = os.getenv("MICROSOFT_APP_ID", "")
    APP_PASSWORD: str = os.getenv("MICROSOFT_APP_PASSWORD", "")
    TENANT_ID: str = os.getenv("TENANT_ID", "")

    # Defender credentials
    DEFENDER_CLIENT_ID: str = os.getenv("DEFENDER_CLIENT_ID", "")
    DEFENDER_CLIENT_SECRET: str = os.getenv("DEFENDER_CLIENT_SECRET", "")
    DEFENDER_TENANT_ID: str = os.getenv("DEFENDER_TENANT_ID", "")

settings = Settings()