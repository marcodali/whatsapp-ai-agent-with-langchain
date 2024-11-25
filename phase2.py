from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from laTerceraEsLaVencida import RedisVectorSearch


class AmorisChatbot:
    def __init__(self, index_name="vector_store_idx:social_profiles"):
        self.vector_search = RedisVectorSearch(index_name)
        self.llm = ChatOpenAI(temperature=0.3, model_name="gpt-4o-mini")

        # Prompt para presentar matches potenciales con un balance entre profesionalismo y calidez
        self.response_prompt = PromptTemplate(
            input_variables=[
                "consulta_usuario",
                "resultados",
                "nombre_usuario",
                "nacionalidad_usuario",
            ],
            template="""Eres un asistente empático y profesional que ayuda a las personas a encontrar conexiones genuinas.
            
            Usuario: {nombre_usuario}
            País: {nacionalidad_usuario}
            Búsqueda: {consulta_usuario}
            
            Perfiles encontrados:
            {resultados}
            
            Instrucciones para presentar los perfiles:
            1. Saluda brevemente y de manera personal, usando el nombre del usuario
            2. Presenta cada perfil destacando con calidez:
               - Su nombre y ocupación
               - Aspectos interesantes de su perfil que coincidan con la búsqueda
               - Las redes sociales donde pueden conocerse mejor
            3. Si hay coincidencia de país, menciónalo como un punto positivo
            4. Mantén un tono genuino pero moderado
            5. Sé conciso pero cálido en las descripciones
            
            Recuerda: el objetivo es presentar cada perfil de manera auténtica, permitiendo que las conexiones surjan naturalmente.""",
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
        # Enriquecer la búsqueda para priorizar matches del mismo país sin ser restrictivo
        enhanced_query = (
            f"Persona de {nacionalidad_usuario} idealmente. {user_input}"
        )
        print(f"Enriqueciendo la búsqueda con: {enhanced_query}")

        # Realizar la búsqueda vectorial con la query enriquecida
        similar_profiles = self.vector_search.search_similar_profiles(
            enhanced_query, k=num_results
        )

        # Formatear los resultados con nuestro LLM para una respuesta balanceada
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

        print(
            f"\nHola {nombre_usuario}, me alegra ayudarte a encontrar una conexión especial."
        )

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
