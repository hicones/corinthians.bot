# Utilizando imagem oficial do Python
FROM python:3.9-slim

# Instalar dependências do wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libssl-dev \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /usr/src/app

# Copiar arquivos para o contêiner
COPY . .

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Executar o bot
CMD ["python", "main.py"]
