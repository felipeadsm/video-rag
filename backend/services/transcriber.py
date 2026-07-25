from faster_whisper import WhisperModel

# Inicializamos o modelo globalmente para não recarregar em toda requisição
# GPU NVIDIA detectada, ativando suporte a CUDA e float16 para máximo desempenho
model = WhisperModel("base", device="cuda", compute_type="float16")

def transcribe_audio(audio_path: str):
    """
    Transcreve o arquivo de áudio utilizando faster-whisper.
    Retorna uma lista de dicionários contendo os campos start, end e text.
    """
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    result = []
    for segment in segments:
        result.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })
        
    return result
