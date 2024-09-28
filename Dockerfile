# Usar uma imagem base oficial do Python
FROM python:3.11-slim

# Definir o diretório de trabalho
WORKDIR /app

# Instalar dependências necessárias para o wkhtmltoimage funcionar
RUN apt-get update && apt-get install -y \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    libfreetype6 \
    libjpeg62-turbo \
    libpng-dev \
    libssl-dev \
    libx11-dev \
    libxrandr-dev \
    xfonts-75dpi \
    xfonts-base \
    wget

# Baixar e instalar o wkhtmltoimage
RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb && \
    dpkg -i wkhtmltox_0.12.6-1.bionic_amd64.deb && \
    apt-get install -f

# Copiar os arquivos do projeto para o diretório de trabalho
COPY . /app

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta que será usada pelo bot (opcional, caso precise fazer testes de saúde)
EXPOSE 8000

# Comando para rodar o bot
CMD ["python", "main.py"]
