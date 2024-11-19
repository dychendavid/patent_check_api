import os
import enum
import sys
from dotenv import load_dotenv, dotenv_values
from app.infrastructure.logger import logger

class EnvEnum(str, enum.Enum):
    Development = "dev"
    Production = "prod"


def load_env():
    env_name = get_env()
    env_path = f".env.{env_name}"
    load_dotenv(env_path)

    # below is debug info
    logger.debug(f"Reading from: {env_path}")

    logger.debug("Direct file reading:")
    with open(env_path, 'r') as env:
        print(env.read())

    logger.debug("Actual environment variables:")
    for key in dotenv_values(env_path).keys():
        logger.debug(f"{key}={os.getenv(key)}")

def get_env():
    if os.getenv('ENV'):
        return os.getenv('ENV')

    for arg in sys.argv:
        match arg:
            # for fastapi run
            case "run":
                return EnvEnum.Production.value
            
            # for python seeder.py prod
            case "prod":
                return EnvEnum.Production.value
        
    return EnvEnum.Development.value



load_env()