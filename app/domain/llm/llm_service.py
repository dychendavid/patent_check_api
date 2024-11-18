from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.infrastructure.logger import logger
from app.domain.analysis.scheme import LLMInfringementAnalysisScheme


class LLMService:
    @classmethod
    def check_infringing_by_chat_open_ai(cls, scores):
        # NOTE ChatOpenAI will read key from os.environ['OPENAI_API_KEY']
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
                "input": [score.as_dict() for score in scores],
            }
            res = chain.invoke(invokeParam)
            return res.content

        except Exception as e:
            logger.error("Error llm invoke", exc_info=e)
