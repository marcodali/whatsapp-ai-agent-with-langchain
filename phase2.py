from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from laTerceraEsLaVencida import RedisVectorSearch
from dotenv import load_dotenv

load_dotenv()

class AmorisChatbot:
    def __init__(self, index_name="vector_store_idx:social_profiles"):
        # Inicializar componentes base
        self.redis_search = RedisVectorSearch()
        self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")
        
        # Definir el prompt para procesar consultas de usuario
        self.query_prompt = PromptTemplate(
            input_variables=["consulta_usuario"],
            template="""Eres un asistente experto en búsqueda de perfiles sociales.
            Analiza la siguiente consulta y genera una versión mejorada que ayude a encontrar los perfiles más relevantes.
            
            Consulta original: {consulta_usuario}
            
            Reglas:
            1. Mantén las palabras clave importantes (profesión, país, red social)
            2. Expande sinónimos relevantes
            3. Añade contexto si es necesario
            4. Mantén el lenguaje natural
            
            Responde SOLO con la consulta mejorada, sin explicaciones adicionales."""
        )
        
        # Definir el prompt para formatear resultados
        self.response_prompt = PromptTemplate(
            input_variables=["consulta_usuario", "resultados"],
            template="""Actúa como un asistente amigable y profesional que ayuda a conectar personas.
            
            Consulta del usuario: {consulta_usuario}
            
            Resultados encontrados:
            {resultados}
            
            Por favor, presenta los resultados de manera conversacional y amigable:
            1. Saluda al usuario
            2. Resume brevemente lo que encontraste
            3. Presenta cada perfil de manera atractiva
            4. Sugiere cómo podrían refinar su búsqueda si los resultados no son ideales
            
            Mantén un tono profesional pero cercano."""
        )
        
        # Crear las cadenas de procesamiento
        self.query_chain = RunnableSequence(
            self.query_prompt,
            self.llm
        )
        
        self.response_chain = RunnableSequence(
            self.response_prompt,
            self.llm
        )
    
    def process_query(self, user_input: str, num_results: int = 3) -> str:
        """
        Procesa la consulta del usuario y retorna una respuesta formatada.
        
        Args:
            user_input (str): Consulta del usuario
            num_results (int): Número de resultados a buscar
            
        Returns:
            str: Respuesta formatada para el usuario
        """
        # Paso 1: Mejorar la consulta con el LLM
        enhanced_query = self.query_chain.invoke({
            "consulta_usuario": user_input
        }).content
        
        # Paso 2: Realizar la búsqueda vectorial
        results = self.redis_search.search_similar_profiles(enhanced_query, k=num_results)
        
        # Paso 3: Formatear los resultados para una respuesta amigable
        formatted_response = self.response_chain.invoke({
            "consulta_usuario": user_input,
            "resultados": str(results)  # Convertimos a string para el prompt
        })
        
        return formatted_response.content
    
    def chat(self):
        """
        Inicia una sesión de chat interactiva con el usuario.
        """
        print("¡Hola! Soy tu asistente de Amoris Laboris. ¿En qué puedo ayudarte hoy?")
        print("(Escribe 'salir' para terminar)")
        
        while True:
            user_input = input("\nTú: ").strip()
            
            if user_input.lower() == 'salir':
                print("\nAsistente: ¡Hasta luego! Fue un placer ayudarte.")
                break
            
            try:
                response = self.process_query(user_input)
                print("\nAsistente:", response)
            except Exception as e:
                print(f"\nAsistente: Lo siento, ocurrió un error: {str(e)}")
                print("Por favor, intenta reformular tu consulta.")

# Ejemplo de uso
if __name__ == "__main__":
    chatbot = AmorisChatbot()
    chatbot.chat()