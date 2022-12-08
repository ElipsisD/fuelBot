from dataclasses import dataclass
from environs import Env

@dataclass
class TgBot:
    token: str
    admin_id: list[int]
    use_redis: bool
    logs_chat: int


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class Miscellaneous:
    other_params: str = None


@dataclass
class Config:
    tg_bot: TgBot
    # db: DbConfig
    # misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("API_TOKEN"),
            admin_id=env.int("ADMIN"),
            use_redis=env.bool("USE_REDIS"),
            logs_chat=env.int("LOGS_CHAT_ID"),
        )
    )
