import os
from dotenv import load_dotenv, dotenv_values


def load_env():
    env_name = os.getenv('ENV')
    env_path = f".env.{env_name}"
    load_dotenv(env_path)
    
    # below is debug info
    # print(f"Reading from: {env_path}")

    # print("Direct file reading:")
    # with open(env_path, 'r') as env:
    #     print(env.read())

    # print("Actual environment variables:")
    # for key in dotenv_values(env_path).keys():
    #     print(f"{key}={os.getenv(key)}")

load_env()