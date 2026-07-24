from faster_whisper import WhisperModel

# Inicializamos o modelo globalmente para não recarregar em toda requisição
# Dependendo da sua máquina, se tiver GPU NVIDIA, altere device para "cuda" e compute_type para "float16"
model = WhisperModel("base", device="cpu", compute_type="int8")

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
