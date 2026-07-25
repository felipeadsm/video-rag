FROM python:3.13-slim

WORKDIR /app

# Instalar FFmpeg (essencial para yt-dlp extrair áudio e whisper processar)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Exporta o caminho das bibliotecas CUDA instaladas pelo pip (cuBLAS e cuDNN) para o faster-whisper enxergar a placa de vídeo
ENV LD_LIBRARY_PATH="/usr/local/lib/python3.13/site-packages/nvidia/cublas/lib:/usr/local/lib/python3.13/site-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
