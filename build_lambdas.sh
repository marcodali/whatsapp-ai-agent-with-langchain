#!/bin/bash
mkdir package/

# Copiar archivos de código
cp lambda.py package/
cp phase2.py package/
cp laTerceraEsLaVencida.py package/

# Crear ZIP
cd package/
zip -r9 ../package.zip .
cd ..

# Compilar para Linux ARM64 (el entorno de ejecución de Lambda)
GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -tags lambda.norpc -o bootstrap main.go

# Crear el archivo zip incluyendo solo el bootstrap
zip receiver.zip bootstrap

# Limpiar el archivo bootstrap
rm -rf package/
rm bootstrap