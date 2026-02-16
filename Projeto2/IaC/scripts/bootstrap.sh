#!/bin/bash
set -e # Falha se qualquer erro ocorrer

echo ">>> INICIANDO BOOTSTRAP (SAFE VENV) <<<"

# 1. Cria o VENV usando o módulo nativo do Python 3
echo ">>> Criando Virtual Environment..."
cd /home/hadoop
python3 -m venv pyspark_venv

# 2. Instala libs DENTRO do venv
echo ">>> Instalando bibliotecas no VENV... <<<"
/home/hadoop/pyspark_venv/bin/pip install --upgrade pip
/home/hadoop/pyspark_venv/bin/pip install numpy scikit-learn pandas findspark boto3

# 3. Criação de Diretórios e Permissões
echo ">>> Configurando Diretórios... <<<"
mkdir -p /home/hadoop/pipeline
mkdir -p /home/hadoop/logs

# Garante que o usuário hadoop seja dono de tudo
chown -R hadoop:hadoop /home/hadoop/pyspark_venv
chown -R hadoop:hadoop /home/hadoop/pipeline
chown -R hadoop:hadoop /home/hadoop/logs

echo ">>> BOOTSTRAP CONCLUÍDO !!! <<<"