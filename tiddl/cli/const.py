from tiddl.infrastructure.paths import APP_DIR_NAME as _APP_DIR_NAME, ENV_KEY, AppPaths


APP_DIR_NAME = _APP_DIR_NAME


APP_PATHS = AppPaths()
APP_PATH = APP_PATHS.root


def get_app_path(env_key: str = ENV_KEY):
    return AppPaths(env_key=env_key).root
