# Use uma imagem base oficial do Python mais recente (Python 3.11)
FROM python:3.11-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie o arquivo requirements.txt para o contêiner (caso você o tenha)
COPY requirements.txt .

# Instale as dependências Python necessárias
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante dos arquivos do projeto para o contêiner
COPY . .

# Exponha a porta (se necessário)
EXPOSE 8000

# Execute o bot ao iniciar o contêiner
CMD ["python", "bot.py"]
