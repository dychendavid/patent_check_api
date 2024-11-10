import os
import json
from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

from app.infrastructure.logger import logging
from app.domain.llm.models import ProductClaimDistance, ProductPatentScore
from app.domain.analysis.scheme import LLMInfringementAnalysisScheme





class LLMService:
    def checkInfringingByChatOpenAI(scores):
        os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_KEY')        

         # 0 is less creativity, 1 is maximum creativity
        llm = ChatOpenAI(
            temperature=0.9,
            model_kwargs={"response_format": {"type": "json_object"}}
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are my competitor, and you can find out any possibility to inference specific product infringing your patent. \n{format_instruction}",
                ),
                ("human", "{input}"),
            ]
        )

        chain = prompt | llm 
        try: 
            parser = JsonOutputParser(pydantic_object=LLMInfringementAnalysisScheme)
            invokeParam = {
                "format_instruction": parser.get_format_instructions(),
                "input": [score.__dict__ for score in scores],
            }
            logging.debug("invokeParam", invokeParam)
            res = chain.invoke(invokeParam)
            return res.content

            # TODO save llm logs
        except Exception as e:
            print(f"Error llm invoke: {e}")
