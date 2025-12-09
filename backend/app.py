# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import re
from bson import ObjectId

# Cargar variables de entorno
load_dotenv()

# Configuración de Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave-secreta-pokemon-uax-2024')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Conexión a MongoDB Atlas
MONGO_URL = os.getenv('MONGO_URL', "mongodb+srv://hectorbujan_db_user:Hector2005@clustertestapwi.hplx5oy.mongodb.net/")
DB_NAME = os.getenv('DB_NAME', 'pokemon_db')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'pokemon')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
pokemon_collection = db[COLLECTION_NAME]
users_collection = db['users']

# Credenciales de administrador
ADMIN_EMAIL = 'hectorbujan@gmail.com'
ADMIN_PASSWORD = 'hector2005'

def is_admin():
    """Verificar si el usuario actual es admin"""
    return session.get('user') == ADMIN_EMAIL and session.get('is_admin') == True

# Crear índices para optimizar búsquedas
try:
    pokemon_collection.create_index('id', unique=True)
    pokemon_collection.create_index([('name.es', 'text'), ('name.en', 'text')])
    pokemon_collection.create_index('types')
    pokemon_collection.create_index('generation')
    pokemon_collection.create_index('habitat')
    pokemon_collection.create_index('is_legendary')
    pokemon_collection.create_index('is_mythical')
    users_collection.create_index('email', unique=True)
except Exception as e:
    print(f"Índices ya existen o error: {e}")

# ==================== RUTAS ====================

@app.route('/')
def index():
    """Página principal con formulario de búsqueda"""
    # Obtener valores únicos para filtros
    tipos = pokemon_collection.distinct('types')
    habitats = pokemon_collection.distinct('habitat')
    generaciones = pokemon_collection.distinct('generation')
    
    return render_template('index.html', 
                         tipos=sorted(tipos),
                         habitats=sorted([h for h in habitats if h]),
                         generaciones=sorted(generaciones),
                         user=session.get('user'),
                         is_admin=is_admin())

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    """Búsqueda con múltiples filtros"""
    query = {}
    
    # Obtener parámetros de búsqueda
    nombre = request.args.get('nombre', '').strip()
    tipo = request.args.get('tipo', '').strip()
    habitat = request.args.get('habitat', '').strip()
    generacion = request.args.get('generacion', '').strip()
    legendario = request.args.get('legendario', '').strip()
    mitico = request.args.get('mitico', '').strip()
    
    # Construir consulta con $and
    condiciones = []
    
    if nombre:
        # Búsqueda parcial con regex (case insensitive)
        condiciones.append({
            '$or': [
                {'name.es': {'$regex': nombre, '$options': 'i'}},
                {'name.en': {'$regex': nombre, '$options': 'i'}}
            ]
        })
    
    if tipo:
        condiciones.append({'types': tipo})
    
    if habitat:
        condiciones.append({'habitat': habitat})
    
    if generacion:
        condiciones.append({'generation': generacion})
    
    if legendario == 'true':
        condiciones.append({'is_legendary': True})
    elif legendario == 'false':
        condiciones.append({'is_legendary': False})
    
    if mitico == 'true':
        condiciones.append({'is_mythical': True})
    elif mitico == 'false':
        condiciones.append({'is_mythical': False})
    
    if condiciones:
        query = {'$and': condiciones}
    
    # Ejecutar consulta
    resultados = list(pokemon_collection.find(query).sort('id', 1).limit(100))
    
    return render_template('resultados.html', 
                         pokemons=resultados,
                         total=len(resultados),
                         user=session.get('user'),
                         is_admin=is_admin())

@app.route('/pokemon/<int:pokemon_id>')
def pokemon_detalle(pokemon_id):
    """Ficha detallada de un Pokémon"""
    pokemon = pokemon_collection.find_one({'id': pokemon_id})
    
    if not pokemon:
        return "Pokémon no encontrado", 404
    
    # Verificar si está en el equipo del usuario
    en_equipo = False
    if 'user' in session:
        user_data = users_collection.find_one({'email': session['user']})
        if user_data and 'team' in user_data:
            en_equipo = pokemon_id in user_data['team']
    
    return render_template('pokemon.html', 
                         pokemon=pokemon,
                         en_equipo=en_equipo,
                         user=session.get('user'),
                         is_admin=is_admin())

@app.route('/comparar')
def comparar():
    """Comparador de dos Pokémon"""
    # Obtener IDs de los Pokémon a comparar
    id1 = request.args.get('id1', type=int)
    id2 = request.args.get('id2', type=int)
    
    pokemon1 = None
    pokemon2 = None
    
    if id1:
        pokemon1 = pokemon_collection.find_one({'id': id1})
    if id2:
        pokemon2 = pokemon_collection.find_one({'id': id2})
    
    # Lista de Pokémon para selector
    todos_pokemon = list(pokemon_collection.find({}, {'id': 1, 'name': 1}).sort('id', 1))
    
    return render_template('comparar.html',
                         pokemon1=pokemon1,
                         pokemon2=pokemon2,
                         todos_pokemon=todos_pokemon,
                         user=session.get('user'),
                         is_admin=is_admin())

@app.route('/estadisticas')
def estadisticas():
    """Página de estadísticas con agregaciones"""
    
    # Obtener parámetros de filtro
    stat1 = request.args.get('stat1', 'attack')
    stat2 = request.args.get('stat2', 'speed')
    
    # Mapeo de nombres de stats
    stat_names = {
        'hp': 'HP',
        'attack': 'Ataque',
        'defense': 'Defensa',
        'special_attack': 'Ataque Especial',
        'special_defense': 'Defensa Especial',
        'speed': 'Velocidad'
    }
    
    # Agregación 1: Top 10 Pokémon con mayor stat seleccionada
    top_stat1 = list(pokemon_collection.aggregate([
        {'$sort': {f'stats.{stat1}': -1}},
        {'$limit': 10},
        {'$project': {
            'id': 1,
            'name': 1,
            'types': 1,
            'img': 1,
            'stat_value': f'$stats.{stat1}'
        }}
    ]))
    
    # Agregación 2: Top 10 con segunda stat
    top_stat2 = list(pokemon_collection.aggregate([
        {'$sort': {f'stats.{stat2}': -1}},
        {'$limit': 10},
        {'$project': {
            'id': 1,
            'name': 1,
            'types': 1,
            'img': 1,
            'stat_value': f'$stats.{stat2}'
        }}
    ]))
    
    # NUEVA AGREGACIÓN: Top 10 combinado (suma de ambas estadísticas)
    top_combinado = list(pokemon_collection.aggregate([
        {'$addFields': {
            'stat1_value': f'$stats.{stat1}',
            'stat2_value': f'$stats.{stat2}',
            'combined_score': {'$add': [f'$stats.{stat1}', f'$stats.{stat2}']}
        }},
        {'$sort': {'combined_score': -1}},
        {'$limit': 10},
        {'$project': {
            'id': 1,
            'name': 1,
            'types': 1,
            'img': 1,
            'stat1_value': 1,
            'stat2_value': 1,
            'combined_score': 1
        }}
    ]))
    
    # Agregación 2: Promedio de estadísticas por generación
    promedios_gen = list(pokemon_collection.aggregate([
        {'$group': {
            '_id': '$generation',
            'promedio_hp': {'$avg': '$stats.hp'},
            'promedio_attack': {'$avg': '$stats.attack'},
            'promedio_defense': {'$avg': '$stats.defense'},
            'promedio_speed': {'$avg': '$stats.speed'},
            'total_pokemon': {'$sum': 1}
        }},
        {'$sort': {'_id': 1}}
    ]))
    
    # Agregación 3: Distribución de Pokémon por tipo
    distribucion_tipos = list(pokemon_collection.aggregate([
        {'$unwind': '$types'},
        {'$group': {
            '_id': '$types',
            'cantidad': {'$sum': 1}
        }},
        {'$sort': {'cantidad': -1}}
    ]))
    
    # Agregación 4: Pokémon legendarios y míticos por generación
    legendarios_gen = list(pokemon_collection.aggregate([
        {'$match': {
            '$or': [{'is_legendary': True}, {'is_mythical': True}]
        }},
        {'$group': {
            '_id': '$generation',
            'legendarios': {'$sum': {'$cond': ['$is_legendary', 1, 0]}},
            'miticos': {'$sum': {'$cond': ['$is_mythical', 1, 0]}}
        }},
        {'$sort': {'_id': 1}}
    ]))
    
    return render_template('estadisticas.html',
                         top_stat1=top_stat1,
                         top_stat2=top_stat2,
                         top_combinado=top_combinado,
                         stat1=stat1,
                         stat2=stat2,
                         stat_names=stat_names,
                         promedios_gen=promedios_gen,
                         distribucion_tipos=distribucion_tipos,
                         legendarios_gen=legendarios_gen,
                         user=session.get('user'),
                         is_admin=is_admin())

@app.route('/equipo')
def equipo():
    """Ver equipo del usuario"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_data = users_collection.find_one({'email': session['user']})
    
    equipo_pokemon = []
    if user_data and 'team' in user_data:
        for pokemon_id in user_data['team']:
            pokemon = pokemon_collection.find_one({'id': pokemon_id})
            if pokemon:
                equipo_pokemon.append(pokemon)
    
    return render_template('equipo.html',
                         equipo=equipo_pokemon,
                         user=session.get('user'))

@app.route('/agregar_equipo/<int:pokemon_id>', methods=['POST'])
def agregar_equipo(pokemon_id):
    """Añadir Pokémon al equipo (máximo 6)"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_data = users_collection.find_one({'email': session['user']})
    equipo_actual = user_data.get('team', []) if user_data else []
    
    # Verificar que no esté ya en el equipo
    if pokemon_id in equipo_actual:
        return redirect(url_for('pokemon_detalle', pokemon_id=pokemon_id))
    
    # Verificar máximo 6 Pokémon
    if len(equipo_actual) >= 6:
        return "Tu equipo ya tiene 6 Pokémon. Elimina uno para añadir otro.", 400
    
    # Añadir al equipo
    equipo_actual.append(pokemon_id)
    users_collection.update_one(
        {'email': session['user']},
        {'$set': {'team': equipo_actual}}
    )
    
    return redirect(url_for('pokemon_detalle', pokemon_id=pokemon_id))

@app.route('/eliminar_equipo/<int:pokemon_id>', methods=['POST'])
def eliminar_equipo(pokemon_id):
    """Eliminar Pokémon del equipo"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    users_collection.update_one(
        {'email': session['user']},
        {'$pull': {'team': pokemon_id}}
    )
    
    return redirect(url_for('equipo'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de nuevos usuarios"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validaciones
        if not email or not password:
            return render_template('registro.html', error='Todos los campos son obligatorios')
        
        if password != confirm_password:
            return render_template('registro.html', error='Las contraseñas no coinciden')
        
        if len(password) < 6:
            return render_template('registro.html', error='La contraseña debe tener al menos 6 caracteres')
        
        # Verificar si el usuario ya existe
        if users_collection.find_one({'email': email}):
            return render_template('registro.html', error='El email ya está registrado')
        
        # Crear usuario
        users_collection.insert_one({
            'email': email,
            'password': generate_password_hash(password),
            'team': []
        })
        
        session['user'] = email
        return redirect(url_for('index'))
    
    return render_template('registro.html', user=session.get('user'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuarios"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Verificar si es el admin
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['user'] = email
            session['is_admin'] = True
            return redirect(url_for('index'))
        
        user = users_collection.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            session['user'] = email
            session['is_admin'] = False
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Email o contraseña incorrectos')
    
    return render_template('login.html', user=session.get('user'))

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.pop('user', None)
    session.pop('is_admin', None)
    return redirect(url_for('index'))

# ==================== RUTAS DE ADMIN ====================

@app.route('/admin/crear_pokemon', methods=['GET', 'POST'])
def crear_pokemon():
    """Crear un nuevo Pokémon (solo admin)"""
    if not is_admin():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Obtener el siguiente ID disponible
        max_pokemon = pokemon_collection.find_one(sort=[('id', -1)])
        next_id = (max_pokemon['id'] + 1) if max_pokemon else 1
        
        # Crear el documento del Pokémon
        nuevo_pokemon = {
            'id': next_id,
            'name': {
                'es': request.form.get('nombre_es', '').strip(),
                'en': request.form.get('nombre_en', '').strip()
            },
            'types': [t.strip().lower() for t in request.form.get('tipos', '').split(',') if t.strip()],
            'stats': {
                'hp': int(request.form.get('hp', 50)),
                'attack': int(request.form.get('attack', 50)),
                'defense': int(request.form.get('defense', 50)),
                'special_attack': int(request.form.get('special_attack', 50)),
                'special_defense': int(request.form.get('special_defense', 50)),
                'speed': int(request.form.get('speed', 50))
            },
            'height': int(request.form.get('height', 10)),
            'weight': int(request.form.get('weight', 100)),
            'generation': request.form.get('generation', 'generation-i'),
            'habitat': request.form.get('habitat', 'grassland'),
            'is_legendary': request.form.get('is_legendary') == 'true',
            'is_mythical': request.form.get('is_mythical') == 'true',
            'abilities': [a.strip() for a in request.form.get('abilities', '').split(',') if a.strip()],
            'capture_rate': int(request.form.get('capture_rate', 45)),
            'base_experience': int(request.form.get('base_experience', 64)),
            'flavor_text_es': request.form.get('descripcion', ''),
            'img': {
                'front_default': request.form.get('imagen_url', ''),
                'official_artwork': request.form.get('imagen_url', '')
            },
            'es_inventado': True  # Marcar como Pokémon inventado
        }
        
        pokemon_collection.insert_one(nuevo_pokemon)
        return redirect(url_for('pokemon_detalle', pokemon_id=next_id))
    
    # Obtener opciones para los selectores
    tipos = pokemon_collection.distinct('types')
    habitats = pokemon_collection.distinct('habitat')
    generaciones = pokemon_collection.distinct('generation')
    
    return render_template('admin_crear_pokemon.html',
                         tipos=sorted(tipos) if tipos else ['normal', 'fire', 'water', 'electric', 'grass', 'ice', 'fighting', 'poison', 'ground', 'flying', 'psychic', 'bug', 'rock', 'ghost', 'dragon', 'dark', 'steel', 'fairy'],
                         habitats=sorted([h for h in habitats if h]) if habitats else ['grassland', 'forest', 'cave', 'mountain', 'water', 'sea', 'urban', 'rare'],
                         generaciones=sorted(generaciones) if generaciones else ['generation-i', 'generation-ii', 'generation-iii', 'generation-iv', 'generation-v', 'generation-vi', 'generation-vii', 'generation-viii', 'generation-ix'],
                         user=session.get('user'),
                         is_admin=is_admin())

@app.route('/admin/eliminar_pokemon/<int:pokemon_id>', methods=['POST'])
def eliminar_pokemon(pokemon_id):
    """Eliminar un Pokémon (solo admin)"""
    if not is_admin():
        return jsonify({'error': 'No autorizado'}), 403
    
    result = pokemon_collection.delete_one({'id': pokemon_id})
    
    if result.deleted_count > 0:
        # También eliminar de todos los equipos de usuarios
        users_collection.update_many(
            {},
            {'$pull': {'team': pokemon_id}}
        )
        return redirect(url_for('buscar'))
    
    return "Pokémon no encontrado", 404

# ==================== API ENDPOINTS (OPCIONAL) ====================

@app.route('/api/pokemon/<int:pokemon_id>')
def api_pokemon(pokemon_id):
    """API: Obtener datos de un Pokémon"""
    pokemon = pokemon_collection.find_one({'id': pokemon_id}, {'_id': 0})
    if pokemon:
        return jsonify(pokemon)
    return jsonify({'error': 'Pokémon no encontrado'}), 404

@app.route('/api/buscar')
def api_buscar():
    """API: Buscar Pokémon"""
    nombre = request.args.get('nombre', '')
    resultados = list(pokemon_collection.find(
        {'$or': [
            {'name.es': {'$regex': nombre, '$options': 'i'}},
            {'name.en': {'$regex': nombre, '$options': 'i'}}
        ]},
        {'_id': 0, 'id': 1, 'name': 1, 'img': 1, 'types': 1}
    ).limit(10))
    return jsonify(resultados)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🔴 POKÉDEX UAX - Universidad Alfonso X El Sabio")
    print("="*50)
    print("\n✅ Servidor Flask iniciado")
    print("🌐 Accede a: http://localhost:5000")
    print("\n📊 Base de datos conectada:")
    print(f"   - MongoDB Atlas: {DB_NAME}")
    print(f"   - Colección: {COLLECTION_NAME}")
    print(f"   - Total Pokémon: {pokemon_collection.count_documents({})}")
    print("\n" + "="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
