#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de inicio para la aplicación Flask Pokédex
"""
import os
from app import app

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🔴 POKÉDEX UAX - Universidad Alfonso X El Sabio")
    print("="*50)
    print("\n✅ Servidor Flask iniciado")
    print("🌐 Accede a: http://localhost:5001")
    print("\n" + "="*50 + "\n")
    
    # Ejecutar sin debug para producción
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
