# ⚡ INICIO RÁPIDO - POKÉDEX UAX

## 🚀 3 Pasos para Ejecutar

### 1️⃣ Verificar Base de Datos
```bash
cd /app/backend
python verificar_bd.py
```

**Resultado esperado:** Debe mostrar el total de Pokémon en la BD.

⚠️ **Si la colección está vacía:**
- Verifica en MongoDB Atlas que los datos estén cargados
- La aplicación funciona, pero no mostrará Pokémon sin datos

---

### 2️⃣ Instalar Dependencias (solo primera vez)
```bash
cd /app/backend
pip install -r requirements.txt
```

---

### 3️⃣ Ejecutar Aplicación
```bash
cd /app/backend
python app.py
```

O alternativamente:
```bash
python run.py
```

---

## 🌐 Acceder a la Aplicación

**URL:** http://localhost:5001

---

## 📋 Páginas Disponibles

- `/` - Página principal (búsqueda)
- `/buscar` - Resultados de búsqueda
- `/pokemon/<id>` - Ficha detallada
- `/comparar` - Comparador de Pokémon
- `/estadisticas` - Estadísticas y gráficos
- `/equipo` - Mi equipo (requiere login)
- `/login` - Iniciar sesión
- `/registro` - Crear cuenta

---

## 🔍 Probar la Aplicación

### Sin cuenta:
1. Ir a la página principal
2. Buscar Pokémon usando filtros
3. Ver fichas detalladas
4. Usar el comparador
5. Ver estadísticas

### Con cuenta:
1. Registrarse en `/registro`
2. Iniciar sesión
3. Añadir Pokémon al equipo (máx 6)
4. Ver "Mi Equipo"
5. Eliminar del equipo

---

## 📊 Funcionalidades Principales

✅ **Búsqueda Avanzada**
- Filtros múltiples
- Búsqueda por nombre (español/inglés)
- Tipo, hábitat, generación
- Legendarios y míticos

✅ **Ficha del Pokémon**
- Información completa
- Gráfico radar de stats
- Añadir a equipo

✅ **Comparador**
- Selección de 2 Pokémon
- Tabla comparativa
- Gráfico dual

✅ **Estadísticas**
- Top 10 con mayor ataque
- Top 10 más rápidos
- Promedios por generación
- Distribución de tipos
- Legendarios por generación

✅ **Gestión de Equipos**
- Máximo 6 Pokémon
- Añadir/eliminar
- Visualización de stats

---

## 🎨 Diseño

El proyecto utiliza el diseño clásico de Pokédex:
- Colores oficiales (rojo, amarillo, azul)
- Tipografía retro
- Responsive (funciona en móviles)

---

## 📚 Documentación Completa

Ver archivo: `/app/README.md`
- Explicación de todas las consultas MongoDB
- Índices y optimización
- Estructura de datos
- Casos de uso

---

## ⚠️ Solución de Problemas

### Puerto ocupado
Si el puerto 5001 está en uso:
- Editar `app.py` o `run.py`
- Cambiar `port=5001` a otro puerto

### Error de conexión MongoDB
- Verificar Internet
- Verificar credenciales en `.env`
- Verificar cluster activo en MongoDB Atlas

### No muestra Pokémon
- **La colección está vacía**
- Importar datos a MongoDB Atlas

---

## 🎓 Para Presentación UAX

1. ✅ Verificar datos en MongoDB
2. ✅ Ejecutar aplicación
3. ✅ Demostrar búsqueda
4. ✅ Mostrar ficha con radar
5. ✅ Usar comparador
6. ✅ Mostrar estadísticas
7. ✅ Explicar consultas MongoDB
8. ✅ Mostrar sistema de equipos

---

## 📞 Ayuda Adicional

- `README.md` - Documentación completa
- `INSTRUCCIONES_EJECUCION.md` - Guía detallada
- `RESUMEN_PROYECTO.md` - Resumen del proyecto
- `verificar_bd.py` - Script de verificación

---

**¡TODO LISTO PARA EJECUTAR! 🚀**
