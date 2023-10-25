from betterconf import Config
from betterconf import caster, field


class Env(Config):
    class Bot(Config):
        _prefix_ = "BOT"
        ACCESS_TOKEN_FILE = field()
        GROUP_ID_FILE = field()

    class Postgres(Config):
        _prefix_ = "POSTGRES"
        HOST = field()
        PORT = field(caster=caster.to_int)

        USER_FILE = field()
        PASSWORD_FILE = field()
        DB_FILE = field()


env = Env()
