# Use a imagem base do Ubuntu
FROM ubuntu:20.04

# Instale as dependências necessárias
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Copie o seu arquivo Python para o container
COPY app.py /app/

# Defina o diretório de trabalho como /app/
WORKDIR /app/

# Instale as dependências do seu aplicativo Python
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install -r /tmp/requirements.txt

# Exponha a porta 5000
EXPOSE 5000

# Defina o comando para executar a aplicação
CMD ["python3", "app.py"]