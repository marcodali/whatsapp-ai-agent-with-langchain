from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from laTerceraEsLaVencida import RedisVectorSearch

class AmorisChatbot:
    def __init__(self, index_name="vector_store_idx:social_profiles"):
        # Inicializar componentes base
        self.vector_search = RedisVectorSearch(index_name)
        self.llm = ChatOpenAI(temperature=0.4, model_name="gpt-4o-mini")
        
        # Prompt para entender la intención del usuario
        self.query_prompt = PromptTemplate(
            input_variables=["consulta_usuario", "nombre_usuario", "nacionalidad_usuario", "VIP_or_not", "boolean_permiso"],
            template="""Eres Cupido, un experto en conectar corazones a través de profesiones y culturas. 
            Tu misión es entender profundamente lo que busca esta persona y encontrar conexiones significativas.

            Consulta del usuario: {consulta_usuario}

            Instrucciones:
            1. Identifica la profesión y nacionalidad mencionadas o implícitas
            2. Considera variaciones culturales y términos profesionales similares
               (Ej: "doctor/médico", "USA/Estados Unidos")
            3. Mantén la esencia humana en la búsqueda
            4. Solo los perfiles VIP pueden buscar perfiles de otro país diferente al suyo,
                para este caso en particular nuestro usuario {nombre_usuario} es de tipo {VIP_or_not}
                por lo que {boolean_permiso} tiene el permiso. Su nacionalidad es {nacionalidad_usuario}.

            Reformula la consulta para encontrar personas afines, manteniendo un balance entre precisión y apertura.
            Responde solo con la consulta mejorada, sin explicaciones."""
        )
        
        # Prompt para presentar matches potenciales
        self.response_prompt = PromptTemplate(
            input_variables=["consulta_usuario", "resultados", "nombre_usuario", "nacionalidad_usuario"],
            template="""Eres un consejero romántico carismático y empático que cree en el poder de las conexiones auténticas.
            
            Buscando para: {nombre_usuario}
            Su interés: {consulta_usuario}
            País de Orígen: {nacionalidad_usuario}
            
            Perfiles encontrados:
            {resultados}
            
            Instrucciones para presentar los matches:
            1. Saluda calurosamente y muestra entusiasmo por las posibilidades
            2. Presenta cada perfil como una historia única, destacando:
               - Lo interesante de su profesión y posibles puntos en común
               - Las redes sociales como ventana a su mundo
            3. Si hay matches profesionales, menciona el potencial de entendimiento mutuo
            4. Si hay matches culturales, resalta la belleza de compartir o descubrir una cultura
            5. Si los resultados no son ideales, ofrece sugerencias constructivas para ampliar la búsqueda
            
            Mantén un tono optimista, respetuoso y genuino. Evita clichés y superficialidades.
            Recuerda: estamos conectando personas reales con sueños y aspiraciones."""
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
    
    def process_query(self, user_input: str, num_results: int = 2) -> str:
        """
        Procesa la consulta del usuario y retorna una respuesta formatada.
        
        Args:
            user_input (str): Consulta del usuario
            num_results (int): Número de resultados a buscar
            
        Returns:
            str: Respuesta formatada para el usuario
        """
        # Paso 1: Mejorar la consulta con el LLM
        VIP_or_not = "VIP"
        enhanced_query = self.query_chain.invoke({
            "consulta_usuario": user_input,
            "nombre_usuario": "Kike",
            "nacionalidad_usuario": "Colombia",
            "VIP_or_not": VIP_or_not,   # Básico
            "boolean_permiso": "SI" if VIP_or_not == "VIP" else "NO",
        }).content

        print(f"Consulta mejorada: {enhanced_query}")
        
        # Paso 2: Realizar la búsqueda vectorial
        similar_profiles = self.vector_search.search_similar_profiles(enhanced_query, k=num_results)
        
        # Paso 3: Formatear los resultados para una respuesta amigable
        formatted_response = self.response_chain.invoke({
            "nombre_usuario": "Kike",
            "nacionalidad_usuario": "Colombia",
            "consulta_usuario": user_input,
            "resultados": str(similar_profiles)
        })
        
        return formatted_response.content
    
    def chat(self):
        """
        Inicia una sesión de chat interactiva con el usuario.
        """
        while True:
            user_input = input("\nTe ayudo a buscar pareja, dime como la quieres: ").strip()
            try:
                print("\n", self.process_query(user_input)) # respuesta del chatbot
            except Exception as e:
                print(f"\nLo siento, ocurrió un error: {str(e)}")

if __name__ == "__main__":
    chatbot = AmorisChatbot()
    chatbot.chat()