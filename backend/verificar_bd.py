#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificación de base de datos
Pokédex UAX - Universidad Alfonso X El Sabio
"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

MONGO_URL = os.getenv('MONGO_URL')
DB_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

print("\n" + "="*60)
print("🔍 VERIFICACIÓN DE BASE DE DATOS - POKÉDEX UAX")
print("="*60 + "\n")

try:
    # Conectar a MongoDB
    print("📡 Conectando a MongoDB Atlas...")
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    pokemon_collection = db[COLLECTION_NAME]
    
    print("✅ Conexión exitosa\n")
    
    # Verificar datos
    print(f"📊 Base de datos: {DB_NAME}")
    print(f"📦 Colección: {COLLECTION_NAME}")
    
    # Contar documentos
    count = pokemon_collection.count_documents({})
    print(f"🔢 Total de Pokémon: {count}\n")
    
    if count > 0:
        print("✅ ¡La base de datos tiene datos!\n")
        
        # Mostrar ejemplo
        ejemplo = pokemon_collection.find_one()
        print("📝 Ejemplo de documento:")
        print(f"   ID: {ejemplo.get('id')}")
        print(f"   Nombre ES: {ejemplo.get('name', {}).get('es')}")
        print(f"   Nombre EN: {ejemplo.get('name', {}).get('en')}")
        print(f"   Tipos: {', '.join(ejemplo.get('types', []))}")
        print(f"   Generación: {ejemplo.get('generation')}")
        
        # Estadísticas de la base de datos
        print("\n📈 Estadísticas:")
        tipos_unicos = pokemon_collection.distinct('types')
        generaciones = pokemon_collection.distinct('generation')
        legendarios = pokemon_collection.count_documents({'is_legendary': True})
        miticos = pokemon_collection.count_documents({'is_mythical': True})
        
        print(f"   - Tipos únicos: {len(tipos_unicos)}")
        print(f"   - Generaciones: {len(generaciones)}")
        print(f"   - Legendarios: {legendarios}")
        print(f"   - Míticos: {miticos}")
        
        print("\n" + "="*60)
        print("✅ TODO LISTO - Puedes ejecutar la aplicación")
        print("="*60)
        print("\n💡 Ejecuta: python app.py")
        print("🌐 Luego abre: http://localhost:5001\n")
        
    else:
        print("⚠️  LA COLECCIÓN ESTÁ VACÍA\n")
        print("❌ La base de datos no tiene documentos de Pokémon")
        print("\n📋 Opciones:")
        print("   1. Verificar en MongoDB Atlas que la colección tenga datos")
        print("   2. Importar datos desde un archivo JSON")
        print("   3. Ejecutar un script de importación desde PokeAPI")
        print("\n💡 Estructura esperada del documento:")
        print("""
        {
          "id": 1,
          "name": {"en": "bulbasaur", "es": "Bulbasaur"},
          "types": ["grass", "poison"],
          "stats": {"hp": 45, "attack": 49, ...},
          ...
        }
        """)
    
    client.close()
    
except Exception as e:
    print(f"\n❌ ERROR DE CONEXIÓN:")
    print(f"   {str(e)}\n")
    print("🔧 Verifica:")
    print("   1. Conexión a Internet")
    print("   2. Credenciales en archivo .env")
    print("   3. Cluster de MongoDB Atlas activo")

print("\n" + "="*60 + "\n")
