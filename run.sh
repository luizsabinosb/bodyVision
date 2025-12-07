#!/bin/bash
# Script para executar o BodyVision

echo "🚀 Iniciando BodyVision..."

# Ativa o ambiente virtual
source venv/bin/activate

# Executa o programa
python BodyVision.py

# Desativa o ambiente virtual ao sair
deactivate

