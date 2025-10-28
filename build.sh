#!/bin/bash
# Script de build para Render.com
# Instala dependencias y crea tablas de base de datos

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "📊 Inicializando base de datos..."
python init_render.py

echo "✅ Build completado exitosamente"
