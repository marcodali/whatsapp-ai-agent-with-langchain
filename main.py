from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence

load_dotenv()

# Crear un traductor de cualquier idioma a cualquier idioma
traductor_template = "Eres un asistente útil que traduce del {idioma_origen} al {idioma_destino} el texto: {texto}."
traductor_prompt_template = PromptTemplate(
    input_variables=["idioma_origen", "idioma_destino", "texto"],
    template=traductor_template
)

llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

# Crear una secuencia ejecutable
chain = RunnableSequence(
    traductor_prompt_template,
    llm
)

texto = "Donde nuestras voces suenan ven a buscarnos, nos hemos llevado lo que mas deseas y para encontrarlo tienes una hora."
respuesta = chain.invoke({"idioma_origen": "español", "idioma_destino": "inglés", "texto": texto})
print(respuesta.content)