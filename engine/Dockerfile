FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04

# Impede prompts interativos do APT (como escolha de timezone do tzdata)
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instalar Python, Pip e FFmpeg no Ubuntu
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# No Ubuntu 22.04+, o pip usa o ambiente de sistema por padrão se passarmos essa flag
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages || pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Usamos python3 para invocar o uvicorn nativamente
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
