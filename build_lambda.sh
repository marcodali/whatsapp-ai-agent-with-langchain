#!/bin/bash
mkdir package/

# Copiar archivos de código
cp lambda.py package/
cp phase2.py package/
cp laTerceraEsLaVencida.py package/

# Crear ZIP
cd package/
zip -r9 ../package.zip .

# Limpiar
cd ..
rm -rf package/