#!/bin/bash
source venv/bin/activate

# 1. Capa para langchain-community
mkdir -p langchain/python
pip install langchain-community==0.3.2 -t langchain/python
cd langchain && zip -r ../langchain.zip . && cd ..
rm -rf langchain/

# 2. Capa para langchain-openai
mkdir -p openai/python
pip install langchain-openai==0.2.2 -t openai/python
cd openai && zip -r ../openai.zip . && cd ..
rm -rf openai/

# 3. Capa para redis
mkdir -p redis/python
pip install redis==5.1.1 -t redis/python
cd redis && zip -r ../redis.zip . && cd ..
rm -rf redis/
