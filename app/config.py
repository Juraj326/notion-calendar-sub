from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    NOTION_API_KEY: str
    ASSIGNMENTS_DATABASE_ID: str
    ASSIGNMENTS_CALENDAR_NAME: str = "Assignments"
    SUBSCRIPTIONS_DATABASE_ID: str
    SUBSCRIPTIONS_CALENDAR_NAME: str = "Subscriptions"
    TOKEN: str


settings = Settings()  # type: ignore
