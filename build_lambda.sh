#!/bin/bash

# Crear y activar entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear directorio temporal para el paquete
mkdir -p lambda_package

# Copiar archivos de código
cp lambda.py lambda_package/
cp phase2.py lambda_package/
cp laTerceraEsLaVencida.py lambda_package/

# Copiar dependencias instaladas
cp -r venv/lib/python3.11/site-packages/* lambda_package/

# Crear ZIP
cd lambda_package
zip -r ../lambda_package.zip .

# Limpiar
cd ..
rm -rf lambda_package
deactivate
rm -rf venv