import os
from dotenv import load_dotenv


def load_env():
    env_name = os.getenv('ENV')
    env_path = f".env.{env_name}"
    load_dotenv(env_path)

load_env()