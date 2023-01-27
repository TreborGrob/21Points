from dynaconf import Dynaconf


settings = Dynaconf(
    envvar_prefix="DYNACONF",  # export envvars with `export DYNACONF_FOO=bar`.
    settings_files=['settings.ini'],  # Load files in the given order.
)

ADMIN_ID = settings.admin_id
TOKEN = settings.token

if __name__ == "__main__":
    print('Запустил конфиг')