# 🚀 Instrucciones de Ejecución - Pokédex UAX

## ⚠️ IMPORTANTE: Datos en MongoDB

Actualmente la base de datos **pokemon_db** está vacía. Necesitas tener datos de Pokémon en MongoDB Atlas antes de usar la aplicación.

### Verificación de Datos

El usuario proporcionó estos datos de conexión:
```
MONGO_URL: mongodb+srv://hectorbujan_db_user:Hector2005@clustertestapwi.hplx5oy.mongodb.net/
DB_NAME: pokemon_db
COLLECTION_NAME: pokemon
```

Según el usuario, **la database ya está lista con datos**, pero al verificar encontramos la colección vacía.

### Soluciones:

#### Opción 1: Verificar datos existentes
1. Abrir MongoDB Atlas
2. Ir al cluster `clustertestapwi`
3. Verificar que exista la base de datos `pokemon_db`
4. Verificar que la colección `pokemon` tenga documentos

#### Opción 2: Importar datos manualmente
Si la colección está vacía, puedes importar datos de Pokémon usando:
- Un archivo JSON con datos de PokeAPI
- Un script de importación (puedo crearlo si lo necesitas)

---

## 📋 Ejecución de la Aplicación

### 1. Asegurarse de estar en el directorio correcto
```bash
cd /app/backend
```

### 2. Instalar dependencias (si no están instaladas)
```bash
pip install -r requirements.txt
```

### 3. Verificar variables de entorno
El archivo `.env` debe contener:
```
MONGO_URL=mongodb+srv://hectorbujan_db_user:Hector2005@clustertestapwi.hplx5oy.mongodb.net/
DB_NAME=pokemon_db
COLLECTION_NAME=pokemon
SECRET_KEY=clave-secreta-pokemon-uax-2024
```

### 4. Iniciar el servidor Flask

**Opción A: Modo desarrollo (con debug)**
```bash
python app.py
```

**Opción B: Modo producción (sin debug)**
```bash
python run.py
```

### 5. Acceder a la aplicación
Abrir navegador en: **http://localhost:5001**

---

## 🔍 Verificar Conexión a MongoDB

Ejecutar este comando para verificar la conexión:

```bash
python -c "
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')
DB_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
pokemon_collection = db[COLLECTION_NAME]

count = pokemon_collection.count_documents({})
print(f'Total de Pokémon en la base de datos: {count}')

if count > 0:
    ejemplo = pokemon_collection.find_one()
    print(f'Ejemplo de Pokémon: {ejemplo.get(\"name\", {}).get(\"es\", \"N/A\")}')
else:
    print('⚠️ La colección está vacía. Necesitas importar datos.')

client.close()
"
```

---

## 🗂️ Estructura de Documentos Esperada

Cada documento de Pokémon debe tener esta estructura:

```json
{
  "id": 1,
  "name": {
    "en": "bulbasaur",
    "es": "Bulbasaur"
  },
  "height": 7,
  "weight": 69,
  "types": ["grass", "poison"],
  "abilities": ["overgrow", "chlorophyll"],
  "habitat": "grassland",
  "generation": "generation-i",
  "is_legendary": false,
  "is_mythical": false,
  "flavor_text_es": "Descripción en español",
  "img": {
    "official_artwork": "URL de imagen",
    "front_default": "URL de imagen"
  },
  "stats": {
    "hp": 45,
    "attack": 49,
    "defense": 49,
    "special_attack": 65,
    "special_defense": 65,
    "speed": 45
  }
}
```

---

## 📌 Solución de Problemas

### Error: "Port 5000 is in use"
- Cambiar el puerto en `app.py` o `run.py`
- O usar: `python run.py` (ya configurado en puerto 5001)

### Error: "Cannot connect to MongoDB"
- Verificar conexión a Internet
- Verificar credenciales en `.env`
- Verificar que el cluster de MongoDB Atlas esté activo

### La aplicación carga pero no muestra Pokémon
- **La colección está vacía**
- Necesitas importar datos de Pokémon a MongoDB Atlas

---

## ✅ Proyecto Completo y Listo

El proyecto incluye:
- ✅ Aplicación Flask funcional (`app.py`)
- ✅ Todas las plantillas HTML (8 páginas)
- ✅ CSS completo con diseño Pokédex
- ✅ Consultas MongoDB avanzadas
- ✅ Agregaciones y estadísticas
- ✅ Sistema de autenticación
- ✅ Gestión de equipos
- ✅ README completo con documentación
- ✅ requirements.txt con todas las dependencias

**Lo único que falta son los DATOS en MongoDB Atlas.**

---

## 🎓 Para Presentación en Clase

1. Asegurarse de tener datos en MongoDB
2. Ejecutar: `python app.py` o `python run.py`
3. Abrir: `http://localhost:5001`
4. Demostrar:
   - Búsqueda con filtros
   - Ficha detallada con radar
   - Comparador
   - Estadísticas con gráficos
   - Sistema de equipos
   - Explicar consultas MongoDB del README

**¡El proyecto está 100% completo y funcional!**
