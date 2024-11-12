from langchain_community.vectorstores.redis import Redis
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from redis import Redis as RedisClient
import os

class RedisVectorSearch:
    def __init__(self, index_name="vector_store_idx:social_profiles"):
        # Si estamos en desarrollo, carga .env
        if os.getenv('ENV') != 'production':
            from dotenv import load_dotenv
            load_dotenv()
        
        self.redis_client = RedisClient(
            host=os.getenv('REDIS_HOST'),
            port=int(os.getenv('REDIS_PORT')),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True,
        )
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",  # buen balance costo/rendimiento
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self.index_name = index_name
        self.networks = ["instagram", "facebook", "threads", "tiktok"]
        self.vector_schema = {
            "algorithm": "HNSW",
            "distance_metric": "COSINE",
            "dims": 1536,   # Dimensión del modelo text-embedding-3-small
            "m": 16,
            "ef_construction": 200,
            "ef_runtime": 10,
        }
        
    def _get_all_social_ids(self):
        """
        Obtiene todos los IDs únicos de las emily's a través de todas las redes sociales.
        """
        all_ids = set()
        
        for network in self.networks:
            ids_key = f"{network}:emily_ids"
            if self.redis_client.exists(ids_key):
                network_ids = self.redis_client.smembers(ids_key)
                all_ids.update(network_ids)
                
        return all_ids
        
    def _get_profile_text(self, hash_key):
        """
        Construye un texto estructurado del perfil para los embeddings.
        """
        profile = self.redis_client.hgetall(hash_key)
        if not profile:
            return None
        
        # Construye un texto que facilite búsquedas específicas
        return (f"Red social: {hash_key.split(':')[0]} | "
                f"Username: {profile.get('username', '')} | "
                f"Ocupación: {profile.get('ocupacion', '')} | "
                f"País: {profile.get('nacionalidad', '')}")

    def create_index(self, force=False):
        """
        Crea el índice de vectores en Redis.
        
        Args:
            force (bool): Si True, elimina el índice existente antes de crear uno nuevo
        """
        # Verificar si el índice ya existe
        if self.redis_client.exists(self.index_name) and not force:
            print(f"El índice {self.index_name} ya existe. Use force=True para recrearlo.")
            return None
            
        # Si force=True o el índice no existe, procedemos
        if force:
            self.redis_client.delete(self.index_name)
            # También buscamos y eliminamos todas las claves relacionadas
            for key in self.redis_client.scan_iter(f"{self.index_name}:*"):
                self.redis_client.delete(key)
        
        # Obtener todos los IDs únicos de todas las redes sociales
        all_ids = self._get_all_social_ids()
        documents = []
        
        for emily_id in all_ids:
            # Recopilar información de todas las redes sociales para este ID
            profile_texts = []
            
            for network in self.networks:
                hash_key = f"{network}:{emily_id}"
                profile_text = self._get_profile_text(hash_key)
                if profile_text:
                    profile_texts.append(profile_text)
            
            if profile_texts:
                # Crear documento con todos los perfiles de redes sociales de nuestra emily
                metadata = {
                    "emily_id": emily_id,
                    "text_type": "profile"
                }
                
                documents.append(Document(
                    page_content=" || ".join(profile_texts),
                    metadata=metadata
                ))
        
        # Crear el índice en Redis
        vector_store = Redis.from_documents(
            documents=documents,
            embedding=self.embeddings,
            redis_url=f"redis://:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}",
            index_name=self.index_name,
            key_prefix=self.index_name,
            vector_schema=self.vector_schema,
        )
        
        return vector_store
    
    def search_similar_profiles(self, query: str, k: int = 2):
        """
        Busca perfiles similares basados en una consulta.
        
        Args:
            query (str): Consulta de búsqueda (ej: "abogadas de USA con instagram")
            k (int): Número de resultados a retornar
        """
        vector_store = Redis.from_existing_index(
            self.embeddings,
            redis_url=f"redis://:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}",
            index_name=self.index_name,
            key_prefix=self.index_name,
            schema=self.vector_schema,
        )
        
        results = vector_store.similarity_search_with_score(query, k=k)
        
        # Formatear resultados
        formatted_results = []
        for doc, score in results:
            # make another query to get the emily_id
            emily_id = self.redis_client.hget(doc.metadata["id"], "emily_id")
            result = {
                "emily_id": emily_id,
                "profiles": doc.page_content,
                "similarity_score": float(score)
            }
            formatted_results.append(result)
            
        return formatted_results

if __name__ == "__main__":
    # Inicializar el sistema de búsqueda
    search_system = RedisVectorSearch()
    
    # Crear el índice (forzar recreación)
    #vector_store = search_system.create_index(force=True)
    
    # Búsquedas de ejemplo
    queries = [
        "dame el username de 2 abogadas de USA que tengan instagram",
        "dame el tiktok de 1 enfermera de mexico",
        "presentame a 3 psicologas de colombia"
    ]
    
    for query in queries:
        print(f"\nBúsqueda: {query}")
        results = search_system.search_similar_profiles(query)
        for i, result in enumerate(results, 1):
            print(f"\nResultado {i}:")
            print(f"ID: {result['emily_id']}")
            print(f"Score: {result['similarity_score']:.4f}")
            print(f"Perfiles: {result['profiles']}")