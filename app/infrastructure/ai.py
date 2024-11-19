import os 
import numpy as np
from langchain_openai import OpenAIEmbeddings
from app.infrastructure.logger import logger
from app.infrastructure.env import get_env, EnvEnum

class AI:
    @classmethod
    async def get_embeddings(cls, embeds: list, dimension:int=1536):

        if get_env() == EnvEnum.Development.value:
            logger.warning('Get embedding from np')
            return [np.random.rand(dimension) for embed in embeds]
        else:
            logger.warning('Get embedding from OpenAI')
            embeddings_model = OpenAIEmbeddings(api_key=os.getenv('OPENAI_API_KEY'), model="text-embedding-3-small")
            return embeddings_model.embed_documents(embeds)
