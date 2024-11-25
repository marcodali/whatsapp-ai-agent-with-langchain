from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from laTerceraEsLaVencida import RedisVectorSearch


class AmorisChatbot:
    def __init__(self, index_name="vector_store_idx:social_profiles"):
        self.vector_search = RedisVectorSearch(index_name)
        self.llm = ChatOpenAI(temperature=0.2, model_name="gpt-4o-mini")

        # Prompt para presentar matches potenciales con un enfoque más natural y directo
        self.response_prompt = PromptTemplate(
            input_variables=[
                "consulta_usuario",
                "resultados",
                "nombre_usuario",
                "nacionalidad_usuario",
            ],
            template="""Actúa como un asistente amigable pero profesional que ayuda a las personas a encontrar su media naranja.
            
            Usuario: {nombre_usuario}
            País: {nacionalidad_usuario}
            Búsqueda: {consulta_usuario}
            
            Perfiles encontrados:
            {resultados}
            
            Instrucciones para presentar los perfiles:
            1. Usa un tono amigable pero profesional, evitando exageraciones o entusiasmo artificial
            2. Presenta cada perfil destacando:
               - Su ocupación y actividades principales
               - Las redes sociales disponibles para contacto
            3. Mantén las descripciones concisas y relevantes
            4. Evita hacer suposiciones sobre compatibilidad o dar consejos no solicitados
            5. No incluyas reflexiones finales ni sugerencias adicionales
            
            Enfócate en presentar la información de manera clara y directa, permitiendo que el usuario tome sus propias decisiones.""",
        )

        # Crear la cadena de procesamiento para la respuesta
        self.response_chain = RunnableSequence(self.response_prompt, self.llm)

    def process_query(
        self,
        user_input: str,
        nombre_usuario: str,
        nacionalidad_usuario: str,
        num_results: int = 2,
    ) -> str:
        """
        Procesa la consulta del usuario y retorna una respuesta formatada.

        Args:
            user_input (str): Consulta del usuario
            nombre_usuario (str): Nombre del usuario que realiza la búsqueda
            nacionalidad_usuario (str): País de origen del usuario
            num_results (int): Número de resultados a buscar

        Returns:
            str: Respuesta formatada para el usuario
        """
        # Realizar la búsqueda vectorial directamente con la consulta original
        similar_profiles = self.vector_search.search_similar_profiles(
            user_input, k=num_results
        )

        # Formatear los resultados con nuestro LLM para una respuesta amigable
        formatted_response = self.response_chain.invoke(
            {
                "nombre_usuario": nombre_usuario,
                "nacionalidad_usuario": nacionalidad_usuario,
                "consulta_usuario": user_input,
                "resultados": str(similar_profiles),
            }
        )

        return formatted_response.content

    def chat(self):
        """
        Inicia una sesión de chat interactiva con el usuario.
        """
        # Obtener información del usuario
        nombre_usuario = input("\nPor favor, ingresa tu nombre: ").strip()
        nacionalidad_usuario = input("¿De qué país eres?: ").strip()

        print(f"\nBienvenido/a {nombre_usuario}! ¿En qué puedo ayudarte hoy?")

        while True:
            user_input = input(
                "\nDescribe cómo te gustaría que fuera tu pareja ideal: "
            ).strip()

            try:
                print(
                    "\n",
                    self.process_query(
                        user_input, nombre_usuario, nacionalidad_usuario
                    ),
                )
            except Exception as e:
                print(f"\nLo siento, ocurrió un error: {str(e)}")


if __name__ == "__main__":
    chatbot = AmorisChatbot()
    chatbot.chat()
