from betterconf import Config as BaseConfig
from betterconf import caster, field


class Config(BaseConfig):
    TOKENS = field(caster=caster.ListCaster(";"))
    GROUP_ID = field(caster=caster.to_int)

    class PG(BaseConfig):
        _prefix_ = "PG"
        HOST = field()
        PORT = field(caster=caster.to_int)
        USER = field()
        PASSWORD = field()
        DATABASE = field()


config = Config()
