from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    NOTION_API_KEY: str
    NOTION_DATABASE_ID: str
    CALENDAR_NAME: str = "Assignments"
    TOKEN: str


settings = Settings()  # type: ignore
