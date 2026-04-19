from dataclasses import dataclass
from functools import cached_property, lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass(frozen=True)
class TgBotSettings:
    token: str
    admin_id: int
    use_redis: bool
    logs_chat: int


@dataclass(frozen=True)
class DbSettings:
    sqlite_path: Path

    @property
    def sqlite_url(self) -> str:
        return f"sqlite:///{self.sqlite_path}"

    @property
    def data_dir(self) -> Path:
        return self.sqlite_path.parent


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_token: str = Field(validation_alias="API_TOKEN")
    admin_id: int = Field(validation_alias="ADMIN")
    use_redis: bool = Field(validation_alias="USE_REDIS")
    logs_chat: int = Field(validation_alias="LOGS_CHAT_ID")
    sqlite_path: Path = Field(default=Path("data/fuelbot.sqlite3"), validation_alias="SQLITE_PATH")

    @cached_property
    def tg_bot(self) -> TgBotSettings:
        return TgBotSettings(
            token=self.api_token,
            admin_id=self.admin_id,
            use_redis=self.use_redis,
            logs_chat=self.logs_chat,
        )

    @cached_property
    def db(self) -> DbSettings:
        return DbSettings(sqlite_path=self.sqlite_path)


@lru_cache(maxsize=1)
def load_config(path: str | None = None) -> Config:
    if path is None:
        return Config()
    return Config(_env_file=path)
