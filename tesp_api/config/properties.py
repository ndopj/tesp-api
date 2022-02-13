from dynaconf import Dynaconf


def get_properties() -> Dynaconf:
    return Dynaconf(
        settings_files=["settings.toml", ".secrets.toml"],
        environments=True,
        default_env="default",
        env_switcher="FASTAPI_PROFILE",
        envvar_prefix="TESP_API",
        merge_enabled=True
    )


properties = get_properties()
