import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()

template = """Te voy a dar informacion sobre algunas bicicletas, me tienes que dar
la informacion (en español) del modelo, marca, precio, tipo y descripcion de las
primeras 3 que aparezcan de forma estructurada (si aparecen menos, me das las que aparezcan).
{response}"""

prompt_template = PromptTemplate(
  input_variables=["respuesta"], template=template
)

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=1000)

prompt = PromptTemplate.from_template("Dime que soy {adjetivo} y por que lo soy")

print(prompt.format(adjetivo="inteligente"))