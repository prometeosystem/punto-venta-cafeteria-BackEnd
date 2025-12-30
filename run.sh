#!/bin/bash

# Script para iniciar el servidor de la API

# Activar el entorno virtual
source venv/bin/activate

# Iniciar el servidor con uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

