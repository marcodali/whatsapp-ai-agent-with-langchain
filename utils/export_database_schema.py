import redis
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Configuración de la conexión a Redis
r = redis.from_url(os.getenv('REDIS_URL'))

# Inicializamos un diccionario para almacenar los datos exportados
export_data = {}

# Recorremos solo las claves que coinciden con el patrón
pattern = "vector_store_idx:social_profiles:*"
for key in r.scan_iter(match=pattern):
    # Verificamos si es un hash
    if r.type(key) == b'hash':
        data = r.hgetall(key)
        
        # Convertimos los datos de bytes a string y omitimos el campo content_vector
        parsed_data = {k.decode('utf-8'): v.decode('utf-8') for k, v in data.items() if k.decode('utf-8') != 'content_vector'}
        
        # Guardamos el contenido en el diccionario con el nombre de la clave
        export_data[key.decode('utf-8')] = parsed_data

# Exportamos el diccionario a un archivo JSON con caracteres especiales preservados
with open('export_redis.json', 'w', encoding='utf-8') as f:
    json.dump(export_data, f, ensure_ascii=False, indent=4)

print("Exportación completada. Los datos están en 'export_redis.json' con caracteres especiales correctamente.")
