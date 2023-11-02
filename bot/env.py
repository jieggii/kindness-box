from betterconf import Config, caster, field


class Env(Config):
    class Bot(Config):
        _prefix_ = "BOT"
        ACCESS_TOKEN_FILE = field()
        GROUP_ID_FILE = field()

    class Mongo(Config):
        _prefix_ = "MONGO"
        HOST = field()
        PORT = field(caster=caster.to_int)

        USERNAME_FILE = field()
        PASSWORD_FILE = field()
        DATABASE = field()


env = Env()
